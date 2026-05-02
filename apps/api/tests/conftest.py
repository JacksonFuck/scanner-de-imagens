"""Fixtures compartilhadas dos testes do scanner_api."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def tmp_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Cria um data dir temporário e seta env vars + limpa caches.

    SCANNER_VAPID_* são stubs nos testes — push notifications não são
    exercitadas aqui.
    """
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("SCANNER_DATA_DIR", str(data))
    monkeypatch.setenv("SCANNER_VAPID_PUBLIC_KEY", "test-public-key")
    monkeypatch.setenv("SCANNER_VAPID_PRIVATE_KEY", "test-private-key")
    monkeypatch.setenv("SCANNER_VAPID_EMAIL", "test@example.com")

    # Limpa singletons de settings/db (lru_cache module-level)
    from scanner_api.db.engine import async_session_factory, get_engine
    from scanner_api.settings import get_settings

    get_settings.cache_clear()
    get_engine.cache_clear()
    async_session_factory.cache_clear()

    return data


@pytest_asyncio.fixture
async def app(tmp_data_dir: Path) -> AsyncIterator[FastAPI]:
    """App com schema do DB criado e pool não inicializado.

    Como não rodamos lifespan via httpx ASGI client, criamos as tabelas
    manualmente via Base.metadata.create_all(). Pool fica não inicializado;
    rotas que dependem dele têm fallback (health) ou tratamento explícito (jobs).
    """
    from scanner_api.db.engine import get_engine
    from scanner_api.db.models import Base
    from scanner_api.main import create_app

    # Cria tabelas no DB do tmp_data_dir
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield create_app()

    # Teardown: descarta a engine para evitar locks no Windows
    await engine.dispose()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """httpx AsyncClient apontado para a app em ASGI mode."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
