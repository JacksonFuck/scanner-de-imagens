"""Testes do endpoint /api/health."""

from __future__ import annotations

from httpx import AsyncClient


async def test_health_returns_200(client: AsyncClient) -> None:
    """GET /api/health responde 200."""
    response = await client.get("/api/health")
    assert response.status_code == 200


async def test_health_payload_shape(client: AsyncClient) -> None:
    """Payload tem todos os campos especificados (Section 7.1)."""
    response = await client.get("/api/health")
    body = response.json()
    expected_keys = {
        "device",
        "gpu_name",
        "queue_depth",
        "workers_busy",
        "db_size_mb",
        "disk_free_gb",
        "version",
    }
    assert set(body.keys()) == expected_keys


async def test_health_device_is_valid(client: AsyncClient) -> None:
    """device é cuda | cpu (não 'auto' — já resolvido em runtime)."""
    response = await client.get("/api/health")
    body = response.json()
    assert body["device"] in ("cuda", "cpu")


async def test_health_queue_zero_initially(client: AsyncClient) -> None:
    """Phase 1A não tem worker pool ainda — queue_depth = 0."""
    response = await client.get("/api/health")
    body = response.json()
    assert body["queue_depth"] == 0
    assert body["workers_busy"] == 0


async def test_health_version_matches_package(client: AsyncClient) -> None:
    """version é o __version__ do scanner_api."""
    from scanner_api import __version__

    response = await client.get("/api/health")
    body = response.json()
    assert body["version"] == __version__


async def test_health_disk_free_is_positive(client: AsyncClient) -> None:
    """disk_free_gb > 0 num filesystem real."""
    response = await client.get("/api/health")
    body = response.json()
    assert body["disk_free_gb"] > 0


async def test_health_db_size_zero_before_init(client: AsyncClient) -> None:
    """Antes de Alembic upgrade, scanner.db não existe — tamanho = 0."""
    response = await client.get("/api/health")
    body = response.json()
    assert body["db_size_mb"] == 0.0
