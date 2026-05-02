"""Testes do orquestrador — focam validação e tratamento de erro.

Não carregam Docling: usam apenas as funções que validam paths e formatos.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest

from scanner.errors import InvalidInputError
from scanner.pipeline import OutputFormat, ScanRequest, collect_inputs, formats_for


class TestCollectInputs:
    def test_arquivo_unico_retorna_lista_de_um(self, fake_image_file: Path) -> None:
        result = collect_inputs(fake_image_file)
        assert result == [fake_image_file.resolve()]

    def test_pasta_filtra_extensoes_suportadas(self, tmp_path: Path) -> None:
        (tmp_path / "valida.jpg").write_bytes(b"\xff\xd8")
        (tmp_path / "valida.png").write_bytes(b"\x89PNG")
        (tmp_path / "ignorada.txt").write_text("texto")
        (tmp_path / "ignorada.docx").write_bytes(b"PK")

        result = collect_inputs(tmp_path)
        names = sorted(p.name for p in result)
        assert names == ["valida.jpg", "valida.png"]

    def test_pasta_vazia_lanca_erro(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()
        with pytest.raises(InvalidInputError, match="Nenhum arquivo suportado"):
            collect_inputs(empty)

    def test_caminho_inexistente_lanca_erro(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidInputError, match="não existe"):
            collect_inputs(tmp_path / "fantasma")

    def test_pasta_ordena_arquivos(self, tmp_path: Path) -> None:
        (tmp_path / "z.jpg").write_bytes(b"")
        (tmp_path / "a.jpg").write_bytes(b"")
        (tmp_path / "m.jpg").write_bytes(b"")

        result = collect_inputs(tmp_path)
        assert [p.name for p in result] == ["a.jpg", "m.jpg", "z.jpg"]


class TestScanRequest:
    def test_default_format_md(self, fake_image_file: Path, tmp_output_dir: Path) -> None:
        req = ScanRequest(source=fake_image_file, output_dir=tmp_output_dir)
        assert req.formats == OutputFormat.MD
        assert req.do_ocr is True

    def test_pode_desabilitar_ocr(self, fake_image_file: Path, tmp_output_dir: Path) -> None:
        req = ScanRequest(source=fake_image_file, output_dir=tmp_output_dir, do_ocr=False)
        assert req.do_ocr is False


class TestOutputFormat:
    """Cobertura do enum estendido (PDF, ALL) + alias deprecated (BOTH)."""

    def test_enum_has_pdf_and_all(self) -> None:
        """Novos valores PDF e ALL devem existir no enum."""
        assert OutputFormat.PDF.value == "pdf"
        assert OutputFormat.ALL.value == "all"

    def test_enum_keeps_legacy_both_alias(self) -> None:
        """BOTH continua existindo (alias temporário) durante a janela de deprecation."""
        assert OutputFormat.BOTH.value == "both"

    def test_formats_for_md_only(self) -> None:
        """OutputFormat.MD produz apenas o intermediário Markdown."""
        assert formats_for(OutputFormat.MD) == frozenset({"md"})

    def test_formats_for_docx_includes_md(self) -> None:
        """OutputFormat.DOCX produz MD + DOCX (MD é intermediário do Docling)."""
        assert formats_for(OutputFormat.DOCX) == frozenset({"md", "docx"})

    def test_formats_for_pdf_includes_md(self) -> None:
        """OutputFormat.PDF produz MD + PDF (sem DOCX)."""
        assert formats_for(OutputFormat.PDF) == frozenset({"md", "pdf"})

    def test_formats_for_all_includes_three(self) -> None:
        """OutputFormat.ALL produz os 3 formatos."""
        assert formats_for(OutputFormat.ALL) == frozenset({"md", "docx", "pdf"})

    def test_formats_for_both_emits_deprecation_warning(self) -> None:
        """OutputFormat.BOTH emite DeprecationWarning ao ser resolvido."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            formats_for(OutputFormat.BOTH)
        assert any(
            issubclass(w.category, DeprecationWarning) and "BOTH" in str(w.message)
            for w in caught
        ), "Esperado DeprecationWarning ao resolver OutputFormat.BOTH"

    def test_formats_for_both_is_alias_of_all(self) -> None:
        """BOTH e ALL produzem o mesmo conjunto de formatos."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            assert formats_for(OutputFormat.BOTH) == formats_for(OutputFormat.ALL)
