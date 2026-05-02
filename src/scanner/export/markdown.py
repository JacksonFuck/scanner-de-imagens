"""Persistência do markdown extraído."""

from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)


def write_markdown(content: str, target: Path) -> Path:
    """Escreve o markdown em `target`, criando pastas pai se necessário.

    Returns:
        O `target` resolvido (path absoluto).
    """
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    log.info("Markdown gravado: %s (%d bytes)", target, len(content.encode("utf-8")))
    return target
