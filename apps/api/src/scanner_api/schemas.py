"""Pydantic schemas para request/response da API.

Separado dos ORM models (db/models.py) para permitir validação independente
do schema do DB. Quando o ORM mudar (ex: adicionar coluna user_id em
Phase 2 multi-tenant), o schema externo pode ficar igual.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobAdvancedOptions(BaseModel):
    """Sub-objeto de opções avançadas (corresponde ao painel Advanced no frontend)."""

    do_ocr: bool = True
    do_tables: bool = True
    ocr_engine: str = Field(default="easyocr", pattern="^(easyocr|tesseract)$")
    ocr_lang: str = Field(default="pt,en")
    device: str = Field(default="auto", pattern="^(auto|cuda|cpu)$")


class JobCreatedResponse(BaseModel):
    """Retorno do POST /api/jobs."""

    job_id: str
    status: str  # 'queued'


class JobFileInfo(BaseModel):
    """Item de arquivo num job."""

    model_config = ConfigDict(from_attributes=True)

    role: str
    filename: str
    size_bytes: int


class JobSummary(BaseModel):
    """Item de listagem (sem arquivos detalhados)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    title: str | None
    input_count: int
    formats: str
    created_at: datetime
    is_favorite: int


class JobUpdate(BaseModel):
    """Body do PATCH /api/jobs/{id} — todos os campos opcionais.

    Side effect: se `is_favorite=1`, `expires_at` é forçado para NULL
    (favoritos nunca expiram). Para definir manualmente expires_at sem
    favoritar, envie is_favorite=0 OU omita is_favorite.
    """

    is_favorite: int | None = Field(default=None, ge=0, le=1)
    title: str | None = None
    expires_at: datetime | None = None


class JobDetail(BaseModel):
    """Detalhe completo de um job (inclui files)."""

    model_config = ConfigDict(from_attributes=True)

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
