"""Testes de PATCH/DELETE em /api/jobs/{id}."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from httpx import AsyncClient


async def _create_job(client: AsyncClient) -> str:
    """Helper: cria um job básico, retorna o job_id."""
    files = {"files": ("a.jpg", b"x", "image/jpeg")}
    response = await client.post("/api/jobs", files=files, data={"formats": "md"})
    assert response.status_code == 201
    return response.json()["job_id"]


@pytest.mark.asyncio
async def test_patch_favorite_clears_expires(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """PATCH is_favorite=1 zera expires_at."""
    job_id = await _create_job(client)

    response = await client.patch(
        f"/api/jobs/{job_id}",
        json={"is_favorite": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_favorite"] == 1

    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import Job

    factory = async_session_factory()
    async with factory() as session:
        job = await session.get(Job, job_id)
        assert job is not None
        assert job.is_favorite == 1
        assert job.expires_at is None


@pytest.mark.asyncio
async def test_patch_renames(client: AsyncClient, tmp_data_dir: Path) -> None:
    """PATCH com title atualiza o nome."""
    job_id = await _create_job(client)
    response = await client.patch(
        f"/api/jobs/{job_id}",
        json={"title": "Novo Nome"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Novo Nome"


@pytest.mark.asyncio
async def test_patch_unfavorite_keeps_provided_expires(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """PATCH is_favorite=0 + expires_at preserva expires_at."""
    job_id = await _create_job(client)
    future = (datetime.now(UTC) + timedelta(days=7)).replace(tzinfo=None)
    response = await client.patch(
        f"/api/jobs/{job_id}",
        json={"is_favorite": 0, "expires_at": future.isoformat()},
    )
    assert response.status_code == 200

    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import Job

    factory = async_session_factory()
    async with factory() as session:
        job = await session.get(Job, job_id)
        assert job is not None
        assert job.is_favorite == 0
        assert job.expires_at is not None


@pytest.mark.asyncio
async def test_patch_404(client: AsyncClient, tmp_data_dir: Path) -> None:
    """PATCH em job inexistente → 404."""
    response = await client.patch(
        "/api/jobs/nonexistent-id",
        json={"is_favorite": 1},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_cascades_filesystem(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """DELETE remove DB + pasta de inputs."""
    job_id = await _create_job(client)
    job_folder = tmp_data_dir / "jobs" / job_id
    assert job_folder.exists()

    response = await client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 204

    assert not job_folder.exists()

    from sqlalchemy import select

    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import Job, JobFile

    factory = async_session_factory()
    async with factory() as session:
        job = await session.get(Job, job_id)
        assert job is None
        # JobFile cascade (filhos foram apagados)
        files_left = (
            await session.execute(
                select(JobFile).where(JobFile.job_id == job_id)
            )
        ).scalars().all()
        assert files_left == []


@pytest.mark.asyncio
async def test_delete_404(client: AsyncClient, tmp_data_dir: Path) -> None:
    """DELETE em job inexistente → 404."""
    response = await client.delete("/api/jobs/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_idempotent_filesystem(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Mesmo se o filesystem já foi removido por fora, DELETE não falha."""
    job_id = await _create_job(client)
    job_folder = tmp_data_dir / "jobs" / job_id
    import shutil

    shutil.rmtree(job_folder)

    response = await client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 204
