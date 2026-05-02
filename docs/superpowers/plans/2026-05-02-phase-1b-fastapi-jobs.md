# Phase 1B — FastAPI Jobs API + Workers + WebSocket Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development ou inline. Steps usam checkbox (`- [ ]`).

**Goal:** Implementar processamento de jobs assíncronos: worker pool isolado (ProcessPoolExecutor), endpoints CRUD de `/api/jobs` (POST upload, GET list/detail), download de outputs, e WebSocket de progresso. Após Phase 1B, o backend é completo o suficiente para o frontend (Phase 2) consumir.

**Architecture:** `POST /api/jobs` salva inputs em disco + grava `Job` no SQLite + envia `job_id` para uma asyncio.Queue. ProcessPoolExecutor com 2 workers retira da fila; cada worker carrega Docling 1x e processa N jobs serialmente. Worker reporta progresso anexando linhas JSON em `<job>/.progress.jsonl`. FastAPI tail desse arquivo via aiofiles + asyncio.Event e faz broadcast WebSocket aos clientes inscritos no `job_id`.

**Tech Stack:** FastAPI 0.115, SQLAlchemy 2.0 async, ProcessPoolExecutor (concurrent.futures), aiofiles, python-multipart, websockets via FastAPI.

**Source spec:** `docs/superpowers/specs/2026-05-02-web-app-pwa-design.md` (Section 7.1 endpoints, 7.2 worker model).

**Working directory:** `c:\Users\jacks\OneDrive\2º Cérebro\Scanner de imagens`

**Pré-requisito:** Phase 1A completa (skeleton + settings + storage + DB + /api/health).

---

## File Structure

| Caminho | Ação | Responsabilidade |
|---------|------|------------------|
| `apps/api/src/scanner_api/workers/__init__.py` | CREATE | Re-export de pool + worker_main |
| `apps/api/src/scanner_api/workers/pool.py` | CREATE | Lifecycle do ProcessPoolExecutor + queue + dispatcher |
| `apps/api/src/scanner_api/workers/worker_main.py` | CREATE | Entry point do subprocess: load Docling 1x, processa job |
| `apps/api/src/scanner_api/progress.py` | CREATE | Pub/sub de eventos de progresso por job_id (asyncio) |
| `apps/api/src/scanner_api/schemas.py` | CREATE | Pydantic models para request/response (separado de db/models) |
| `apps/api/src/scanner_api/routes/jobs.py` | CREATE | POST/GET /api/jobs + GET /api/jobs/{id} |
| `apps/api/src/scanner_api/routes/files.py` | CREATE | GET /api/jobs/{id}/files/{filename} |
| `apps/api/src/scanner_api/routes/ws.py` | CREATE | WebSocket /ws/jobs/{id} |
| `apps/api/src/scanner_api/routes/__init__.py` | MODIFY | Adicionar jobs_router, files_router, ws_router |
| `apps/api/src/scanner_api/routes/health.py` | MODIFY | Conectar queue_depth/workers_busy ao pool real |
| `apps/api/src/scanner_api/main.py` | MODIFY | Lifespan inicia/termina o pool + monta routers |
| `apps/api/tests/test_progress.py` | CREATE | Pub/sub events |
| `apps/api/tests/test_workers.py` | CREATE | Pool lifecycle (sem rodar Docling de verdade) |
| `apps/api/tests/test_jobs_api.py` | CREATE | POST/GET endpoints (mock pool) |
| `apps/api/tests/test_files.py` | CREATE | Download seguro |
| `apps/api/tests/test_ws.py` | CREATE | WebSocket events |

---

## Task 1: Workers infrastructure (pool + worker_main + progress)

Bundle de 3 arquivos altamente acoplados. Implementação coordenada para evitar quebrar interfaces.

**Files:**
- Create: `workers/__init__.py`, `workers/pool.py`, `workers/worker_main.py`
- Create: `progress.py`
- Create: `tests/test_progress.py`, `tests/test_workers.py`
- Modify: `main.py` (lifespan), `routes/health.py` (expor métricas reais)

