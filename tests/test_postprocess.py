"""Testes do pós-processador PT-BR.

Cobertura:
- fix_accents: dicionário básico, preservação de casing, cedilha
- fix_spaces_and_punct: espaço antes de pontuação removido sem afetar listas
- fix_zero_as_o: "0" no início de palavra vira "O"
- fix_text / process_markdown: pipeline completo preserva blocos de código
- merge_into_book: concatenação com sumário
"""

from __future__ import annotations

from pathlib import Path

from scanner.postprocess import (
    ACCENT_MAP,
    fix_accents,
    fix_spaces_and_punct,
    fix_text,
    fix_zero_as_o,
    merge_into_book,
    process_markdown,
)

# ---------------------------------------------------------------------------
# fix_accents
# ---------------------------------------------------------------------------


def test_fix_accents_replaces_common_words() -> None:
    """Palavras comuns sem acento devem ser corrigidas."""
    text = "A reducao e satisfacao em medico."
    result = fix_accents(text)
    assert "redução" in result
    assert "satisfação" in result
    assert "médico" in result


def test_fix_accents_preserves_casing_uppercase() -> None:
    """Casing UPPERCASE deve ser mantido na substituição."""
    text = "REDUCAO de custos"
    result = fix_accents(text)
    assert "REDUÇÃO" in result


def test_fix_accents_preserves_casing_titlecase() -> None:
    """Casing Titlecase deve ser mantido na substituição."""
    text = "Reducao de custos"
    result = fix_accents(text)
    assert "Redução" in result


def test_fix_accents_handles_words_with_diacritics() -> None:
    """Palavras com diacríticos (til, agudo) devem ser corrigidas."""
    text = "A reducao da saude e da atencao."
    result = fix_accents(text)
    # Estas três estão no ACCENT_MAP curado.
    assert "redução" in result
    assert "saúde" in result
    assert "atenção" in result


def test_fix_accents_does_not_touch_already_correct() -> None:
    """Palavras já corretas não devem ser alteradas."""
    text = "A função é boa."
    result = fix_accents(text)
    assert result == text


def test_accent_map_is_non_empty() -> None:
    """ACCENT_MAP deve ter o dicionário curado preservado."""
    # Garante que a migração não esvaziou o dicionário.
    assert len(ACCENT_MAP) > 100, "ACCENT_MAP perdeu entradas após migração"
    assert "satisfacao" in ACCENT_MAP
    assert ACCENT_MAP["satisfacao"] == "satisfação"


# ---------------------------------------------------------------------------
# fix_spaces_and_punct
# ---------------------------------------------------------------------------


def test_fix_spaces_and_punct_removes_space_before_comma() -> None:
    """Espaço antes de vírgula deve ser removido."""
    text = "palavra , outra"
    assert fix_spaces_and_punct(text) == "palavra, outra"


def test_fix_spaces_and_punct_removes_space_before_period() -> None:
    """Espaço antes de ponto final deve ser removido."""
    text = "fim da frase ."
    assert fix_spaces_and_punct(text) == "fim da frase."


def test_fix_spaces_and_punct_handles_multiple_punct() -> None:
    """Funciona para todos os pontos exceto ; antes de minúscula.

    Nota: ; seguido de minúscula é intencionalmente convertido para ',' por
    `_SEMICOLON_TO_COMMA` (heurística OCR — fontes antigas confundem).
    Aqui usamos ; antes de Maiúscula para isolar fix_spaces_and_punct.
    """
    text = "fim ; Sentenca seguinte : meio . pergunta ?"
    result = fix_spaces_and_punct(text)
    assert result == "fim; Sentenca seguinte: meio. pergunta?"


def test_fix_spaces_and_punct_converts_semicolon_to_comma_in_midsentence() -> None:
    """Heurística OCR: ; seguido de minúscula → ',' (sentence midflow)."""
    text = "primeira parte ; segunda parte"
    result = fix_spaces_and_punct(text)
    assert "," in result
    assert ";" not in result


def test_fix_spaces_and_punct_does_not_break_list_dashes() -> None:
    """Listas markdown ('- item') não devem ser afetadas."""
    text = "- item um\n- item dois"
    assert fix_spaces_and_punct(text) == text


# ---------------------------------------------------------------------------
# fix_zero_as_o
# ---------------------------------------------------------------------------


def test_fix_zero_as_o_replaces_when_followed_by_uppercase_word() -> None:
    """'0' vira 'O' apenas quando seguido de espaço + Maiúscula + minúscula.

    Padrão estrito (não dispara em '0 cm' ou números soltos).
    """
    text = "Frase: 0 Paciente atendido."
    result = fix_zero_as_o(text)
    assert "O Paciente" in result
    assert "0 Paciente" not in result


def test_fix_zero_as_o_does_not_touch_numbers() -> None:
    """'0' em números reais (sem padrão Maiúscula+minúscula seguinte) fica."""
    text = "Eram 0 cm de profundidade."
    result = fix_zero_as_o(text)
    assert result == text  # nada muda


# ---------------------------------------------------------------------------
# fix_text / process_markdown — pipeline completo
# ---------------------------------------------------------------------------


def test_fix_text_is_alias_of_process_markdown() -> None:
    """fix_text e process_markdown devem produzir o mesmo resultado."""
    text = "A reducao da atencao medica."
    assert fix_text(text) == process_markdown(text)


def test_fix_text_preserves_code_blocks() -> None:
    """Blocos de código ```...``` não devem ter palavras corrigidas."""
    text = "Antes:\n\n```python\ndef reducao():\n    pass\n```\n\nDepois reducao."
    result = fix_text(text)
    # O nome de função no bloco de código deve permanecer intocado
    assert "def reducao()" in result
    # Mas a palavra fora do bloco deve ser corrigida
    assert "Depois redução." in result


def test_fix_text_applies_all_steps() -> None:
    """fix_text aplica accents + spaces + zero-as-O combinadamente."""
    text = "A reducao da atencao ."
    result = fix_text(text)
    assert "redução" in result
    assert "atenção" in result
    assert "atenção." in result  # espaço antes do ponto removido


# ---------------------------------------------------------------------------
# merge_into_book
# ---------------------------------------------------------------------------


def test_merge_into_book_creates_consolidated_file(tmp_path: Path) -> None:
    """merge_into_book deve criar um arquivo único com sumário e seções."""
    md1 = tmp_path / "pagina-1.md"
    md1.write_text("# Página 1\n\nConteúdo da primeira página.", encoding="utf-8")
    md2 = tmp_path / "pagina-2.md"
    md2.write_text("# Página 2\n\nConteúdo da segunda página.", encoding="utf-8")

    target = tmp_path / "book.md"
    result = merge_into_book([md1, md2], target, title="Livro Teste")

    assert result == target
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "# Livro Teste" in content
    assert "## Sumário" in content
    assert "pagina-1" in content
    assert "pagina-2" in content
    assert "Conteúdo da primeira página" in content
    assert "Conteúdo da segunda página" in content
