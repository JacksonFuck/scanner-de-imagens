"""Testes dos ORM models — mapping, relationship, cascade."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from scanner_api.db.models import Base, Job, JobFile, PushSubscription


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Engine in-memory por test (isolamento total entre casos)."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


async def test_job_can_be_created(session: AsyncSession) -> None:
    """Um Job pode ser inserido e recuperado."""
    job = Job(
        id="job-1",
        status="queued",
        title="test",
        input_count=2,
        merge_mode=1,
        formats="all",
    )
    session.add(job)
    await session.commit()

    fetched = await session.get(Job, "job-1")
    assert fetched is not None
    assert fetched.title == "test"
    assert fetched.input_count == 2
    assert fetched.merge_mode == 1
    assert fetched.formats == "all"
    assert fetched.is_favorite == 0  # default


async def test_job_status_constraint_rejects_invalid(session: AsyncSession) -> None:
    """status IN ('queued','running','done','error','cancelled') é validado."""
    from sqlalchemy.exc import IntegrityError

    job = Job(
        id="job-bad",
        status="invalid-status",
        input_count=1,
        merge_mode=0,
        formats="md",
    )
    session.add(job)
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_job_files_cascade_delete(session: AsyncSession) -> None:
    """Deletar Job apaga JobFile relacionados (cascade ON DELETE)."""
    job = Job(
        id="job-2", status="queued", input_count=1, merge_mode=0, formats="md"
    )
    job.files.append(
        JobFile(role="input", filename="foto.jpg", size_bytes=1000)
    )
    session.add(job)
    await session.commit()

    # Confirma que o JobFile foi inserido
    files_before = (await session.execute(select(JobFile))).scalars().all()
    assert len(files_before) == 1

    # Deleta o Job — files devem cascatear
    await session.delete(job)
    await session.commit()

    files_after = (await session.execute(select(JobFile))).scalars().all()
    assert files_after == []


async def test_job_file_role_constraint(session: AsyncSession) -> None:
    """role IN ('input','output_md','output_docx','output_pdf','image') é validado."""
    from sqlalchemy.exc import IntegrityError

    job = Job(
        id="job-3", status="queued", input_count=1, merge_mode=0, formats="md"
    )
    job.files.append(
        JobFile(role="invalid-role", filename="x", size_bytes=1)
    )
    session.add(job)
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_push_subscription_unique_endpoint(session: AsyncSession) -> None:
    """endpoint é PRIMARY KEY — não pode duplicar."""
    from sqlalchemy.exc import IntegrityError

    s1 = PushSubscription(
        endpoint="https://example.com/1", p256dh="x", auth="y"
    )
    session.add(s1)
    await session.commit()

    s2 = PushSubscription(
        endpoint="https://example.com/1", p256dh="x2", auth="y2"
    )
    session.add(s2)
    with pytest.raises(IntegrityError):
        await session.commit()