### Step 1.1: `progress.py` — pub/sub de eventos

```python
"""Pub/sub assíncrono de eventos de progresso de job.

Cada job_id tem um asyncio.Event compartilhado: workers (ou file tail)
fazem `set()`, consumidores WebSocket fazem `wait()`. Eventos são lidos
do disco (`<job>/.progress.jsonl`, append-only).
"""
from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from collections.abc import AsyncIterator
from pathlib import Path

import aiofiles


class ProgressBroker:
    """Distribui eventos do .progress.jsonl para clientes WebSocket."""

    def __init__(self) -> None:
        self._events: dict[str, asyncio.Event] = defaultdict(asyncio.Event)

    def signal(self, job_id: str) -> None:
        """Worker chama isso após escrever no .progress.jsonl."""
        evt = self._events.get(job_id)
        if evt is not None:
            evt.set()
            self._events[job_id] = asyncio.Event()  # rearm

    async def stream(
        self, job_id: str, progress_path: Path
    ) -> AsyncIterator[dict]:
        """Yields cada nova linha do .progress.jsonl como dict.

        Termina quando aparece um evento {type: 'done'|'error'|'cancelled'}.
        """
        # Espera arquivo existir
        while not progress_path.exists():
            await asyncio.sleep(0.1)

        async with aiofiles.open(progress_path) as f:
            while True:
                line = await f.readline()
                if line:
                    try:
                        event = json.loads(line.strip())
                    except json.JSONDecodeError:
                        continue
                    yield event
                    if event.get("type") in ("done", "error", "cancelled"):
                        return
                else:
                    # EOF — espera novo evento
                    await self._events[job_id].wait()


# Singleton
_broker = ProgressBroker()


def get_broker() -> ProgressBroker:
    return _broker
```

### Step 1.2: `workers/worker_main.py` — subprocess entry

```python
"""Entry point do worker subprocess.

Cada subprocess do ProcessPoolExecutor:
1. Importa Docling/scanner UMA VEZ (caro, ~5s)
2. Recebe job_id + paths de input/output
3. Roda scanner.scan_batch()
4. Apenda eventos no <job>/.progress.jsonl

Não conecta no DB diretamente — atualiza status via parent process após
retornar.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class WorkerJobSpec:
    """Tudo que o worker precisa para processar (sem ORM)."""
    job_id: str
    inputs: list[Path]
    output_dir: Path
    progress_path: Path
    formats: str       # 'md' | 'docx' | 'pdf' | 'all' | 'both'
    merge: bool
    do_ocr: bool
    device: str
    ocr_engine: str
    ocr_languages: tuple[str, ...]
    do_tables: bool


@dataclass
class WorkerResult:
    """Resumo do que aconteceu, lido pelo parent após o worker retornar."""
    job_id: str
    status: str  # 'done' | 'error'
    output_files: list[tuple[str, str, int]]  # (role, filename, size_bytes)
    page_count: int
    error_msg: str | None


def _emit(progress_path: Path, event: dict) -> None:
    """Append-only writer pra .progress.jsonl."""
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    with progress_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def process_job(spec_dict: dict) -> dict:
    """Entry point chamado via run_in_executor.

    Recebe e retorna dicts (serializáveis cross-process). spec_dict é o
    asdict() de WorkerJobSpec; retorna asdict() de WorkerResult.
    """
    spec = WorkerJobSpec(**{
        **spec_dict,
        "inputs": [Path(p) for p in spec_dict["inputs"]],
        "output_dir": Path(spec_dict["output_dir"]),
        "progress_path": Path(spec_dict["progress_path"]),
        "ocr_languages": tuple(spec_dict["ocr_languages"]),
    })

    _emit(spec.progress_path, {"type": "started", "ts": time.time(),
                                 "input_count": len(spec.inputs)})

    try:
        # Lazy imports (custosos)
        from scanner.pipeline import OutputFormat, scan_batch

        fmt_map = {
            "md": OutputFormat.MD, "docx": OutputFormat.DOCX,
            "pdf": OutputFormat.PDF, "all": OutputFormat.ALL,
            "both": OutputFormat.BOTH,
        }

        result = scan_batch(
            spec.inputs,
            spec.output_dir,
            formats=fmt_map[spec.formats],
            do_ocr=spec.do_ocr,
            device=spec.device,
            ocr_languages=spec.ocr_languages,
            ocr_engine=spec.ocr_engine,
            merge=spec.merge,
        )

        for i, sr in enumerate(result.successes, 1):
            _emit(spec.progress_path, {"type": "progress", "ts": time.time(),
                                         "current": i, "total": len(spec.inputs),
                                         "current_file": sr.source.name})

        # Coleta arquivos gerados em (role, filename, size)
        output_files: list[tuple[str, str, int]] = []
        for sr in result.successes:
            output_files.append(("output_md", sr.markdown_path.name,
                                 sr.markdown_path.stat().st_size))
            if sr.docx_path:
                output_files.append(("output_docx", sr.docx_path.name,
                                     sr.docx_path.stat().st_size))
            if sr.pdf_path:
                output_files.append(("output_pdf", sr.pdf_path.name,
                                     sr.pdf_path.stat().st_size))
            for img in sr.images:
                output_files.append(("image", img.name, img.stat().st_size))

        page_count = sum(sr.page_count for sr in result.successes)
        wr = WorkerResult(spec.job_id, "done", output_files, page_count, None)
        _emit(spec.progress_path, {"type": "done", "ts": time.time(),
                                     "page_count": page_count})

    except Exception as exc:  # noqa: BLE001 — sempre captura, propaga via WorkerResult
        wr = WorkerResult(spec.job_id, "error", [], 0, str(exc))
        _emit(spec.progress_path, {"type": "error", "ts": time.time(),
                                     "message": str(exc)})

    return asdict(wr)
```

