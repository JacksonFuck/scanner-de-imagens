"""Persistência do markdown extraído."""

from __future__ import annotations

import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

# Matches a markdown image link `![alt](URL)`. Greedy `[^\n]+` + `\)`
# backtracks so embedded `)` characters stay inside the URL when the line
# ends with a paren — necessary for filenames like `... (1).png`.
_IMAGE_LINK_RE = re.compile(r"!\[([^\]]*)\]\(([^\n]+)\)")


def _wrap_image_urls(content: str) -> str:
    """Wrap image URLs in angle brackets so pandoc handles spaces and parens.

    Docling emits image refs with raw filename stems, so URLs may contain
    runs of spaces (collapsed by pandoc's URL parser) and parens (which
    terminate the URL early or trigger ambiguity). CommonMark's angle
    bracket form `<URL>` allows any character except `>` and newlines, and
    pandoc preserves the whole URL verbatim. Idempotent: skips URLs that
    are already wrapped.
    """

    def repl(m: re.Match[str]) -> str:
        alt, url = m.group(1), m.group(2)
        if url.startswith("<") and url.endswith(">"):
            return m.group(0)
        return f"![{alt}](<{url}>)"

    return _IMAGE_LINK_RE.sub(repl, content)


def write_markdown(content: str, target: Path) -> Path:
    """Escreve o markdown em `target`, criando pastas pai se necessário.

    Image URLs são embrulhadas em `<...>` para sobreviverem à exportação
    pandoc → DOCX/PDF quando os nomes de arquivos contêm espaços ou parens.

    Returns:
        O `target` resolvido (path absoluto).
    """
    content = _wrap_image_urls(content)
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    log.info("Markdown gravado: %s (%d bytes)", target, len(content.encode("utf-8")))
    return target
