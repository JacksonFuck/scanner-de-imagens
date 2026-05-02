"""Alembic environment — usa async engine + import dos models.

Roda em modo online por default (precisa do DB rodando). Modo offline gera
SQL dump pra revisão manual sem aplicar.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from scanner_api.db.models import Base
from scanner_api.settings import get_settings

# Alembic Config object — provê acesso ao alembic.ini
config = context.config

# Logging do alembic.ini (se houver seção)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Injeta a URL real do settings (sobrescreve sqlalchemy.url do alembic.ini)
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.db_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Modo offline: emite SQL no stdout, não conecta no DB."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Aplicação síncrona da migração — chamada via run_sync."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Cria engine async, aplica migrações via run_sync."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Modo online: aplica migrações no DB real."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
