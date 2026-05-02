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
from pathlib import Path

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
        """Callback invocado quando o subprocess termina."""
        self._busy = max(0, self._busy - 1)
        try:
            result = future.result()
            log.info(
                "Job %s done: status=%s, files=%d",
                spec.job_id,
                result.get("status"),
                len(result.get("output_files", [])),
            )
            # NOTA: atualização do DB com result fica para Phase 1B Task 2
            # (POST handler vai expor uma callback que sincroniza com Job ORM)
        except Exception as exc:
            log.exception("Job %s crashed in subprocess: %s", spec.job_id, exc)


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
