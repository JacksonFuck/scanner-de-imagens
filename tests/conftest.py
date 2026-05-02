"""Fixtures comuns aos testes.

Estratégia: a maior parte dos testes não toca o Docling (importa caro).
Quando precisamos do engine, usamos fixture `docling_engine` que é session-scoped.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Pasta de saída isolada por teste."""
    out = tmp_path / "output"
    out.mkdir()
    return out


@pytest.fixture
def fake_image_file(tmp_path: Path) -> Path:
    """Cria um arquivo .jpg falso (apenas extensão correta — não é imagem real).

    Útil para testar validações que só olham extensão/existência.
    """
    f = tmp_path / "fake.jpg"
    f.write_bytes(b"\xff\xd8\xff\xe0")  # magic bytes JPEG
    return f


@pytest.fixture(scope="session")
def docling_engine():
    """Engine Docling real — pula gracefully se Docling não está instalado."""
    pytest.importorskip("docling", reason="Docling não instalado — pule com pytest -m 'not slow'")
    from scanner.engine import DoclingEngine

    return DoclingEngine(do_ocr=True)
