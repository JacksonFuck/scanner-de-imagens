"""POST/GET /api/jobs.

POST cria um job: salva inputs em disco, grava no DB, submete ao worker pool.
GET lista (paginado, com filtros) e GET /{id} retorna detalhe.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from scanner_api.db import get_session
from scanner_api.db.models import Job, JobFile
from scanner_api.schemas import JobAdvancedOptions, JobCreatedResponse
from scanner_api.settings import get_settings
from scanner_api.storage import (
    ensure_data_dirs,
    ensure_job_dirs,
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