### Step 1.3: `workers/pool.py` — pool lifecycle + dispatcher

```python
"""ProcessPoolExecutor lifecycle + asyncio.Queue dispatcher.

A startup do FastAPI cria o pool (+ task que consome a queue). Shutdown
encerra graciosamente.
"""
from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

from scanner_api.workers.worker_main import WorkerJobSpec, process_job

log = logging.getLogger(__name__)


class WorkerPool:
    """Wrapper sobre ProcessPoolExecutor + asyncio.Queue."""

    def __init__(self, max_workers: int) -> None:
        self.max_workers = max_workers
        self._executor: ProcessPoolExecutor | None = None
        self._queue: asyncio.Queue[WorkerJobSpec] = asyncio.Queue()
        self._dispatcher_task: asyncio.Task | None = None
        self._busy = 0

    @property
    def queue_depth(self) -> int:
        return self._queue.qsize()

    @property
    def workers_busy(self) -> int:
        return self._busy

    async def start(self) -> None:
        """Cria executor + task que consome a queue."""
        self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
        self._dispatcher_task = asyncio.create_task(self._dispatch_loop())
        log.info("WorkerPool started (max_workers=%d)", self.max_workers)

    async def shutdown(self) -> None:
        """Encerra dispatcher + executor (espera jobs em andamento)."""
        if self._dispatcher_task:
            self._dispatcher_task.cancel()
            try:
                await self._dispatcher_task
            except asyncio.CancelledError:
                pass
        if self._executor:
            self._executor.shutdown(wait=True)
        log.info("WorkerPool shut down")

    async def submit(self, spec: WorkerJobSpec) -> None:
        """Adiciona um job à queue. Não bloqueia."""
        await self._queue.put(spec)

    async def _dispatch_loop(self) -> None:
        """Consome a queue e dispara process_job no executor."""
        loop = asyncio.get_running_loop()
        on_done = self._on_job_done
        while True:
            spec = await self._queue.get()
            if self._executor is None:
                return
            self._busy += 1
            future = loop.run_in_executor(
                self._executor, process_job, asdict(spec, dict_factory=_path_safe_dict)
            )
            future.add_done_callback(lambda f, s=spec: on_done(s, f))

    def _on_job_done(self, spec: WorkerJobSpec, future) -> None:
        """Callback invocado quando o subprocess termina."""
        self._busy = max(0, self._busy - 1)
        try:
            result = future.result()
            log.info("Job %s done: %s", spec.job_id, result.get("status"))
        except Exception as exc:
            log.exception("Job %s crashed: %s", spec.job_id, exc)


def _path_safe_dict(items: list[tuple[str, object]]) -> dict:
    """dict_factory que converte Path → str para serialização inter-process."""
    out: dict[str, object] = {}
    for k, v in items:
        if isinstance(v, Path):
            out[k] = str(v)
        elif isinstance(v, list) and v and isinstance(v[0], Path):
            out[k] = [str(p) for p in v]
        else:
            out[k] = v
    return out


# Singleton
_pool: WorkerPool | None = None


def get_pool() -> WorkerPool:
    """Acessa o pool global (criado em lifespan)."""
    if _pool is None:
        raise RuntimeError("WorkerPool não inicializado — chame init_pool() em lifespan")
    return _pool


async def init_pool(max_workers: int) -> WorkerPool:
    global _pool
    _pool = WorkerPool(max_workers)
    await _pool.start()
    return _pool


async def shutdown_pool() -> None:
    global _pool
    if _pool:
        await _pool.shutdown()
        _pool = None
```

