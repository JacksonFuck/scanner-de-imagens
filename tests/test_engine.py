"""Testes do engine — validações puras (não carregam Docling)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scanner.engine.docling_engine import SUPPORTED_EXTENSIONS, DoclingEngine
from scanner.errors import InvalidInputError


class TestValidateSource:
    """`_validate_source` é estático — testa sem instanciar engine."""

    def test_arquivo_inexistente(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidInputError, match="não encontrado"):
            DoclingEngine._validate_source(tmp_path / "fantasma.jpg")

    def test_pasta_em_vez_de_arquivo(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidInputError, match="Não é arquivo"):
            DoclingEngine._validate_source(tmp_path)

    @pytest.mark.parametrize("ext", [".txt", ".docx", ".html", ".zip", ""])
    def test_extensao_nao_suportada(self, tmp_path: Path, ext: str) -> None:
        f = tmp_path / f"arquivo{ext}"
        f.write_bytes(b"dummy")
        with pytest.raises(InvalidInputError, match="Formato não suportado"):
            DoclingEngine._validate_source(f)

    @pytest.mark.parametrize("ext", [".jpg", ".jpeg", ".png", ".pdf", ".tif", ".webp"])
    def test_extensoes_suportadas_passam(self, tmp_path: Path, ext: str) -> None:
        f = tmp_path / f"arquivo{ext}"
        f.write_bytes(b"dummy")
        # Não deve levantar
        DoclingEngine._validate_source(f)

    def test_extensao_case_insensitive(self, tmp_path: Path) -> None:
        f = tmp_path / "ARQUIVO.JPG"
        f.write_bytes(b"dummy")
        DoclingEngine._validate_source(f)


def test_supported_extensions_inclui_pdf_e_imagens() -> None:
    """Sanity check do conjunto de formatos."""
    assert ".jpg" in SUPPORTED_EXTENSIONS
    assert ".png" in SUPPORTED_EXTENSIONS
    assert ".pdf" in SUPPORTED_EXTENSIONS
    assert ".docx" not in SUPPORTED_EXTENSIONS  # docx é OUTPUT, não input


@pytest.mark.slow
class TestDoclingRealRun:
    """Testes que carregam Docling — só rodam com `pytest -m slow`."""

    def test_init_engine(self, docling_engine) -> None:  # type: ignore[no-untyped-def]
        assert docling_engine is not None
