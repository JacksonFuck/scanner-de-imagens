"""HTTP routes — agrupados por área."""

from scanner_api.routes.files import router as files_router
from scanner_api.routes.health import router as health_router
from scanner_api.routes.jobs import router as jobs_router
from scanner_api.routes.push import router as push_router
from scanner_api.routes.ws import router as ws_router

__all__ = [
    "files_router",
    "health_router",
    "jobs_router",
    "push_router",
    "ws_router",
]