### Step 1.4: Integrar no lifespan e health

Modificar `main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from scanner_api.settings import get_settings
    from scanner_api.storage import ensure_data_dirs
    from scanner_api.workers.pool import init_pool, shutdown_pool

    settings = get_settings()
    ensure_data_dirs(settings.data_dir)
    await init_pool(settings.max_workers)
    log.info("scanner_api %s startup", __version__)
    yield
    await shutdown_pool()
    log.info("scanner_api %s shutdown", __version__)
```

Modificar `routes/health.py`:

```python
@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    device, gpu_name = _resolve_device()

    # Pool pode não estar inicializado em testes — usa try
    try:
        from scanner_api.workers.pool import get_pool
        pool = get_pool()
        queue_depth = pool.queue_depth
        workers_busy = pool.workers_busy
    except RuntimeError:
        queue_depth = 0
        workers_busy = 0

    return HealthResponse(
        device=device,
        gpu_name=gpu_name,
        queue_depth=queue_depth,
        workers_busy=workers_busy,
        ...
    )
```

### Step 1.5: Tests

`tests/test_progress.py`: testar pub/sub + stream com .jsonl real (sem Docling).

```python
import asyncio
import json
import pytest
from pathlib import Path
from scanner_api.progress import ProgressBroker


async def test_progress_stream_yields_events_until_done(tmp_path: Path) -> None:
    progress_path = tmp_path / "progress.jsonl"
    broker = ProgressBroker()

    # Escreve 3 eventos
    progress_path.write_text(
        json.dumps({"type": "started"}) + "\n"
        + json.dumps({"type": "progress", "current": 1, "total": 2}) + "\n"
        + json.dumps({"type": "done"}) + "\n"
    )

    events = []
    async for evt in broker.stream("job-x", progress_path):
        events.append(evt)
    assert [e["type"] for e in events] == ["started", "progress", "done"]
```

`tests/test_workers.py`: testar pool start/stop sem submeter jobs reais.

```python
import pytest
from scanner_api.workers.pool import WorkerPool


async def test_pool_start_shutdown() -> None:
    pool = WorkerPool(max_workers=1)
    await pool.start()
    assert pool.queue_depth == 0
    assert pool.workers_busy == 0
    await pool.shutdown()
```

### Step 1.6: Run tests + commit

```bash
cd apps/api && pytest tests/test_progress.py tests/test_workers.py tests/test_health.py -v
```

Expected: pool/progress tests passam, health.py continua passando com fallback de pool não-inicializado.

