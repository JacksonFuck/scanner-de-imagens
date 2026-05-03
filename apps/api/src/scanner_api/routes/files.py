"""GET /api/jobs/{job_id}/files/{filename} — download seguro de outputs.

Também expõe `GET /api/jobs/{job_id}/download` que retorna um ZIP com
todos os arquivos da pasta `outputs/` (atalho para o usuário não precisar
clicar em cada arquivo).

Procura o arquivo solicitado em `outputs/`, `images/` e `inputs/` (nessa
ordem) dentro do diretório do job. Valida path traversal antes de servir.
"""

from __future__ import annotations

import io
import logging
import re
import zipfile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from scanner_api.db import get_session
from scanner_api.db.models import Job
from scanner_api.settings import get_settings
from scanner_api.storage import job_dir

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["files"])

# Subpastas onde procuramos o arquivo (ordem importa: outputs > images > inputs)
_SEARCH_SUBDIRS = ("outputs", "images", "inputs")


def _safe_zip_name(text: str) -> str:
    """Sanitiza o título do job para virar nome de arquivo ZIP."""
    text = text.strip() or "job"
    text = re.sub(r"[^\w\-. ]+", "_", text, flags=re.UNICODE)
    return text[:80]


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


@router.get("/{job_id}/download")
async def download_all(
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """Retorna ZIP com todos os arquivos de `outputs/` do job.

    Usado pelo botão de download direto da listagem de jobs. Inclui
    Markdown, DOCX, PDF e a pasta `<base>-images/`. Não inclui inputs
    (a foto original) — só o que foi gerado.
    """
    job = await session.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job não encontrado: {job_id}")

    settings = get_settings()
    base = job_dir(settings.data_dir, job_id).resolve()
    outputs_dir = (base / "outputs").resolve()

    if not outputs_dir.exists() or not outputs_dir.is_dir():
        raise HTTPException(
            status_code=404, detail=f"Job {job_id} não tem outputs gerados ainda."
        )

    files = [p for p in outputs_dir.rglob("*") if p.is_file()]
    if not files:
        raise HTTPException(
            status_code=404, detail=f"Job {job_id} ainda não produziu arquivos."
        )

    # Constrói o ZIP em memória — outputs típicos têm ~14 mds (~3 KB cada)
    # + algumas imagens; cabe folgado em RAM. Para volumes maiores, vale
    # migrar para zipstream-ng com StreamingResponse iterativo.
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = path.relative_to(outputs_dir).as_posix()
            zf.write(path, arcname)
    buf.seek(0)

    title = _safe_zip_name(job.title or job_id)
    log.info("ZIP %s: %d files, %d bytes", job_id, len(files), buf.getbuffer().nbytes)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{title}.zip"'},
    )
