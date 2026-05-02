"""Helper privado de localização do pandoc.

Compartilhado por `export/docx.py` e `export/pdf.py` — evita duplicar a lógica
de discovery (PATH → cache pypandoc → path Windows → auto-download).

A função era originalmente `_ensure_pandoc()` em docx.py; ao adicionar PDF
export (Fase 0 Task 3) extraímos para esta camada interna do pacote.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from scanner.errors import ConfigurationError

log = logging.getLogger(__name__)


def ensure_pandoc() -> str:
    """Garante que pandoc está disponível e retorna o path/binário a usar.

    Ordem de busca:
    1. PATH do shell (`shutil.which`) — pandoc instalado pelo usuário
    2. Cache do pypandoc (`pypandoc.get_pandoc_path`) — auto-download anterior
    3. Caminho conhecido do Windows (`~/AppData/Local/Pandoc/pandoc.exe`)
    4. Auto-download como último recurso

    Sem o cache lookup (passos 2-3), o passo 4 dispara em toda chamada e
    GitHub retorna 403 (rate limit) — bug histórico corrigido em commit 9fd4d0c.

    Returns:
        Path absoluto do pandoc OU a string "pandoc" se estiver no PATH.

    Raises:
        ConfigurationError: pypandoc ausente OU auto-download falhou.
    """
    if shutil.which("pandoc"):
        return "pandoc"

    try:
        import pypandoc  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ConfigurationError("pypandoc não instalado.") from exc

    # Tenta usar pandoc baixado anteriormente pelo pypandoc
    try:
        cached = pypandoc.get_pandoc_path()
        if cached and Path(cached).exists():
            log.debug("pandoc cacheado encontrado: %s", cached)
            return str(cached)
    except OSError:
        pass  # pypandoc lança OSError se nunca baixou

    # Fallback explícito ao path padrão do Windows
    win_default = Path.home() / "AppData" / "Local" / "Pandoc" / "pandoc.exe"
    if win_default.exists():
        log.debug("pandoc encontrado em %s", win_default)
        return str(win_default)

    log.warning("pandoc não encontrado em PATH/cache — fazendo download via pypandoc")
    try:
        pypandoc.download_pandoc()
    except Exception as exc:
        raise ConfigurationError(
            "Falha ao baixar pandoc automaticamente. "
            "Instale manualmente: https://pandoc.org/installing.html"
        ) from exc
    return "pandoc"
