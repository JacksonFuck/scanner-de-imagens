"""GET /api/jobs/{job_id}/files/{filename} — download seguro de outputs.

Procura o arquivo solicitado em `outputs/`, `images/` e `inputs/` (nessa
ordem) dentro do diretório do job. Valida path traversal antes de servir.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from scanner_api.db import get_session
from scanner_api.db.models import Job
from scanner_api.settings import get_settings
from scanner_api.storage import job_dir

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["files"])

# Subpastas onde procuramos o arquivo (ordem importa: outputs > images > inputs)
_SEARCH_SUBDIRS = ("outputs", "images", "inputs")


@router.get("/{job_id}/files/{filename}")
async def download_file(
    job_id: str,
    filename: str,
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    """Retorna arquivo do job como download.

    Args:
        job_id: UUID do job.
        filename: Nome do arquivo (sem path — só nome dentro de uma subpasta).

    Returns:
        FileResponse com Content-Disposition: attachment.

    Raises:
        HTTPException(404): Job não encontrado ou arquivo não encontrado.
        HTTPException(400): Path traversal detectado.
    """
    # Valida que o job existe (evita leak de info via timing)
    job = await session.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job não encontrado: {job_id}")

    settings = get_settings()
    base = job_dir(settings.data_dir, job_id).resolve()

    # Procura em ordem de prioridade
    for sub in _SEARCH_SUBDIRS:
        candidate = (base / sub / filename).resolve()

        # Path traversal check: candidate DEVE estar dentro de base
        try:
            candidate.relative_to(base)
        except ValueError as exc:
            log.warning(
                "Path traversal blocked: job=%s filename=%r", job_id, filename
            )
            raise HTTPException(status_code=400, detail="Path inválido") from exc

        if candidate.exists() and candidate.is_file():
            log.info("Serving %s/%s/%s", job_id, sub, filename)
            return FileResponse(
                candidate,
                filename=filename,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                },
            )

    raise HTTPException(
        status_code=404,
        detail=f"Arquivo não encontrado no job {job_id}: {filename}",
    )