```bash
git add apps/api/
git commit -m "feat(api): add ProcessPool worker + progress pub/sub + lifespan integration

- workers/pool.py: WorkerPool wrapper sobre ProcessPoolExecutor + asyncio.Queue
- workers/worker_main.py: subprocess entry, carrega Docling 1x, scan_batch
- progress.py: ProgressBroker — pub/sub via asyncio.Event + .progress.jsonl tail
- main.py: lifespan inicia/termina pool, ensure_data_dirs no startup
- routes/health.py: queue_depth/workers_busy do pool real (fallback 0 se off)
- Tests: progress stream, pool lifecycle (sem rodar Docling de verdade)

Plan Phase 1B Task 1/5"
```

---

## Task 2: POST /api/jobs (upload + queue)

**Files:**
- Create: `schemas.py` — Pydantic request/response models
- Create: `routes/jobs.py` (parcial: só POST)
- Modify: `routes/__init__.py` (re-export jobs_router)
- Modify: `main.py` (include jobs_router)
- Create: `tests/test_jobs_api.py` (POST tests)

### Step 2.1: `schemas.py`

```python
"""Pydantic schemas para request/response da API. Separado dos ORM
models para permitir validação independente do schema do DB."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class JobAdvancedOptions(BaseModel):
    """Sub-objeto de opções avançadas (corresponde ao painel Advanced no frontend)."""
    do_ocr: bool = True
    do_tables: bool = True
    ocr_engine: str = Field(default="easyocr", pattern="^(easyocr|tesseract)$")
    ocr_lang: str = Field(default="pt,en")
    device: str = Field(default="auto", pattern="^(auto|cuda|cpu)$")


class JobCreatedResponse(BaseModel):
    job_id: str
    status: str  # 'queued'


class JobFileInfo(BaseModel):
    role: str
    filename: str
    size_bytes: int


class JobDetail(BaseModel):
    id: str
    status: str
    title: str | None
    input_count: int
    merge_mode: int
    formats: str
    created_at: datetime
    finished_at: datetime | None
    is_favorite: int
    error_msg: str | None
    page_count: int | None
    files: list[JobFileInfo]


class JobSummary(BaseModel):
    """Item de listagem (sem `files`)."""
    id: str
    status: str
    title: str | None
    input_count: int
    formats: str
    created_at: datetime
    is_favorite: int
```

### Step 2.2: `routes/jobs.py` (POST handler)

```python
"""POST/GET /api/jobs."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from scanner_api.db import get_session
from scanner_api.db.models import Job, JobFile
from scanner_api.schemas import JobAdvancedOptions, JobCreatedResponse
from scanner_api.settings import get_settings
from scanner_api.storage import (
    ensure_job_dirs,
    job_input_path,
    job_output_path,
    job_progress_path,
)
from scanner_api.workers.pool import get_pool
from scanner_api.workers.worker_main import WorkerJobSpec

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobCreatedResponse, status_code=201)
async def create_job(
    files: list[UploadFile] = File(...),
    formats: str = Form(default="md"),
    merge: bool = Form(default=False),
    title: str | None = Form(default=None),
    advanced: str | None = Form(default=None),  # JSON encoded JobAdvancedOptions
    session: AsyncSession = Depends(get_session),
) -> JobCreatedResponse:
    """Cria um job: salva inputs + grava DB + envia para worker pool."""
    settings = get_settings()

    if not files:
        raise HTTPException(400, "Nenhum arquivo enviado.")
    if formats not in ("md", "docx", "pdf", "all", "both"):
        raise HTTPException(400, f"Formato inválido: {formats}")

    advanced_obj = JobAdvancedOptions()
    if advanced:
        try:
            advanced_obj = JobAdvancedOptions.model_validate_json(advanced)
        except Exception as exc:
            raise HTTPException(400, f"Advanced inválido: {exc}") from exc

    job_id = str(uuid.uuid4())
    ensure_job_dirs(settings.data_dir, job_id)

    # Salva inputs em disco (streaming)
    input_paths: list[Path] = []
    for upload in files:
        if upload.filename is None:
            raise HTTPException(400, "Arquivo sem nome.")
        target = job_input_path(settings.data_dir, job_id, upload.filename)
        async with aiofiles.open(target, "wb") as f:
            while chunk := await upload.read(1024 * 1024):  # 1 MB chunks
                await f.write(chunk)
        input_paths.append(target)

    # Grava Job no DB
    job = Job(
        id=job_id,
        status="queued",
        title=title or input_paths[0].stem,
        input_count=len(files),
        merge_mode=1 if merge else 0,
        formats=formats,
        advanced=advanced_obj.model_dump_json(),
        expires_at=datetime.utcnow() + timedelta(hours=settings.purge_hours),
    )
    for p in input_paths:
        job.files.append(
            JobFile(role="input", filename=p.name, size_bytes=p.stat().st_size)
        )
    session.add(job)
    await session.commit()

    # Submete ao worker pool
    output_dir = settings.data_dir / "jobs" / job_id / "outputs"
    spec = WorkerJobSpec(
        job_id=job_id,
        inputs=input_paths,
        output_dir=output_dir,
        progress_path=job_progress_path(settings.data_dir, job_id),
        formats=formats,
        merge=merge,
        do_ocr=advanced_obj.do_ocr,
        device=advanced_obj.device,
        ocr_engine=advanced_obj.ocr_engine,
        ocr_languages=tuple(s.strip() for s in advanced_obj.ocr_lang.split(",")),
        do_tables=advanced_obj.do_tables,
    )
    await get_pool().submit(spec)

    return JobCreatedResponse(job_id=job_id, status="queued")
```

