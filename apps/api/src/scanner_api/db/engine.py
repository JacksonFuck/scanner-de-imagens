"""SQLAlchemy 2.0 engine + session factory (async via aiosqlite).

A engine é singleton e criada lazy via `get_engine()`. As sessions são curtas:
abertas por request via dependency `get_session()`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from scanner_api.settings import get_settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Singleton: cria a engine ao primeiro uso.

    Em testes, limpe via `get_engine.cache_clear()` para mudar o DB
    (p.ex. apontar para `:memory:` em test fixtures).
    """
    settings = get_settings()
    return create_async_engine(
        settings.db_url,
        echo=False,  # True para debug local de queries
        future=True,
        # SQLite específico: 1 conexão por path; async é cooperativo
        connect_args={"check_same_thread": False},
    )


@lru_cache(maxsize=1)
def async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Factory de sessions assíncronas, vinculada à engine singleton."""
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: cede uma session por request, encerra ao fim.

    Uso em rotas:
        @router.get("/...")
        async def handler(session: AsyncSession = Depends(get_session)):
            ...
    """
    factory = async_session_factory()
    async with factory() as session:
        yield session
