"""FastAPI application — entry point para Uvicorn.

Lifespan async para inicialização (worker pool em Phase 1B). CORS aberto
para o frontend Next.js. Routes são montadas via include_router.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scanner_api import __version__

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown hooks.

    Inicializa data dirs + worker pool. Em testes, lifespan pode não rodar
    (httpx ASGI client direto não dispara) — handlers usam fallback safe.
    """
    from scanner_api.settings import get_settings
    from scanner_api.storage import ensure_data_dirs
    from scanner_api.workers.pool import init_pool, shutdown_pool

    settings = get_settings()
    ensure_data_dirs(settings.data_dir)
    await init_pool(settings.max_workers)
    log.info("scanner_api %s startup", __version__)
    try:
        yield
    finally:
        await shutdown_pool()
        log.info("scanner_api %s shutdown", __version__)


def create_app() -> FastAPI:
    """Factory para criar a app — facilita testes (cria app por test client)."""
    app = FastAPI(
        title="Scanner de Imagens API",
        version=__version__,
        description="OCR de fotos de páginas → Markdown + DOCX + PDF",
        lifespan=lifespan,
    )

    # CORS: permitir o frontend Next.js (mesmo domínio em prod via Nginx)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ajustado em produção via env var
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    from scanner_api.routes import health_router, jobs_router

    app.include_router(health_router)
    app.include_router(jobs_router)
    # Phase 1B continua: files_router, ws_router
    # Phase 1C adiciona: push_router

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "scanner_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