### Step 2.3: Tests

`tests/test_jobs_api.py`:

```python
import io
import pytest
from httpx import AsyncClient


async def test_create_job_returns_201_with_job_id(client: AsyncClient) -> None:
    files = {"files": ("test.jpg", b"fake-jpg-bytes", "image/jpeg")}
    response = await client.post("/api/jobs", files=files, data={"formats": "md"})
    assert response.status_code == 201
    body = response.json()
    assert "job_id" in body
    assert body["status"] == "queued"


async def test_create_job_rejects_invalid_format(client: AsyncClient) -> None:
    files = {"files": ("test.jpg", b"x", "image/jpeg")}
    response = await client.post("/api/jobs", files=files, data={"formats": "bogus"})
    assert response.status_code == 400


async def test_create_job_rejects_no_files(client: AsyncClient) -> None:
    response = await client.post("/api/jobs", data={"formats": "md"})
    assert response.status_code in (400, 422)
```

**Nota sobre testes:** o pool deve ser **mockado** nos tests (não rodar Docling). Adicionar fixture `mock_pool` no conftest que substitui `get_pool()` por um mock que aceita `submit()` mas não processa nada. Job permanece status `queued` no DB — suficiente para validar criação.

### Step 2.4: Commit

```bash
git add apps/api/
git commit -m "feat(api): POST /api/jobs — multipart upload + DB + queue submit

- schemas.py: Pydantic request/response (JobCreatedResponse, JobDetail, etc.)
- routes/jobs.py: POST handler salva inputs em /data/jobs/{id}/inputs/,
  grava Job + JobFile no DB, submete WorkerJobSpec ao pool
- main.py: include jobs_router
- 3 tests (mock pool): 201 created, formato inválido, sem arquivos

Plan Phase 1B Task 2/5"
```

---

## Task 3: GET /api/jobs (list + detail)

### Step 3.1: Adicionar handlers em `routes/jobs.py`

