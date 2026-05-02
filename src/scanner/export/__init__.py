"""Exporters — escrevem o resultado da extração em formatos finais."""

from scanner.export.docx import write_docx
from scanner.export.markdown import write_markdown

__all__ = ["write_docx", "write_markdown"]
