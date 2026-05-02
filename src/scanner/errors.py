"""Exceções específicas do scanner.

Hierarquia simples: tudo herda de `ScannerError` para que o CLI possa capturar
qualquer falha esperada num único `except` e formatar mensagem amigável.
Erros não-esperados continuam subindo como `Exception` e geram traceback.
"""

from __future__ import annotations


class ScannerError(Exception):
    """Erro base do scanner — qualquer falha esperada herda daqui."""


class InvalidInputError(ScannerError):
    """Input inexistente, formato não suportado ou corrompido."""


class ConversionError(ScannerError):
    """Falha durante extração via Docling ou conversão para DOCX."""


class ConfigurationError(ScannerError):
    """Configuração inválida (engine não disponível, pandoc faltando, etc.)."""
