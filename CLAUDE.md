# context-mode — MANDATORY routing rules

You have context-mode MCP tools available. These rules are NOT optional — they protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## BLOCKED commands — do NOT attempt these

### curl / wget — BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error message. Do NOT retry.
Instead use:
- `ctx_fetch_and_index(url, source)` to fetch and index web pages
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` to run HTTP calls in sandbox

### Inline HTTP — BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, or `http.request(` is intercepted and replaced with an error message. Do NOT retry with Bash.
Instead use:
- `ctx_execute(language, code)` to run HTTP calls in sandbox — only stdout enters context

### WebFetch — BLOCKED
WebFetch calls are denied entirely. The URL is extracted and you are told to use `ctx_fetch_and_index` instead.
Instead use:
- `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` to query the indexed content

## REDIRECTED tools — use sandbox equivalents

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` — run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` — run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct (Edit needs content in context).
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead. Only your printed summary enters context. The raw file content stays in the sandbox.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox. Only your printed summary enters context.

## Tool selection hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` — Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` — Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` — Sandbox execution. Only stdout enters context.
4. **WEB**: `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` — Fetch, chunk, index, query. Raw HTML never enters context.
5. **INDEX**: `ctx_index(content, source)` — Store content in FTS5 knowledge base for later search.

## Subagent routing

When spawning subagents (Agent/Task tool), the routing block is automatically injected into their prompt. Bash-type subagents are upgraded to general-purpose so they have access to MCP tools. You do NOT need to manually instruct subagents about context-mode.

## Output constraints

- Keep responses under 500 words.
- Write artifacts (code, configs, PRDs) to FILES — never return them as inline text. Return only: file path + 1-line description.
- When indexing content, use descriptive source labels so others can `ctx_search(source: "label")` later.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call the `ctx_stats` MCP tool and display the full output verbatim |
| `ctx doctor` | Call the `ctx_doctor` MCP tool, run the returned shell command, display as checklist |
| `ctx upgrade` | Call the `ctx_upgrade` MCP tool, run the returned shell command, display as checklist |

---

# Projeto: Scanner de Imagens

App que recebe **fotografias de páginas de livros/artigos** e gera **Markdown estruturado** com export opcional para **DOCX**, preservando imagens e qualidade.

**Status atual**: greenfield — infraestrutura de memória/grafo montada, codificação ainda não iniciada.

## Stack

- Python 3.13
- **Motor de extração**: ✅ **Docling** (decisão aceita) — fonte clonada em `docling-main/docling-main/`
  - Backend principal para fotos: `docling/backend/image_backend.py`
  - Backend fallback para PDFs: `docling/backend/pypdfium2_backend.py`
  - OCR engine: a decidir (EasyOCR / Tesseract / RapidOCR)
  - Ver [[vault/projeto/decisoes#motor-extracao]] para detalhes
- API web futura: FastAPI
- Export DOCX: pandoc CLI ou python-docx (a decidir)

### Exceção à regra global de PDF

A regra `~/.claude/rules/pdf-extraction-default.md` define **opendataloader-pdf** como default — mas é PDF-only. Como o input deste projeto são **fotos**, usamos **Docling** como motor primário. OpenDataloader-PDF fica reservado para inputs em PDF já existentes (uso secundário/fallback).

## Context Navigation (3 camadas)

Antes de ler arquivos de código brutos, **consulte sempre nesta ordem**:

1. **Knowledge graph** (se existir): `graphify-out/graph.json`, `graphify-out/wiki/index.md`, `graphify-out/GRAPH_REPORT.md`
   - Contém estrutura, conexões e métricas do código sem precisar reler tudo.
   - Se ainda não existe, é porque o código ainda não foi escrito ou Graphify não rodou.
2. **Vault Obsidian**: `vault/`
   - `vault/projeto/decisoes.md` — log de decisões arquiteturais (ADR-style)
   - `vault/projeto/arquitetura.md` — visão geral da arquitetura
   - `vault/projeto/convencoes.md` — coding standards
   - `vault/logs/*.md` — session logs (últimos 3 dão o contexto recente)
   - `vault/chats/code/` e `vault/chats/web/` — chats anteriores indexados
3. **Arquivos de código brutos**: só leia quando vai **editar** ou quando as camadas anteriores não tiverem a resposta.

## Comandos custom

- `/retomar` — carrega contexto do vault no início da sessão. Ver `.claude/commands/retomar.md`.
- `/salvar` — gera session log no vault ao fim da sessão. Ver `.claude/commands/salvar.md`.

## Convenções Zettelkasten

Toda escrita em `vault/` segue Zettelkasten — wikilinks `[[nome]]`, frontmatter YAML, kebab-case nos nomes. Regras completas em `vault/CLAUDE.md`.

## Knowledge Graph (Graphify)

Quando houver código:

```powershell
graphify . --obsidian --obsidian-dir ".\vault\graphify"
graphify hook install   # depois de git init — reconstrói o grafo a cada commit
```

- Não modifique arquivos em `graphify-out/` ou `vault/graphify/` manualmente.
- Após mudanças estruturais (novos módulos, refactors), rode `graphify . --update`.
- Modo `--mode deep` consome tokens de LLM — só usar quando necessário; modo AST padrão custa **0 tokens**.

## Pipeline de importação de chats

Scripts em `scripts/`:
- `claude_to_obsidian.py` — pós-processador Python (frontmatter, tags, wikilinks)
- `sync_claude_obsidian.ps1` — automação PowerShell (Windows-native)

Staging area: `claude-exports/code/` e `claude-exports/web/` (gitignored).
Output processado: `vault/chats/code/` e `vault/chats/web/`.

## Estrutura do projeto

```
.
├── CLAUDE.md            # este arquivo
├── .claude/commands/    # /retomar, /salvar
├── vault/               # memória persistente (Obsidian)
├── scripts/             # automação Python + PowerShell
├── claude-exports/      # staging de chats (gitignored)
├── reports/             # relatórios de sessão (markdown)
└── (src/, graphify-out/ — quando houver código)
```
