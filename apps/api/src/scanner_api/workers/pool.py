"""ProcessPoolExecutor lifecycle + asyncio.Queue dispatcher.

A startup do FastAPI cria o pool e a task que consome a queue. Shutdown
encerra graciosamente esperando jobs em andamento.

Por que ProcessPoolExecutor (não ThreadPool):
- Docling/EasyOCR/PyTorch carregam ~1.5GB de modelos. Em threads, isso
  competiria pelo GIL e não dá ganho de paralelismo real (CPU-bound).
- Subprocess isolado evita contaminação de estado entre jobs (ex: leak
  de modelo se Docling tem bug).
- Crash de um worker derruba só ele, não a API toda.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from concurrent.futures import Future, ProcessPoolExecutor
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select

from scanner_api.push import send_push
from scanner_api.workers.worker_main import WorkerJobSpec, process_job

log = logging.getLogger(__name__)


def _path_safe_dict(items: list[tuple[str, object]]) -> dict[str, object]:
    """dict_factory que converte Path → str para serialização inter-process.

    Inputs são WorkerJobSpec controlados por nós (não conteúdo externo);
    convertemos Path → str porque a serialização nativa do Python para
    múltiplos processos pode ter atritos com paths Windows com Unicode.
    Mais seguro normalizar para str de antemão.
    """
    out: dict[str, object] = {}
    for k, v in items:
        if isinstance(v, Path):
            out[k] = str(v)
        elif isinstance(v, list) and v and isinstance(v[0], Path):
            out[k] = [str(p) for p in v]
        elif isinstance(v, tuple):
            out[k] = list(v)
        else:
            out[k] = v
    return out


class WorkerPool:
    """Wrapper sobre ProcessPoolExecutor + asyncio.Queue.

    Padrão produtor-consumidor: rotas chamam `submit()` (não-bloqueante),
    o `_dispatch_loop` consome a queue e despacha para o executor.
    """

    def __init__(self, max_workers: int) -> None:
        self.max_workers = max_workers
        self._executor: ProcessPoolExecutor | None = None
        self._queue: asyncio.Queue[WorkerJobSpec] = asyncio.Queue()
        self._dispatcher_task: asyncio.Task[None] | None = None
        self._busy = 0
        self._loop: asyncio.AbstractEventLoop | None = None

    @property
    def queue_depth(self) -> int:
        """Número de jobs aguardando na fila (não inclui em execução)."""
        return self._queue.qsize()

    @property
    def workers_busy(self) -> int:
        """Número de workers atualmente processando jobs."""
        return self._busy

    async def start(self) -> None:
        """Cria executor + task que consome a queue."""
        self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
        self._loop = asyncio.get_running_loop()
        self._dispatcher_task = asyncio.create_task(self._dispatch_loop())
        log.info("WorkerPool started (max_workers=%d)", self.max_workers)

    async def shutdown(self) -> None:
        """Encerra dispatcher + executor (espera jobs em andamento)."""
        if self._dispatcher_task is not None:
            self._dispatcher_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._dispatcher_task
            self._dispatcher_task = None
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None
        log.info("WorkerPool shut down")

    async def submit(self, spec: WorkerJobSpec) -> None:
        """Adiciona um job à queue. Não bloqueia."""
        await self._queue.put(spec)

    async def _dispatch_loop(self) -> None:
        """Consome a queue e dispara process_job no executor."""
        loop = asyncio.get_running_loop()
        while True:
            spec = await self._queue.get()
            if self._executor is None:
                # Pool sendo encerrado — descarta o spec
                log.warning("Spec %s dropped: pool not active", spec.job_id)
                return
            self._busy += 1
            future: Future[dict] = loop.run_in_executor(
                self._executor,
                process_job,
                asdict(spec, dict_factory=_path_safe_dict),
            )
            future.add_done_callback(
                lambda f, s=spec: self._on_job_done(s, f)
            )

    def _on_job_done(self, spec: WorkerJobSpec, future: Future[dict]) -> None:
        """Callback invocado quando o subprocess termina.

        Agenda a finalização (DB update + push) no event loop, já que
        este callback pode rodar em thread auxiliar do executor.
        """
        self._busy = max(0, self._busy - 1)
        try:
            result = future.result()
        except Exception as exc:
            log.exception("Job %s crashed in subprocess: %s", spec.job_id, exc)
            result = {"status": "error", "error": str(exc), "output_files": []}

        log.info(
            "Job %s done: status=%s, files=%d",
            spec.job_id,
            result.get("status"),
            len(result.get("output_files", [])),
        )

        if self._loop is not None and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                _finalize_job(spec.job_id, result), self._loop
            )


async def _finalize_job(job_id: str, result: dict) -> None:
    """Atualiza o Job no DB, persiste arquivos de saída e dispara push.

    O `result` vem do `WorkerResult` do subprocess (asdict), com chaves:
    `status`, `page_count`, `error_msg`, `output_files` (lista de tuplas
    `(role, filename, size_bytes)`).
    """
    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import Job, JobFile, PushSubscription

    factory = async_session_factory()
    status = str(result.get("status", "error"))
    page_count = result.get("page_count")
    # WorkerResult.error_msg é a chave canônica; alguns paths legados podiam
    # mandar 'error' — aceitar ambos para robustez.
    error_msg = result.get("error_msg") or result.get("error")
    output_files = result.get("output_files") or []

    async with factory() as session:
        job = await session.get(Job, job_id)
        if job is None:
            log.warning("Job %s não encontrado no DB ao finalizar", job_id)
            return
        job.status = status
        job.finished_at = datetime.now(UTC).replace(tzinfo=None)
        if isinstance(page_count, int):
            job.page_count = page_count
        if error_msg:
            job.error_msg = str(error_msg)

        # Persiste outputs (md, docx, pdf, image) gerados pelo worker. Sem
        # estas linhas, GET /api/jobs/{id} mostra só os inputs e o frontend
        # nunca apresenta links de download mesmo com os arquivos no disco.
        for entry in output_files:
            try:
                role, filename, size_bytes = entry
            except (TypeError, ValueError):
                log.warning(
                    "Job %s: output_files entry malformed: %r", job_id, entry
                )
                continue
            session.add(
                JobFile(
                    job_id=job_id,
                    role=str(role),
                    filename=str(filename),
                    size_bytes=int(size_bytes) if size_bytes is not None else 0,
                )
            )

        title = job.title
        await session.commit()

        if status == "done":
            stmt = select(PushSubscription)
            subs = list((await session.execute(stmt)).scalars())
            await _broadcast_done(session, subs, job_id, title, page_count)


async def _broadcast_done(
    session, subs: list, job_id: str, title: str | None, page_count: int | None
) -> None:
    """Dispara push notification para todas as subscriptions ativas.

    Subscriptions expiradas (410/404) são removidas do DB.
    """
    from scanner_api.db.models import PushSubscription

    if not subs:
        return

    body_parts = []
    if page_count:
        body_parts.append(f"{page_count} página(s)")
    body = ", ".join(body_parts) if body_parts else "Concluído"
    payload = {
        "title": f"Job concluído: {title or job_id[:8]}",
        "body": body,
        "url": f"/jobs/{job_id}",
    }

    expired_endpoints = []
    for sub in subs:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            send_push,
            sub.endpoint,
            sub.p256dh,
            sub.auth,
            payload,
        )
        if result.expired:
            expired_endpoints.append(sub.endpoint)

    if expired_endpoints:
        from sqlalchemy import delete

        await session.execute(
            delete(PushSubscription).where(
                PushSubscription.endpoint.in_(expired_endpoints)
            )
        )
        await session.commit()
        log.info(
            "Removidas %d subscriptions expiradas", len(expired_endpoints)
        )


# Singleton — criado em main.py lifespan, acessado via get_pool()
_pool: WorkerPool | None = None


def get_pool() -> WorkerPool:
    """Acessa o pool global (deve ser inicializado no lifespan)."""
    if _pool is None:
        raise RuntimeError(
            "WorkerPool não inicializado — chame init_pool() no lifespan"
        )
    return _pool


async def init_pool(max_workers: int) -> WorkerPool:
    """Cria e inicializa o pool global."""
    global _pool
    if _pool is not None:
        log.warning("init_pool chamado com pool já existente — encerrando o anterior")
        await _pool.shutdown()
    _pool = WorkerPool(max_workers)
    await _pool.start()
    return _pool


async def shutdown_pool() -> None:
    """Encerra e remove o pool global."""
    global _pool
    if _pool is not None:
        await _pool.shutdown()
        _pool = None