```python
from sqlalchemy import select

from scanner_api.schemas import JobDetail, JobFileInfo, JobSummary


@router.get("", response_model=list[JobSummary])
async def list_jobs(
    favorite: int | None = None,
    status: str | None = None,
    page: int = 1,
    session: AsyncSession = Depends(get_session),
) -> list[JobSummary]:
    """Lista jobs paginada. Filtros opcionais: favorite, status."""
    if page < 1:
        raise HTTPException(400, "page deve ser >= 1")
    page_size = 20
    stmt = select(Job).order_by(Job.created_at.desc())
    if favorite is not None:
        stmt = stmt.where(Job.is_favorite == favorite)
    if status:
        stmt = stmt.where(Job.status == status)
    stmt = stmt.limit(page_size).offset((page - 1) * page_size)
    result = await session.execute(stmt)
    return [JobSummary.model_validate(j, from_attributes=True) for j in result.scalars()]


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: str, session: AsyncSession = Depends(get_session)
) -> JobDetail:
    """Detalhe de um job + seus arquivos."""
    job = await session.get(Job, job_id)
    if job is None:
        raise HTTPException(404, f"Job não encontrado: {job_id}")
    files = [
        JobFileInfo(role=f.role, filename=f.filename, size_bytes=f.size_bytes)
        for f in job.files
    ]
    return JobDetail.model_validate({**job.__dict__, "files": files})
```

### Step 3.2: Tests

```python
async def test_list_jobs_empty_returns_empty(client: AsyncClient) -> None:
    response = await client.get("/api/jobs")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_job_404_for_nonexistent(client: AsyncClient) -> None:
    response = await client.get("/api/jobs/nonexistent")
    assert response.status_code == 404


async def test_list_jobs_after_create(client: AsyncClient) -> None:
    files = {"files": ("test.jpg", b"x", "image/jpeg")}
    create = await client.post("/api/jobs", files=files, data={"formats": "md"})
    job_id = create.json()["job_id"]

    listing = await client.get("/api/jobs")
    assert listing.status_code == 200
    body = listing.json()
    assert any(j["id"] == job_id for j in body)
```

### Step 3.3: Commit

```bash
git add apps/api/
git commit -m "feat(api): GET /api/jobs (list + detail) with filters and pagination

- list_jobs: page-size 20, filtros favorite/status, ORDER BY created_at DESC
- get_job: 404 se não existe; eager load files via relationship
- 3 tests cobrindo lista vazia, 404, e listagem após criação

Plan Phase 1B Task 3/5"
```

---

## Task 4: WebSocket /ws/jobs/{id}

### Step 4.1: `routes/ws.py`

```python
"""WebSocket /ws/jobs/{job_id} — streaming de eventos de progresso."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from scanner_api.progress import get_broker
from scanner_api.settings import get_settings
from scanner_api.storage import job_progress_path

router = APIRouter(prefix="/ws", tags=["ws"])


@router.websocket("/jobs/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str) -> None:
    """Stream eventos do .progress.jsonl como JSON ao cliente.

    O socket fecha quando aparece type='done' | 'error' | 'cancelled'.
    """
    await websocket.accept()
    settings = get_settings()
    progress_path = job_progress_path(settings.data_dir, job_id)
    broker = get_broker()

    try:
        async for event in broker.stream(job_id, progress_path):
            await websocket.send_json(event)
    except WebSocketDisconnect:
        return
    finally:
        await websocket.close()
```

### Step 4.2: Mount router + test

`routes/__init__.py` ganha export, `main.py` faz include.

`tests/test_ws.py`:

```python
import asyncio
import json
import pytest
from httpx import AsyncClient


async def test_ws_streams_events_from_progress_file(
    client: AsyncClient, tmp_data_dir
) -> None:
    """Escrevemos eventos no .progress.jsonl e validamos que chegam ao WS."""
    job_id = "test-ws-job"
    from scanner_api.storage import job_progress_path, ensure_job_dirs

    ensure_job_dirs(tmp_data_dir, job_id)
    progress_path = job_progress_path(tmp_data_dir, job_id)
    progress_path.write_text(
        json.dumps({"type": "started"}) + "\n"
        + json.dumps({"type": "progress", "current": 1, "total": 1}) + "\n"
        + json.dumps({"type": "done"}) + "\n"
    )

    with client.websocket_connect(f"/ws/jobs/{job_id}") as ws:
        evt1 = ws.receive_json()
        evt2 = ws.receive_json()
        evt3 = ws.receive_json()
        assert evt1["type"] == "started"
        assert evt2["type"] == "progress"
        assert evt3["type"] == "done"
```

