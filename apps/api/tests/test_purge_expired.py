"""Testes da task `purge_expired`."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_purge_expired_removes_only_expired_nonfav(
    tmp_data_dir: Path,
) -> None:
    """Cria 3 jobs (expirado normal, expirado favorito, ativo) e roda purge.

    Espera-se que somente o expirado normal seja removido (DB + filesystem).
    """
    # Garante que as tabelas existem
    from scanner_api.db.engine import async_session_factory, get_engine
    from scanner_api.db.models import Base, Job
    from scanner_api.tasks.purge_expired import purge

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    past = (datetime.now(UTC) - timedelta(hours=2)).replace(tzinfo=None)
    future = (datetime.now(UTC) + timedelta(hours=2)).replace(tzinfo=None)

    factory = async_session_factory()
    async with factory() as session:
        session.add(
            Job(
                id="job-expired",
                status="done",
                title="expired",
                input_count=1,
                formats="md",
                expires_at=past,
                is_favorite=0,
            )
        )
        session.add(
            Job(
                id="job-expired-fav",
                status="done",
                title="expired-fav",
                input_count=1,
                formats="md",
                expires_at=past,
                is_favorite=1,
            )
        )
        session.add(
            Job(
                id="job-active",
                status="done",
                title="active",
                input_count=1,
                formats="md",
                expires_at=future,
                is_favorite=0,
            )
        )
        await session.commit()

    # Cria as pastas no filesystem
    for jid in ("job-expired", "job-expired-fav", "job-active"):
        (tmp_data_dir / "jobs" / jid).mkdir(parents=True, exist_ok=True)
        (tmp_data_dir / "jobs" / jid / "marker.txt").write_text("x")

    removed = await purge()

    assert removed == 1

    async with factory() as session:
        assert await session.get(Job, "job-expired") is None
        assert await session.get(Job, "job-expired-fav") is not None
        assert await session.get(Job, "job-active") is not None

    assert not (tmp_data_dir / "jobs" / "job-expired").exists()
    assert (tmp_data_dir / "jobs" / "job-expired-fav").exists()
    assert (tmp_data_dir / "jobs" / "job-active").exists()


@pytest.mark.asyncio
async def test_purge_idempotent(tmp_data_dir: Path) -> None:
    """Rodar purge duas vezes seguidas: 2ª retorna 0, sem erro."""
    from scanner_api.db.engine import get_engine
    from scanner_api.db.models import Base
    from scanner_api.tasks.purge_expired import purge

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    first = await purge()
    second = await purge()
    assert first == 0
    assert second == 0
