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

    Phase 1A: apenas log + placeholder. Phase 1B adiciona ProcessPoolExecutor.
    """
    log.info("scanner_api %s startup", __version__)
    yield
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

    # Routes: montadas em Phase 1A Task 6 (health) + Phase 1B (jobs/ws)
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
