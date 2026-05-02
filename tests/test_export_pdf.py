"""Testes de geração de PDF via pandoc + xelatex.

Testes lentos (não rodam em CI minimalista). Skip automático se pandoc OU
xelatex não estiverem disponíveis no ambiente. Em produção (Hostinger Docker)
ambos vão estar — `texlive-xetex` no Dockerfile cobre xelatex.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scanner.errors import ConversionError
from scanner.export import write_pdf


def _has_pandoc() -> bool:
    """True se pandoc está acessível via PATH ou cache pypandoc."""
    if shutil.which("pandoc"):
        return True
    try:
        import pypandoc  # type: ignore[import-untyped]

        pypandoc.get_pandoc_path()
        return True
    except (ImportError, OSError):
        return False


def _has_xelatex() -> bool:
    """True se xelatex está no PATH (ou em paths comuns Windows)."""
    if shutil.which("xelatex"):
        return True
    # Paths comuns no Windows (MikTeX, TeX Live)
    candidates = [
        Path("C:/Program Files/MiKTeX/miktex/bin/x64/xelatex.exe"),
        Path("C:/texlive/2024/bin/windows/xelatex.exe"),
        Path.home() / "AppData/Local/Programs/MiKTeX/miktex/bin/x64/xelatex.exe",
    ]
    return any(p.exists() for p in candidates)


_PDF_TOOLCHAIN_AVAILABLE = _has_pandoc() and _has_xelatex()
_SKIP_REASON = (
    "Toolchain de PDF (pandoc + xelatex) não disponível neste ambiente. "
    "Em produção (Hostinger Docker) o Dockerfile instala texlive-xetex."
)


@pytest.fixture
def sample_md(tmp_path: Path) -> Path:
    """MD de exemplo com acentos PT-BR e estrutura básica."""
    md = tmp_path / "sample.md"
    md.write_text(
        "# Título com Acentuação\n\n"
        "Parágrafo com palavras: **gestão**, *atenção*, função.\n\n"
        "## Subseção\n\n"
        "- Item 1\n"
        "- Item 2 com ção\n",
        encoding="utf-8",
    )
    return md


@pytest.mark.slow
@pytest.mark.skipif(not _PDF_TOOLCHAIN_AVAILABLE, reason=_SKIP_REASON)
def test_write_pdf_creates_non_empty_file(sample_md: Path, tmp_path: Path) -> None:
    """write_pdf gera um PDF não-vazio a partir de um MD válido."""
    target = tmp_path / "output.pdf"
    result = write_pdf(sample_md, target)
    assert result == target.resolve()
    assert target.exists()
    assert target.stat().st_size > 1000  # PDF mínimo viável > 1KB


@pytest.mark.slow
@pytest.mark.skipif(not _PDF_TOOLCHAIN_AVAILABLE, reason=_SKIP_REASON)
def test_write_pdf_preserves_portuguese_chars(
    sample_md: Path, tmp_path: Path
) -> None:
    """O PDF deve ser gerado sem erro com caracteres acentuados PT-BR."""
    target = tmp_path / "output.pdf"
    write_pdf(sample_md, target)  # não levanta exceção
    assert target.exists()


@pytest.mark.slow
@pytest.mark.skipif(not _PDF_TOOLCHAIN_AVAILABLE, reason=_SKIP_REASON)
def test_write_pdf_creates_parent_dirs(sample_md: Path, tmp_path: Path) -> None:
    """write_pdf cria diretórios pais ausentes."""
    target = tmp_path / "nested" / "deep" / "output.pdf"
    write_pdf(sample_md, target)
    assert target.exists()


def test_write_pdf_raises_on_invalid_engine(sample_md: Path, tmp_path: Path) -> None:
    """Engine inexistente deve levantar ConversionError (sempre testável,
    mesmo sem xelatex disponível, porque o erro acontece antes de tocar TeX)."""
    if not _has_pandoc():
        pytest.skip("pandoc não disponível")
    target = tmp_path / "output.pdf"
    with pytest.raises(ConversionError, match=r"engine[=\-]"):
        write_pdf(sample_md, target, pdf_engine="engine-inexistente")
