"""GET /api/health — informa estado do servidor (device, queue, disk).

Phase 1A: queue_depth e workers_busy retornam 0 (sem worker pool ainda).
Phase 1B atualiza esses valores conectando ao ProcessPoolExecutor real.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from scanner_api import __version__
from scanner_api.settings import get_settings

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    """Payload do /api/health (espelha spec Section 7.1)."""

    device: str  # cuda | cpu
    gpu_name: str | None
    queue_depth: int
    workers_busy: int
    db_size_mb: float
    disk_free_gb: float
    version: str


def _resolve_device() -> tuple[str, str | None]:
    """Detecta device atual (CUDA disponível? GPU name?).

    Honra `settings.device`: se 'cpu', força CPU sem checar torch.
    """
    settings = get_settings()
    if settings.device == "cpu":
        return "cpu", None
    try:
        import torch
    except ImportError:
        return "cpu", None
    if torch.cuda.is_available():
        return "cuda", torch.cuda.get_device_name(0)
    return "cpu", None


def _db_size_mb(db_path: Path) -> float:
    """Tamanho do arquivo SQLite em MB. 0 se não existe ainda."""
    if not db_path.exists():
        return 0.0
    return db_path.stat().st_size / (1024 * 1024)


def _disk_free_gb(data_dir: Path) -> float:
    """Espaço livre no filesystem do data_dir, em GB.

    Se o data_dir ainda não existe, sobe para o parent que exista.
    """
    target = data_dir
    while not target.exists() and target != target.parent:
        target = target.parent
    usage = shutil.disk_usage(target)
    return usage.free / (1024**3)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Retorna estado do servidor."""
    settings = get_settings()
    device, gpu_name = _resolve_device()

    return HealthResponse(
        device=device,
        gpu_name=gpu_name,
        queue_depth=0,  # Phase 1B conecta com pool real
        workers_busy=0,
        db_size_mb=round(_db_size_mb(settings.db_path), 2),
        disk_free_gb=round(_disk_free_gb(settings.data_dir), 2),
        version=__version__,
    )
