"""Conversão Markdown → PDF usando pandoc + xelatex.

Decisão registrada em `docs/superpowers/specs/2026-05-02-web-app-pwa-design.md`
(Seção 11.2): pandoc + xelatex como motor PDF principal — reusa toolchain do
DOCX, lida com acentos PT-BR nativamente, gera PDF "estilo artigo" com
tipografia decente.

Pré-requisitos:
- pandoc no PATH (ou cache pypandoc) — ver `scanner.export._pandoc.ensure_pandoc`
- xelatex (TeX Live com pacote xetex) instalado. Em produção (Hostinger)
  vai no Dockerfile via `apt-get install texlive-xetex`. No Windows, MikTeX
  ou TeX Live oficial.
"""

from __future__ import annotations

import logging
from pathlib import Path

from scanner.errors import ConfigurationError, ConversionError
from scanner.export._pandoc import ensure_pandoc

log = logging.getLogger(__name__)


def write_pdf(
    markdown_path: Path,
    target: Path,
    *,
    resource_dir: Path | None = None,
    pdf_engine: str = "xelatex",
) -> Path:
    """Converte um arquivo Markdown para PDF preservando estrutura e imagens.

    Args:
        markdown_path: Arquivo .md de origem.
        target: Caminho final do .pdf (será sobrescrito se existir).
        resource_dir: Pasta base para resolver imagens referenciadas no MD.
            Se None, usa o diretório do `markdown_path`.
        pdf_engine: 'xelatex' (default, suporta UTF-8 nativo) | 'lualatex' | 'pdflatex'.

    Returns:
        Path absoluto do PDF gerado.

    Raises:
        ConfigurationError: pandoc ausente E auto-download falhou.
        ConversionError: pandoc/xelatex falharam na conversão (p.ex. xelatex
            não instalado, fonte ausente, sintaxe MD inválida para LaTeX).
    """
    markdown_path = markdown_path.resolve()
    target = target.resolve()
    if resource_dir is None:
        resource_dir = markdown_path.parent
    target.parent.mkdir(parents=True, exist_ok=True)

    pandoc_bin = ensure_pandoc()
    log.debug("Usando pandoc: %s (engine=%s)", pandoc_bin, pdf_engine)

    try:
        import pypandoc  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ConfigurationError("pypandoc não instalado.") from exc

    extra_args: list[str] = [
        f"--pdf-engine={pdf_engine}",
        f"--resource-path={resource_dir}",
        "--variable=geometry:margin=2cm",
        "--variable=lang:pt-BR",
        "--standalone",
    ]

    log.info("Gerando PDF: %s -> %s", markdown_path.name, target.name)
    try:
        pypandoc.convert_file(
            source_file=str(markdown_path),
            to="pdf",
            outputfile=str(target),
            extra_args=extra_args,
        )
    except Exception as exc:  # pypandoc lança múltiplos tipos
        raise ConversionError(
            f"Falha ao gerar PDF de {markdown_path.name} "
            f"(engine={pdf_engine}): {exc}"
        ) from exc

    if not target.exists() or target.stat().st_size == 0:
        raise ConversionError(
            f"Pandoc retornou sucesso mas o PDF está vazio: {target}"
        )
    log.info("PDF gravado: %s (%d bytes)", target, target.stat().st_size)
    return target
