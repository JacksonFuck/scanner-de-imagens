"""POST/GET /api/jobs.

POST cria um job: salva inputs em disco, grava no DB, submete ao worker pool.
GET lista (paginado, com filtros) e GET /{id} retorna detalhe.
"""

from __future__ import annotations

import logging
import shutil
import uuid
from datetime import UTC, datetime, timedelta

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from scanner_api.db import get_session
from scanner_api.db.models import Job, JobFile
from scanner_api.schemas import (
    JobAdvancedOptions,
    JobCreatedResponse,
    JobDetail,
    JobFileInfo,
    JobSummary,
    JobUpdate,
)
from scanner_api.settings import get_settings
from scanner_api.storage import (
    ensure_data_dirs,
    ensure_job_dirs,
    job_dir,
    job_input_path,
    job_progress_path,
)
from scanner_api.workers.pool import get_pool
from scanner_api.workers.worker_main import WorkerJobSpec

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


_VALID_FORMATS = ("md", "docx", "pdf", "all", "both")


@router.post("", response_model=JobCreatedResponse, status_code=201)
async def create_job(
    files: list[UploadFile] = File(...),
    formats: str = Form(default="md"),
    merge: bool = Form(default=False),
    title: str | None = Form(default=None),
    advanced: str | None = Form(default=None),
    session: AsyncSession = Depends(get_session),
) -> JobCreatedResponse:
    """Cria um job e submete ao worker pool.

    Aceita 1+ arquivos via multipart. Salva em /data/jobs/{job_id}/inputs/.
    Persiste Job + JobFile no DB. Submete WorkerJobSpec ao pool — não
    aguarda processamento (job fica em status 'queued').

    Args:
        files: Arquivos enviados (multipart).
        formats: 'md' | 'docx' | 'pdf' | 'all' | 'both'.
        merge: Consolidar múltiplas imagens em um arquivo único.
        title: Título amigável (default: nome do 1º arquivo).
        advanced: JSON-encoded JobAdvancedOptions (opcional).

    Returns:
        JobCreatedResponse com job_id (UUID4) e status='queued'.

    Raises:
        HTTPException(400): Sem arquivos, formato inválido, ou advanced malformado.
    """
    settings = get_settings()
    ensure_data_dirs(settings.data_dir)

    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")
    if formats not in _VALID_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato inválido: {formats}. Aceitos: {list(_VALID_FORMATS)}",
        )

    # Parse advanced (JSON encoded ou None)
    advanced_obj = JobAdvancedOptions()
    if advanced:
        try:
            advanced_obj = JobAdvancedOptions.model_validate_json(advanced)
        except Exception as exc:
            raise HTTPException(
                status_code=400, detail=f"Advanced inválido: {exc}"
            ) from exc

    job_id = str(uuid.uuid4())
    ensure_job_dirs(settings.data_dir, job_id)

    # Salva inputs em disco (streaming para não estourar memória em uploads grandes)
    input_paths = []
    for upload in files:
        if not upload.filename:
            raise HTTPException(status_code=400, detail="Arquivo sem nome.")
        target = job_input_path(settings.data_dir, job_id, upload.filename)
        async with aiofiles.open(target, "wb") as f:
            while chunk := await upload.read(1024 * 1024):  # 1MB chunks
                await f.write(chunk)
        input_paths.append(target)

    # Grava Job + JobFile no DB
    job = Job(
        id=job_id,
        status="queued",
        title=title or input_paths[0].stem,
        input_count=len(files),
        merge_mode=1 if merge else 0,
        formats=formats,
        advanced=advanced_obj.model_dump_json(),
        expires_at=datetime.now(UTC) + timedelta(hours=settings.purge_hours),
    )
    for p in input_paths:
        job.files.append(
            JobFile(role="input", filename=p.name, size_bytes=p.stat().st_size)
        )
    session.add(job)
    await session.commit()

    # Submete ao worker pool (best-effort: testes podem ter pool não inicializado)
    output_dir = settings.data_dir / "jobs" / job_id / "outputs"
    spec = WorkerJobSpec(
        job_id=job_id,
        inputs=input_paths,
        output_dir=output_dir,
        progress_path=job_progress_path(settings.data_dir, job_id),
        formats=formats,
        merge=merge,
        do_ocr=advanced_obj.do_ocr,
        do_tables=advanced_obj.do_tables,
        device=advanced_obj.device,
        ocr_engine=advanced_obj.ocr_engine,
        ocr_languages=tuple(s.strip() for s in advanced_obj.ocr_lang.split(",")),
    )
    try:
        pool = get_pool()
        await pool.submit(spec)
        log.info("Job %s queued (inputs=%d, formats=%s)", job_id, len(files), formats)
    except RuntimeError:
        # Pool não inicializado — válido em testes sem lifespan, mas warn
        log.warning(
            "Job %s gravado mas pool não disponível — não submetido", job_id
        )

    return JobCreatedResponse(job_id=job_id, status="queued")


