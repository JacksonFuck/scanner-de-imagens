"""Conversão Markdown → DOCX usando pandoc.

Decisão registrada em `vault/projeto/decisoes.md`: pandoc via `pypandoc` em
vez de python-docx puro. Pandoc preserva imagens (paths relativos no MD viram
imagens embutidas no DOCX) e estrutura semântica (headings, tabelas, listas)
sem precisar reimplementar manualmente.

Pandoc precisa estar instalado no sistema. Se não estiver, `pypandoc` faz
download de uma release oficial via `download_pandoc()` na primeira execução.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from scanner.errors import ConfigurationError, ConversionError

log = logging.getLogger(__name__)


def write_docx(markdown_path: Path, target: Path, *, resource_dir: Path | None = None) -> Path:
    """Converte um arquivo Markdown para DOCX preservando imagens e estrutura.

    Args:
        markdown_path: Arquivo .md de origem.
        target: Caminho final do .docx (será sobrescrito se existir).
        resource_dir: Pasta onde o pandoc procura imagens referenciadas.
            Default: pasta do `markdown_path` (imagens relativas ao .md).

    Returns:
        O `target` resolvido.

    Raises:
        ConfigurationError: pandoc não disponível e falhou auto-download.
        ConversionError: pandoc falhou na conversão.
    """
    markdown_path = markdown_path.resolve()
    target = target.resolve()
    if resource_dir is None:
        resource_dir = markdown_path.parent
    target.parent.mkdir(parents=True, exist_ok=True)

    pandoc_bin = _ensure_pandoc()
    log.debug("Usando pandoc: %s", pandoc_bin)

    try:
        import pypandoc
    except ImportError as exc:
        raise ConfigurationError("pypandoc não instalado. Rode: pip install pypandoc") from exc

    try:
        pypandoc.convert_file(
            source_file=str(markdown_path),
            to="docx",
            outputfile=str(target),
            extra_args=[
                f"--resource-path={resource_dir}",
                "--standalone",
            ],
        )
    except Exception as exc:
        raise ConversionError(f"pandoc falhou ao gerar {target.name}: {exc}") from exc

    log.info("DOCX gravado: %s", target)
    return target


def _ensure_pandoc() -> str:
    """Garante que pandoc está disponível. Tenta auto-download se necessário."""
    if shutil.which("pandoc"):
        return "pandoc"

    try:
        import pypandoc
    except ImportError as exc:
        raise ConfigurationError("pypandoc não instalado.") from exc

    log.warning("pandoc não encontrado no PATH — fazendo download via pypandoc")
    try:
        pypandoc.download_pandoc()
    except Exception as exc:
        raise ConfigurationError(
            "Falha ao baixar pandoc automaticamente. "
            "Instale manualmente: https://pandoc.org/installing.html"
        ) from exc
    return "pandoc"
