#!/usr/bin/env python3
"""
claude_to_obsidian.py
=====================
Pipeline de pós-processamento de chats exportados do Claude Code/Web.

Lê arquivos .md em <export-dir>/code/ e <export-dir>/web/, adiciona frontmatter
YAML padronizado, gera tags automáticas a partir de keywords, insere wikilinks
para notas que já existem em <vault>/permanent/, e move o resultado para
<vault>/chats/code/ ou <vault>/chats/web/.

Uso:
    python claude_to_obsidian.py --export-dir EXPORTS --vault-dir VAULT [--move]

Idempotente: arquivos que já tenham frontmatter `type: chat` são ignorados.
Compatível com Windows + UTF-8.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

# Mapeia substrings (lowercase) → tag Obsidian.
# Adapte conforme o vocabulário do seu projeto.
KEYWORD_TAG_MAP: dict[str, str] = {
    # Stack do projeto Scanner de Imagens
    "docling": "docling",
    "opendataloader": "opendataloader",
    "ocr": "ocr",
    "tesseract": "tesseract",
    "pdf": "pdf",
    "docx": "docx",
    "markdown": "markdown",
    "scanner": "scanner",
    "pillow": "pillow",
    "opencv": "opencv",
    "fastapi": "fastapi",
    # Conceitos gerais
    "python": "python",
    "deploy": "deploy",
    "bug": "debugging",
    "refactor": "refactoring",
    "obsidian": "obsidian",
    "graphify": "graphify",
    "git": "git",
    "windows": "windows",
    "powershell": "powershell",
}

# Tag aplicada a TODO chat importado, para fácil filtragem.
COMMON_TAG = "chat-import"

# Limite de tags geradas automaticamente (evita poluição).
MAX_AUTO_TAGS = 6

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]")

# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------


@dataclass
class ChatFile:
    src: Path
    source: str  # "code" | "web"
    title: str
    body: str  # corpo SEM frontmatter pré-existente
    has_existing_chat_frontmatter: bool


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def detect_source(path: Path, export_dir: Path) -> str:
    """Determina origem ('code' ou 'web') pela posição relativa do arquivo."""
    try:
        rel = path.relative_to(export_dir)
        first_part = rel.parts[0].lower() if rel.parts else ""
        if first_part in ("code", "web"):
            return first_part
    except ValueError:
        pass
    # Fallback: assume 'code' (claude-extract joga aqui por padrão)
    return "code"


def slugify(text: str) -> str:
    """Converte um título arbitrário em kebab-case ASCII-safe."""
    text = text.strip().lower()
    # Remove caracteres não-alfanuméricos exceto hífen
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text or "chat-sem-titulo"


def extract_title(body: str, fallback: str) -> str:
    """Pega o primeiro heading H1 do markdown, ou usa o fallback."""
    for line in body.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return m.group(1).strip()
    return fallback


def parse_chat(path: Path, export_dir: Path) -> ChatFile:
    """Lê o arquivo, separa frontmatter pré-existente (se houver), captura título."""
    raw = path.read_text(encoding="utf-8", errors="replace")

    has_chat_fm = False
    body = raw
    m = FRONTMATTER_RE.match(raw)
    if m:
        existing = m.group(1)
        if "type: chat" in existing or "type:chat" in existing:
            has_chat_fm = True
        body = raw[m.end() :]

    fallback_title = path.stem.replace("_", " ").replace("-", " ").strip()
    title = extract_title(body, fallback_title)
    source = detect_source(path, export_dir)

    return ChatFile(
        src=path,
        source=source,
        title=title,
        body=body,
        has_existing_chat_frontmatter=has_chat_fm,
    )


# ---------------------------------------------------------------------------
# Enriquecimento
# ---------------------------------------------------------------------------


def auto_tags(text: str) -> list[str]:
    """Retorna tags inferidas pelo conteúdo (case-insensitive, dedup, ordem estável)."""
    lower = text.lower()
    found: list[str] = []
    seen: set[str] = set()
    for keyword, tag in KEYWORD_TAG_MAP.items():
        if keyword in lower and tag not in seen:
            seen.add(tag)
            found.append(tag)
            if len(found) >= MAX_AUTO_TAGS:
                break
    return found


def list_permanent_titles(vault_dir: Path) -> list[str]:
    """Lista títulos das notas em vault/permanent/ (sem extensão)."""
    permanent = vault_dir / "permanent"
    if not permanent.is_dir():
        return []
    return [p.stem for p in permanent.glob("*.md") if p.is_file()]


def inject_wikilinks(body: str, candidates: list[str]) -> str:
    """Substitui ocorrências de títulos por wikilinks, preservando casing original.

    Estratégia conservadora: só injeta no PRIMEIRO match de cada título no corpo,
    fora de blocos de código e wikilinks já existentes.
    """
    if not candidates:
        return body

    # Normaliza candidatos por tamanho (longos primeiro, evita match parcial)
    candidates_sorted = sorted(set(candidates), key=len, reverse=True)
    already_linked: set[str] = set(m.lower() for m in WIKILINK_RE.findall(body))

    lines = body.split("\n")
    in_code = False
    used: set[str] = set()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        for cand in candidates_sorted:
            if cand.lower() in already_linked or cand.lower() in used:
                continue
            # Match palavra-completa, case-insensitive
            pattern = re.compile(r"\b" + re.escape(cand) + r"\b", re.IGNORECASE)
            if pattern.search(line):
                lines[i] = pattern.sub(f"[[{cand}]]", line, count=1)
                used.add(cand.lower())
                break  # um match por linha basta

    return "\n".join(lines)


def build_frontmatter(chat: ChatFile, tags: list[str]) -> str:
    """Gera frontmatter YAML padronizado. Sem dependência de pyyaml."""
    today = datetime.now().strftime("%Y-%m-%d")
    src_mtime = datetime.fromtimestamp(chat.src.stat().st_mtime).strftime("%Y-%m-%d")
    safe_title = chat.title.replace('"', '\\"')

    all_tags = [COMMON_TAG] + tags
    # YAML inline list
    tags_yaml = "[" + ", ".join(all_tags) + "]"

    return (
        "---\n"
        f'title: "{safe_title}"\n'
        f"tags: {tags_yaml}\n"
        f"created: {src_mtime}\n"
        f"updated: {today}\n"
        f"source: claude-{chat.source}\n"
        f"imported: {today}\n"
        "type: chat\n"
        "status: imported\n"
        "---\n\n"
    )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def process_file(chat: ChatFile, vault_dir: Path, move: bool) -> Path | None:
    """Processa um chat. Retorna o path final no vault, ou None se pulado."""
    if chat.has_existing_chat_frontmatter:
        print(f"[skip] já processado: {chat.src.name}", file=sys.stderr)
        return None

    permanent_titles = list_permanent_titles(vault_dir)
    enriched_body = inject_wikilinks(chat.body, permanent_titles)
    tags = auto_tags(chat.body)
    frontmatter = build_frontmatter(chat, tags)

    final = frontmatter + enriched_body.lstrip("\n")

    target_dir = vault_dir / "chats" / chat.source
    target_dir.mkdir(parents=True, exist_ok=True)

    # Nome de destino: data + slug do título, evita conflito
    date_prefix = datetime.fromtimestamp(chat.src.stat().st_mtime).strftime("%Y-%m-%d")
    slug = slugify(chat.title)
    target = target_dir / f"{date_prefix}-{slug}.md"
    counter = 2
    while target.exists():
        target = target_dir / f"{date_prefix}-{slug}-{counter}.md"
        counter += 1

    target.write_text(final, encoding="utf-8")

    if move:
        try:
            chat.src.unlink()
        except OSError as exc:
            print(f"[warn] não consegui remover {chat.src}: {exc}", file=sys.stderr)

    return target


def collect_inputs(export_dir: Path) -> list[Path]:
    """Coleta .md em export_dir/code/ e export_dir/web/."""
    inputs: list[Path] = []
    for sub in ("code", "web"):
        d = export_dir / sub
        if d.is_dir():
            inputs.extend(p for p in d.glob("*.md") if p.is_file())
    return inputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa chats do Claude para o vault Obsidian.")
    parser.add_argument("--export-dir", required=True, type=Path, help="Diretório com code/ e web/")
    parser.add_argument("--vault-dir", required=True, type=Path, help="Raiz do vault Obsidian")
    parser.add_argument("--move", action="store_true", help="Remove originais após processar")
    parser.add_argument("--dry-run", action="store_true", help="Apenas lista o que seria feito")
    args = parser.parse_args()

    export_dir: Path = args.export_dir.resolve()
    vault_dir: Path = args.vault_dir.resolve()

    if not export_dir.is_dir():
        print(f"[error] export-dir não existe: {export_dir}", file=sys.stderr)
        return 2
    if not vault_dir.is_dir():
        print(f"[error] vault-dir não existe: {vault_dir}", file=sys.stderr)
        return 2

    inputs = collect_inputs(export_dir)
    if not inputs:
        print(f"[info] nenhum .md em {export_dir}/(code|web)")
        return 0

    print(f"[info] {len(inputs)} arquivo(s) candidato(s)")

    processed = 0
    skipped = 0
    for path in inputs:
        chat = parse_chat(path, export_dir)
        if args.dry_run:
            print(f"[dry] {path.name} → chats/{chat.source}/  (title='{chat.title}')")
            continue
        result = process_file(chat, vault_dir, move=args.move)
        if result:
            processed += 1
            print(f"[ok]   {path.name} → {result.relative_to(vault_dir)}")
        else:
            skipped += 1

    print(f"[done] processados={processed} pulados={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