_VALID_STATUSES = ("queued", "running", "done", "error", "cancelled")
_PAGE_SIZE = 20


@router.get("", response_model=list[JobSummary])
async def list_jobs(
    favorite: int | None = Query(default=None, ge=0, le=1),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    session: AsyncSession = Depends(get_session),
) -> list[JobSummary]:
    """Lista jobs paginada (20/página) com filtros opcionais.

    Args:
        favorite: 0 ou 1 — filtra por is_favorite. Sem valor = todos.
        status: queued|running|done|error|cancelled. Sem valor = todos.
        page: Número da página (1-indexed).

    Returns:
        Lista (possivelmente vazia) de JobSummary.

    Raises:
        HTTPException(400): status inválido.
    """
    if status is not None and status not in _VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido: {status}. Aceitos: {list(_VALID_STATUSES)}",
        )

    stmt = select(Job).order_by(Job.created_at.desc())
    if favorite is not None:
        stmt = stmt.where(Job.is_favorite == favorite)
    if status:
        stmt = stmt.where(Job.status == status)
    stmt = stmt.limit(_PAGE_SIZE).offset((page - 1) * _PAGE_SIZE)

    result = await session.execute(stmt)
    return [JobSummary.model_validate(j) for j in result.scalars()]


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: str, session: AsyncSession = Depends(get_session)
) -> JobDetail:
    """Detalhe de um job (inclui lista de files relacionados).

    Raises:
        HTTPException(404): Job não encontrado.
    """
    stmt = select(Job).where(Job.id == job_id).options(selectinload(Job.files))
    result = await session.execute(stmt)
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job não encontrado: {job_id}")

    return JobDetail(
        id=job.id,
        status=job.status,
        title=job.title,
        input_count=job.input_count,
        merge_mode=job.merge_mode,
        formats=job.formats,
        created_at=job.created_at,
        finished_at=job.finished_at,
        is_favorite=job.is_favorite,
        error_msg=job.error_msg,
        page_count=job.page_count,
        files=[
            JobFileInfo(role=f.role, filename=f.filename, size_bytes=f.size_bytes)
            for f in job.files
        ],
    )


@router.patch("/{job_id}", response_model=JobDetail)
async def update_job(
    job_id: str,
    body: JobUpdate,
    session: AsyncSession = Depends(get_session),
) -> JobDetail:
    """Atualiza campos editáveis de um job.

    Permite togglar favorite, renomear (title) e ajustar expires_at.
    Side effect: se `is_favorite=1`, força `expires_at=NULL` (favoritos
    nunca expiram).

    Raises:
        HTTPException(404): Job não encontrado.
    """
    stmt = select(Job).where(Job.id == job_id).options(selectinload(Job.files))
    result = await session.execute(stmt)
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job não encontrado: {job_id}")

    payload = body.model_dump(exclude_unset=True)
    if "title" in payload:
        job.title = payload["title"]
    if "expires_at" in payload:
        job.expires_at = payload["expires_at"]
    if "is_favorite" in payload:
        job.is_favorite = payload["is_favorite"]
        if job.is_favorite == 1:
            job.expires_at = None

    await session.commit()
    await session.refresh(job, ["files"])

    return JobDetail(
        id=job.id,
        status=job.status,
        title=job.title,
        input_count=job.input_count,
        merge_mode=job.merge_mode,
        formats=job.formats,
        created_at=job.created_at,
        finished_at=job.finished_at,
        is_favorite=job.is_favorite,
        error_msg=job.error_msg,
        page_count=job.page_count,
        files=[
            JobFileInfo(role=f.role, filename=f.filename, size_bytes=f.size_bytes)
            for f in job.files
        ],
    )


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Remove um job: linha do DB (cascade em JobFile) + pasta no disco.

    Raises:
        HTTPException(404): Job não encontrado.
    """
    settings = get_settings()
    job = await session.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job não encontrado: {job_id}")

    await session.delete(job)
    await session.commit()

    # Remove a pasta do filesystem (best-effort)
    target = job_dir(settings.data_dir, job_id)
    shutil.rmtree(target, ignore_errors=True)
    log.info("Job %s deletado (DB + disco)", job_id)

    return Response(status_code=204)
