---
title: 2026-05-02 — Bootstrap do MVP (infra + app)
tags: [log, sessao, scanner, docling, mvp]
created: 2026-05-02
updated: 2026-05-02
status: closed
type: log
---

# 2026-05-02 — Bootstrap do MVP (infra + app)

## Objetivo da sessão

Implementar o setup completo do guia "Claude Code + Obsidian + Graphify" e construir o MVP do app de scanner usando Docling.

## O que foi feito

### Fase 1 — Infraestrutura (memória + grafo)
- Estrutura `vault/` Zettelkasten criada (permanent, inbox, fleeting, templates, logs, references, projeto, pipeline, dados, features, chats, graphify)
- `vault/CLAUDE.md` — regras Zettelkasten para o Claude Code
- `vault/templates/nota-padrao.md` — template padrão
- `vault/projeto/{arquitetura,decisoes,convencoes}.md` — MOCs do projeto
- `.claude/commands/{retomar,salvar}.md` — slash commands custom (já visíveis no skill list)
- `scripts/claude_to_obsidian.py` + `scripts/sync_claude_obsidian.ps1` — pipeline de import de chats
- `CLAUDE.md` raiz extendido com Context Navigation + stack
- `.gitignore` completo (Graphify cache, Obsidian workspace, claude-exports, docling-main, Python deps)
- `graphifyy v0.6.2` e `claude-conversation-extractor v1.1.2` instalados
- Skill `graphify` registrado em `~/.claude/skills/graphify/`

### Fase 2 — App MVP (src/scanner/)
- `pyproject.toml` com hatchling + dependências (docling, typer, rich, pillow, pypandoc, dev: pytest+ruff+mypy)
- Package `src/scanner/`:
  - `__init__.py` — version + API pública
  - `__main__.py` — `python -m scanner`
  - `errors.py` — hierarquia ScannerError → InvalidInputError, ConversionError, ConfigurationError
  - `engine/docling_engine.py` — adapter sobre `DocumentConverter` (import tardio, validação de extensão, ImageRefMode.REFERENCED)
  - `export/markdown.py` — escreve `.md` UTF-8
  - `export/docx.py` — MD→DOCX via pypandoc (auto-download de pandoc se faltar)
  - `pipeline.py` — `scan()`, `scan_batch()`, `collect_inputs()`, `OutputFormat (StrEnum)`, `ScanRequest`, `ScanResult`, `BatchResult`
  - `cli.py` — Typer + Rich, comando `convert`, flags `--format`, `--no-ocr`, `--no-tables`, `-v`
- `tests/` — 29 testes unitários (CLI, pipeline, engine validação) + 1 smoke test slow para Docling real
- `README.md` com instalação, uso CLI/API, arquitetura
- `.python-version`

## Decisões tomadas

- **Docling release vs editable**: release (`pip install docling`). Source clonada em `docling-main/` fica como referência. Registrado em [[../projeto/decisoes#stack-mvp]].
- **OCR engine**: EasyOCR (default Docling, bom em PT, sem instalação binária extra).
- **DOCX**: pypandoc + pandoc CLI (preserva imagens via passagem MD→DOCX).
- **Storage**: filesystem com pasta `<base>-images/` sibling do `.md`. MinIO é overkill no MVP.
- **Múltiplos Pythons no PATH**: workaround com path explícito ao scoop python; recomendar venv dedicado para uso. Ver [[../projeto/decisoes#multiplos-pythons]].

## Arquivos modificados / criados

### Vault
- [[../projeto/arquitetura]]
- [[../projeto/decisoes]] (nova decisão #stack-mvp e #multiplos-pythons)
- [[../projeto/convencoes]]
- [[../CLAUDE]]

### App
- `pyproject.toml`
- `src/scanner/__init__.py`, `__main__.py`, `errors.py`, `cli.py`, `pipeline.py`
- `src/scanner/engine/__init__.py`, `engine/docling_engine.py`
- `src/scanner/export/__init__.py`, `export/markdown.py`, `export/docx.py`
- `tests/conftest.py`, `tests/test_cli.py`, `tests/test_pipeline.py`, `tests/test_engine.py`
- `README.md`, `.python-version`, `.gitignore`

### Infra
- `CLAUDE.md` (raiz) — extendido
- `.claude/commands/retomar.md`, `.claude/commands/salvar.md`
- `scripts/claude_to_obsidian.py`, `scripts/sync_claude_obsidian.ps1`

## Resultados de validação

- ✅ `python -m scanner --version` → `scanner 0.1.0`
- ✅ `python -m scanner convert --help` → ajuda renderizada com Typer+Rich
- ✅ `pytest -q` → 29 passed, 1 skipped (Docling não instalado)
- ✅ `ruff check src tests` → All checks passed

## Pendências / próximos passos

- [ ] Instalar Docling completo (~3-5 GB): `pip install docling`
- [ ] Testar com foto real de página de livro em português
- [ ] Rodar `graphify . --obsidian --obsidian-dir .\vault\graphify` agora que tem código
- [ ] git init + primeiro commit
- [ ] Avaliar pré-processamento (deskew, dewarp) antes do Docling para fotos com curvatura

## Links

- [[../projeto/decisoes]]
- [[../projeto/arquitetura]]
- [[../CLAUDE]]
- [[../../reports/leia-o-texto-abaixo-joyful-bubble]] (plano de implementação)

## Comandos úteis para a próxima sessão

```powershell
# ativar venv (recomendado)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pip install docling   # ~3-5 GB

# testes
python -m pytest -q

# CLI
python -m scanner convert ./pagina.jpg -o ./output -f both -v

# graphify
graphify . --obsidian --obsidian-dir .\vault\graphify
```
