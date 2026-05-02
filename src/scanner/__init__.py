"""Scanner de Imagens — OCR de fotos de páginas para Markdown estruturado + DOCX.

Pacote principal. Exporta a versão e a função pública de orquestração.
"""

from __future__ import annotations

__version__ = "0.1.0"

from scanner.errors import ConversionError, InvalidInputError, ScannerError
from scanner.pipeline import OutputFormat, ScanRequest, ScanResult, scan

__all__ = [
    "ConversionError",
    "InvalidInputError",
    "OutputFormat",
    "ScanRequest",
    "ScanResult",
    "ScannerError",
    "__version__",
    "scan",
]
