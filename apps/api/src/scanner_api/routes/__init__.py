"""HTTP routes — agrupados por área."""

from scanner_api.routes.health import router as health_router

__all__ = ["health_router"]
