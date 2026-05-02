"""Testes do orquestrador — focam validação e tratamento de erro.

Não carregam Docling: usam apenas as funções que validam paths e formatos.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scanner.errors import InvalidInputError
from scanner.pipeline import OutputFormat, ScanRequest, collect_inputs


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
