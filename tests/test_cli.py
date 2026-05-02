"""Testes da CLI — usam `typer.testing.CliRunner` (não chamam Docling)."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from scanner import __version__
from scanner.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_no_args_mostra_help() -> None:
    result = runner.invoke(app, [])
    # no_args_is_help=True faz Typer retornar exit 2 e mostrar help
    assert result.exit_code in (0, 2)
    assert "scanner" in result.stdout.lower() or "scanner" in result.output.lower()


def test_convert_arquivo_inexistente(tmp_path: Path) -> None:
    """Typer valida `exists=True` antes de chamar nosso código."""
    result = runner.invoke(app, ["convert", str(tmp_path / "fantasma.jpg")])
    assert result.exit_code != 0


def test_convert_pasta_vazia(tmp_path: Path) -> None:
    """Pasta sem arquivos suportados → erro nosso (exit 2)."""
    empty = tmp_path / "empty"
    empty.mkdir()
    result = runner.invoke(app, ["convert", str(empty), "-o", str(tmp_path / "out")])
    # Pasta existe mas não tem arquivos suportados
    assert result.exit_code == 2


@pytest.mark.parametrize("fmt", ["md", "docx", "both"])
def test_help_aceita_formatos_validos(fmt: str) -> None:
    """Sanity: enum OutputFormat aceita os 3 valores documentados."""
    from scanner.pipeline import OutputFormat

    OutputFormat(fmt)  # não levanta
