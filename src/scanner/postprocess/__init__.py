"""Pós-processamento de Markdown extraído pelo OCR.

Corrige problemas conhecidos do OCR sem PT-BR ativo:
- Palavras comuns sem acento → com acento (dicionário ACCENT_MAP)
- Espaços extras antes de pontuação ASCII (.,;:!?)
- "0" no início de palavra → "O" (artigo confundido em fontes antigas)

API pública:
    fix_text(text) -> text         # aplica todas as correções (alias de process_markdown)
    fix_accents(text) -> text
    fix_spaces_and_punct(text) -> text
    fix_zero_as_o(text) -> text
    process_markdown(text) -> text
    merge_into_book(md_paths, target, *, title) -> Path
"""

from __future__ import annotations

from scanner.postprocess.ptbr import (
    ACCENT_MAP,
    fix_accents,
    fix_spaces_and_punct,
    fix_text,
    fix_zero_as_o,
    merge_into_book,
    process_markdown,
)

__all__ = [
    "ACCENT_MAP",
    "fix_accents",
    "fix_spaces_and_punct",
    "fix_text",
    "fix_zero_as_o",
    "merge_into_book",
    "process_markdown",
]
