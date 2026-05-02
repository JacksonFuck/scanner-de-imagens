"""GET /api/health — informa estado do servidor (device, queue, disk).

Phase 1A: queue_depth e workers_busy retornam 0 (sem worker pool ainda).
Phase 1B atualiza esses valores conectando ao ProcessPoolExecutor real.
"""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select

from scanner_api import __version__
from scanner_api.db.engine import async_session_factory
from scanner_api.db.models import Job, PushSubscription
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
    pending_purge: int
    total_subscriptions: int
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


def _pool_metrics() -> tuple[int, int]:
    """Retorna (queue_depth, workers_busy) do pool, ou (0, 0) se off.

    Em testes ou antes do lifespan rodar, o pool pode não existir — fallback
    silencioso para 0/0 (mesmo comportamento da Phase 1A).
    """
    try:
        from scanner_api.workers.pool import get_pool

        pool = get_pool()
        return pool.queue_depth, pool.workers_busy
    except RuntimeError:
        return 0, 0


async def _db_counts() -> tuple[int, int]:
    """Retorna (pending_purge, total_subscriptions). 0/0 em caso de erro."""
    try:
        factory = async_session_factory()
        now = datetime.now(UTC).replace(tzinfo=None)
        async with factory() as session:
            pending_stmt = select(func.count(Job.id)).where(
                Job.expires_at.is_not(None),
                Job.expires_at < now,
                Job.is_favorite == 0,
            )
            subs_stmt = select(func.count(PushSubscription.endpoint))
            pending = (await session.execute(pending_stmt)).scalar_one() or 0
            subs = (await session.execute(subs_stmt)).scalar_one() or 0
            return int(pending), int(subs)
    except Exception:
        return 0, 0


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Retorna estado do servidor."""
    settings = get_settings()
    device, gpu_name = _resolve_device()
    queue_depth, workers_busy = _pool_metrics()
    pending_purge, total_subscriptions = await _db_counts()

    return HealthResponse(
        device=device,
        gpu_name=gpu_name,
        queue_depth=queue_depth,
        workers_busy=workers_busy,
        db_size_mb=round(_db_size_mb(settings.db_path), 2),
        disk_free_gb=round(_disk_free_gb(settings.data_dir), 2),
        pending_purge=pending_purge,
        total_subscriptions=total_subscriptions,
        version=__version__,
    )
