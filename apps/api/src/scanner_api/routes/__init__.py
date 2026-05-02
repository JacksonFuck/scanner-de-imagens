"""HTTP routes — agrupados por área."""

from scanner_api.routes.health import router as health_router
from scanner_api.routes.jobs import router as jobs_router
from scanner_api.routes.ws import router as ws_router

__all__ = ["health_router", "jobs_router", "ws_router"]
