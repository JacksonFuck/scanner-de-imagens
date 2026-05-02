"""Fixtures compartilhadas dos testes do scanner_api."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def tmp_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Cria um data dir temporário e seta env vars necessárias.

    SCANNER_VAPID_* são stubs nos testes — push notifications não são
    exercitadas aqui. Em integração real (Phase 1C tests) usaremos chaves
    de teste reais.
    """
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("SCANNER_DATA_DIR", str(data))
    monkeypatch.setenv("SCANNER_VAPID_PUBLIC_KEY", "test-public-key")
    monkeypatch.setenv("SCANNER_VAPID_PRIVATE_KEY", "test-private-key")
    monkeypatch.setenv("SCANNER_VAPID_EMAIL", "test@example.com")

    # Limpa singletons de settings/db cacheados entre testes
    from scanner_api.settings import get_settings  # noqa: F401 (lazy)
    return data


@pytest.fixture
def app(tmp_data_dir: Path) -> Iterator[FastAPI]:
    """Cria uma instância nova da app por test (lifespan correto)."""
    # Limpa caches lru_cache de settings entre testes
    from scanner_api.settings import get_settings

    get_settings.cache_clear()

    from scanner_api.main import create_app

    yield create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """httpx AsyncClient apontado para a app em ASGI mode."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