(Note: TestClient sync; ajustar se usando httpx.AsyncClient — pode precisar de `from starlette.testclient import TestClient`.)

### Step 4.3: Commit

```bash
git add apps/api/
git commit -m "feat(api): WebSocket /ws/jobs/{id} streams progress events

- routes/ws.py: handler usa ProgressBroker.stream()
- Eventos vêm do .progress.jsonl (escrito pelo worker subprocess)
- Socket fecha em done/error/cancelled
- 1 test E2E injetando eventos manualmente no jsonl

Plan Phase 1B Task 4/5"
```

---

## Task 5: GET /api/jobs/{id}/files/{filename}

### Step 5.1: `routes/files.py`

```python
"""GET /api/jobs/{job_id}/files/{filename} — download seguro de outputs."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from scanner_api.db import get_session
from scanner_api.db.models import Job
from scanner_api.settings import get_settings
from scanner_api.storage import job_dir, job_output_path

router = APIRouter(prefix="/api/jobs", tags=["files"])


@router.get("/{job_id}/files/{filename}")
async def download_file(
    job_id: str, filename: str, session: AsyncSession = Depends(get_session)
) -> FileResponse:
    """Retorna arquivo do job. Valida existência do job e do arquivo."""
    job = await session.get(Job, job_id)
    if job is None:
        raise HTTPException(404, f"Job não encontrado: {job_id}")

    settings = get_settings()
    base = job_dir(settings.data_dir, job_id)
    # Procura em outputs/ e images/ e inputs/
    for sub in ("outputs", "images", "inputs"):
        candidate = base / sub / filename
        if candidate.exists() and candidate.is_file():
            # Path traversal check: candidate deve estar dentro de base
            try:
                candidate.resolve().relative_to(base.resolve())
            except ValueError as exc:
                raise HTTPException(400, "Path inválido") from exc
            return FileResponse(
                candidate,
                filename=filename,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )

    raise HTTPException(404, f"Arquivo não encontrado: {filename}")
```

### Step 5.2: Tests + commit

```python
async def test_download_404_for_nonexistent_job(client: AsyncClient) -> None:
    response = await client.get("/api/jobs/none/files/x.md")
    assert response.status_code == 404


async def test_download_returns_file(client: AsyncClient, tmp_data_dir) -> None:
    """Cria job + arquivo manualmente e baixa."""
    # ... (setup job no DB + escrever output)
    # ... validar Content-Disposition + content
```

```bash
git commit -m "feat(api): GET /api/jobs/{id}/files/{filename} — download seguro

- Procura em outputs/, images/, inputs/
- Path traversal protection: filename normalizado + verifica resolve dentro de base
- Content-Disposition: attachment para forçar download no browser
- 2 tests: 404 job inexistente + download válido

Plan Phase 1B Task 5/5"
```

---

## Self-Review

**Coverage:**
- ✅ Worker pool (Section 7.2)
- ✅ POST /api/jobs (Section 7.1)
- ✅ GET list + detail (Section 7.1)
- ✅ WebSocket (Section 7.1)
- ✅ Download (Section 7.1)
- ⏭️ PATCH/DELETE → Phase 1C
- ⏭️ Push notifications → Phase 1C
- ⏭️ Purge cron → Phase 1C

**Risk areas:**
- ProcessPoolExecutor + import de Docling: deve testar com timeout generoso
- Path traversal em files.py: validado com `resolve().relative_to(base)`
- WebSocket race condition: cliente conecta antes do .progress.jsonl existir → broker espera com sleep loop
- Multipart upload grande: aiofiles streaming + python-multipart limita por config

---

## Execution Handoff

Plan complete. Next step:
- **Inline execution** (recomendado dada experiência): tasks 1-5 commitadas em sequência
- Após Phase 1B: backend está pronto para frontend (Phase 2) consumir
- Phase 1C (push + purge + PATCH/DELETE) pode ser pulada se você só usar single-tenant sem mobile push
