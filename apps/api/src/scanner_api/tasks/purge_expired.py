"""Purga jobs expirados do DB e do filesystem.

Critério: `expires_at < NOW()` AND `is_favorite = 0`. Favoritos nunca expiram.

Idempotente — re-execução não dá erro mesmo se a pasta já foi removida.

Uso (cron diário sugerido às 4h):
    python -m scanner_api.tasks.purge_expired
"""

from __future__ import annotations

import asyncio
import logging
import shutil
from datetime import UTC, datetime

from sqlalchemy import select

from scanner_api.db.engine import async_session_factory
from scanner_api.db.models import Job
from scanner_api.settings import get_settings
from scanner_api.storage import job_dir

log = logging.getLogger(__name__)


async def purge() -> int:
    """Remove jobs expirados (DB + filesystem). Retorna o count removido."""
    settings = get_settings()
    factory = async_session_factory()
    now = datetime.now(UTC).replace(tzinfo=None)  # SQLite armazena naive

    removed = 0
    async with factory() as session:
        stmt = select(Job).where(
            Job.expires_at.is_not(None),
            Job.expires_at < now,
            Job.is_favorite == 0,
        )
        result = await session.execute(stmt)
        jobs = list(result.scalars())

        for job in jobs:
            target = job_dir(settings.data_dir, job.id)
            shutil.rmtree(target, ignore_errors=True)
            await session.delete(job)
            removed += 1

        await session.commit()

    log.info("purge_expired: %d jobs removidos", removed)
    return removed


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    count = asyncio.run(purge())
    print(f"Removed {count} expired job(s)")


if __name__ == "__main__":
    main()
