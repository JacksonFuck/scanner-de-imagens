"""Testes do WorkerPool — start/stop sem rodar Docling."""

from __future__ import annotations

import pytest

from scanner_api.workers import WorkerPool, get_pool, init_pool, shutdown_pool


async def test_pool_start_shutdown() -> None:
    """Pool é criado, expõe métricas zeradas, e encerra sem erro."""
    pool = WorkerPool(max_workers=1)
    await pool.start()
    try:
        assert pool.queue_depth == 0
        assert pool.workers_busy == 0
        assert pool.max_workers == 1
    finally:
        await pool.shutdown()


async def test_pool_double_shutdown_is_safe() -> None:
    """Chamar shutdown() duas vezes não levanta."""
    pool = WorkerPool(max_workers=1)
    await pool.start()
    await pool.shutdown()
    await pool.shutdown()  # idempotente


async def test_init_pool_singleton() -> None:
    """init_pool armazena a instância como singleton acessível via get_pool()."""
    # Garante estado limpo
    await shutdown_pool()
    p = await init_pool(max_workers=2)
    try:
        assert get_pool() is p
        assert get_pool().max_workers == 2
    finally:
        await shutdown_pool()


def test_get_pool_raises_when_not_initialized() -> None:
    """get_pool() levanta RuntimeError se ninguém chamou init_pool()."""
    # NOTA: roda síncronamente; assume que init_pool não foi chamado
    # (testes async podem ter chamado — limpamos via fixture)
    import scanner_api.workers.pool as pool_module

    pool_module._pool = None  # reset manual para garantir
    with pytest.raises(RuntimeError, match="não inicializado"):
        get_pool()


async def test_init_pool_replaces_existing() -> None:
    """Chamar init_pool 2x encerra o primeiro pool e cria um novo."""
    p1 = await init_pool(max_workers=1)
    p2 = await init_pool(max_workers=2)
    try:
        assert p1 is not p2
        assert get_pool() is p2
        assert get_pool().max_workers == 2
    finally:
        await shutdown_pool()
