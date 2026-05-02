"""Scanner de Imagens — FastAPI backend.

Exposes the scanner OCR pipeline as a single-tenant web API with async jobs,
WebSocket progress, and push notifications. Reuses src/scanner/ as a library
(no fork of OCR logic).
"""

from __future__ import annotations

__version__ = "0.1.0"
