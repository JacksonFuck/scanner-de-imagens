# Scanner de Imagens — Handoff

> Documento de transferência de contexto. Cobre tudo que foi construído, decisões tomadas, como rodar, como evoluir, e onde achar o quê.

**Última atualização**: 2026-05-02 (post-Phase 1B)
**Versão atual**: scanner 0.1.0 + scanner-api 0.1.0
**Status**: MVP CLI funcional + Backend FastAPI completo (sem frontend ainda)
**Repositório**: https://github.com/JacksonFuck/scanner-de-imagens

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Arquitetura](#2-arquitetura)
3. [Estrutura do monorepo](#3-estrutura-do-monorepo)
4. [Stack tecnológica](#4-stack-tecnológica)
5. [Instalação do zero](#5-instalação-do-zero)
6. [CLI — uso e features](#6-cli--uso-e-features)
7. [Backend FastAPI — endpoints e features](#7-backend-fastapi--endpoints-e-features)
8. [Pós-processador de PT-BR](#8-pós-processador-de-pt-br)
9. [Testes](#9-testes)
10. [Performance medida](#10-performance-medida)
11. [Decisões arquiteturais](#11-decisões-arquiteturais)
12. [Memória persistente do projeto (Vault + Graphify)](#12-memória-persistente-do-projeto-vault--graphify)
13. [Troubleshooting](#13-troubleshooting)
14. [Histórico de fases](#14-histórico-de-fases)
15. [O que falta (TODO)](#15-o-que-falta-todo)

---

## 1. Visão geral

**Scanner de Imagens** é um sistema Python que recebe **fotografias de páginas de livros, artigos ou documentos** e gera saída estruturada em **Markdown**, **DOCX** e **PDF**, preservando texto, tabelas, layout e imagens embutidas.

Hoje o sistema tem dois pontos de entrada:
- **CLI** (`python -m scanner convert ...`) — para uso local
- **API REST + WebSocket** (`uvicorn scanner_api.main:app`) — para integração web (frontend Phase 2 vai consumir daqui)

### Casos de uso reais validados
- 69 fotos de jornal antigo digitalizado em batch — `~9 min` com GPU RTX 3060
- Páginas com tabelas complexas (TableFormer detecta colspan/rowspan)
- Texto em PT-BR com acentuação correta (EasyOCR `lang=['pt','en']`)
- Pós-processador corrige acentos perdidos em OCR antigo (~150 palavras curadas)

### Diferenciais
- **OCR de qualidade**: Docling 2.92 + EasyOCR/Tesseract com `force_full_page_ocr=True`
- **Detecção de tabelas**: TableFormer preserva colspan/rowspan
- **GPU acceleration**: 7x mais rápido que CPU (5s vs 35s por foto, RTX 3060)
- **Modos de saída**: arquivos separados ou livro consolidado (`--merge`)
- **Worker isolado**: ProcessPoolExecutor evita que crashes do OCR derrubem a API
- **WebSocket de progresso**: `.progress.jsonl` apêndice + tail async + broadcast
- **Path traversal protection**: download seguro com validação `relative_to(base)`

---

## 2. Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│  CLI (Typer + Rich)              scanner.cli                    │ apresentação local
├─────────────────────────────────────────────────────────────────┤
│  HTTP API (FastAPI)              scanner_api.routes.*           │ apresentação web
│    GET /api/health  •  POST /api/jobs  •  GET /api/jobs[/{id}]  │
│    GET /api/jobs/{id}/files/{name}                              │
│  WebSocket                       scanner_api.routes.ws          │
│    WS /ws/jobs/{id}                                             │
├─────────────────────────────────────────────────────────────────┤
│  Worker pool (ProcessPool)       scanner_api.workers.pool       │ execução assíncrona
│    └─ subprocess: worker_main → scanner.scan_batch()            │
│  Progress broker                 scanner_api.progress           │
│    └─ tail .progress.jsonl + asyncio.Event                      │
├─────────────────────────────────────────────────────────────────┤
│  Pipeline (orquestrador)         scanner.pipeline               │ negócio
│  Engine adapter                  scanner.engine.docling_engine  │
│  Exporters (md, docx, pdf)       scanner.export.*               │
│  Pós-processador PT-BR           scanner.postprocess            │
├─────────────────────────────────────────────────────────────────┤
│  Settings (Pydantic)             scanner_api.settings           │ infra
│  Storage (paths/dirs)            scanner_api.storage            │
│  ORM (SQLAlchemy 2 + Alembic)    scanner_api.db.models          │
│  Errors                          scanner.errors                 │
└─────────────────────────────────────────────────────────────────┘
```

### Fluxo de uma conversão via API

```
1. Cliente faz POST /api/jobs com fotos (multipart)
2. API salva inputs em /data/jobs/{id}/inputs/ (aiofiles, 1MB chunks)
3. API grava Job + JobFile no SQLite
4. API cria WorkerJobSpec e empurra na asyncio.Queue
5. API retorna 201 + {job_id, status:'queued'} (sem aguardar processamento)
6. Cliente conecta WS /ws/jobs/{id}
7. Worker subprocess (ProcessPoolExecutor) consome o spec
   ├── Carrega Docling 1x (~5s, cache no subprocess)
   ├── scanner.scan_batch() → MD + DOCX + PDF + imagens extraídas
   └── Apêndice em .progress.jsonl: {started, progress×N, done}
8. ProgressBroker faz tail do .progress.jsonl + envia ao WS
9. Cliente baixa via GET /api/jobs/{id}/files/{filename}
```

---

## 3. Estrutura do monorepo

```
.
├── README.md                   # README curto, aponta para este HANDOFF
├── HANDOFF.md (este arquivo)   # Documento âncora
├── TODO.md                     # O que falta fazer (próximas fases)
├── CLAUDE.md                   # Regras context-mode + Context Navigation
├── pyproject.toml              # Pacote `scanner` (CLI core)
├── .python-version             # 3.13 (Windows: scoop python 3.14 também funciona)
├── .gitignore                  # Excluir cache, output, samples grandes
│
├── src/scanner/                # === PACOTE CORE: scanner ===
│   ├── __init__.py             # version + API pública
│   ├── __main__.py             # python -m scanner
│   ├── cli.py                  # Typer CLI (convert, --device, --format, --merge)
│   ├── pipeline.py             # scan(), scan_batch(), merge_results(), OutputFormat
│   ├── errors.py               # ScannerError → Invalid/Conversion/Configuration
│   ├── engine/
│   │   └── docling_engine.py   # Adapter Docling (auto-device, OCR engines)
│   ├── export/
│   │   ├── markdown.py
│   │   ├── docx.py             # MD → DOCX via pypandoc (auto-baixa pandoc)
│   │   └── pdf.py              # MD → PDF via pandoc + xelatex
│   └── postprocess/
│       └── ptbr_fixer.py       # Dicionário ~150 palavras + regex
│
├── apps/api/                   # === PACOTE BACKEND: scanner-api ===
│   ├── pyproject.toml
│   ├── README.md
│   ├── Dockerfile              # python:3.13-slim + pandoc + texlive + tesseract
│   ├── .dockerignore
│   ├── alembic.ini
│   ├── src/scanner_api/
│   │   ├── __init__.py         # version
│   │   ├── main.py             # create_app() + lifespan async + CORS
│   │   ├── settings.py         # Pydantic Settings (env vars SCANNER_*)
│   │   ├── storage.py          # Layout /data/jobs/{id}/{inputs,outputs,images}
│   │   ├── progress.py         # ProgressBroker (pub/sub via .progress.jsonl)
│   │   ├── schemas.py          # Pydantic request/response (Job*, JobFile*)
│   │   ├── db/
│   │   │   ├── engine.py       # SQLAlchemy 2.0 async + aiosqlite
│   │   │   ├── models.py       # Job, JobFile, PushSubscription
│   │   │   ├── schema.sql      # Referência humana do schema
│   │   │   └── migrations/
│   │   │       ├── env.py      # Alembic async + injeta Settings.db_url
│   │   │       ├── script.py.mako
│   │   │       └── versions/0001_initial.py
│   │   ├── workers/
│   │   │   ├── pool.py         # WorkerPool (ProcessPoolExecutor + asyncio.Queue)
│   │   │   └── worker_main.py  # Subprocess entry: load Docling 1x, scan_batch
│   │   └── routes/
│   │       ├── health.py       # GET /api/health
│   │       ├── jobs.py         # POST/GET /api/jobs + GET /api/jobs/{id}
│   │       ├── files.py        # GET /api/jobs/{id}/files/{filename}
│   │       └── ws.py           # WS /ws/jobs/{id}
│   └── tests/                  # 62 testes; nenhum carrega Docling
│
├── tests/                      # 48 testes do scanner core (CLI + pipeline + engine)
│
├── scripts/
│   ├── postprocess_md.py       # CLI standalone (Phase 0 — wrapper sobre módulo)
│   ├── claude_to_obsidian.py   # Pipeline Obsidian (sessões antigas)
│   └── sync_claude_obsidian.ps1
│
├── docs/
│   ├── HANDOFF.md              # ESTE DOCUMENTO
│   └── superpowers/
│       ├── specs/              # Especificações
│       │   └── 2026-05-02-web-app-pwa-design.md
│       └── plans/              # Planos de implementação (TDD)
│           ├── 2026-05-02-phase-0-backend-refactor.md
│           ├── 2026-05-02-phase-1a-fastapi-foundation.md
│           └── 2026-05-02-phase-1b-fastapi-jobs.md
│
├── samples/                    # Imagens de teste (gitignored)
├── output/                     # Outputs locais (gitignored)
├── tessdata-portuguese/        # Tesseract por.traineddata + eng + osd (gitignored)
├── docling-main/               # Source clonada do Docling (gitignored, referência)
├── claude-exports/             # Staging de chats (gitignored)
│
├── graphify-out/               # Knowledge graph
│   ├── graph.json              # 4667 nodes, 19987 edges
│   ├── graph.html
│   └── GRAPH_REPORT.md
│
├── vault/                      # Obsidian vault local
│   ├── CLAUDE.md
│   ├── projeto/                # MOCs (arquitetura, decisoes, convencoes)
│   ├── logs/                   # Session logs
│   ├── chats/code/             # Imports automáticos
│   └── graphify/               # Notas geradas pelo Graphify
│
└── .claude/
    └── commands/               # Slash commands (/retomar, /salvar)
```

---

## 4. Stack tecnológica

### Runtime / linguagem
- **Python 3.11+** (testado com 3.13 e 3.14)
- **PyTorch 2.11.0+cu128** (GPU CUDA 12.8) ou 2.11.0+cpu
- **Docling 2.92.0** (com `docling-slim`)
- **EasyOCR 1.7.2** (instalado separado — NÃO vem com `docling-slim`)

### CLI
- **Typer 0.25** (geração automática de help, type-safe)
- **Rich 15** (output bonito, tabelas, progressbar)

### Backend (apps/api)
- **FastAPI 0.115** + **Uvicorn 0.32**
- **Pydantic 2.9** + **pydantic-settings 2.6**
- **SQLAlchemy 2.0** + **aiosqlite 0.20** + **Alembic 1.14**
- **aiofiles 24** (streaming de uploads)
- **python-multipart 0.0.20** (form upload)
- **pywebpush 2** (Web Push — Phase 1C)

### Conversão
- **pypandoc 1.x** (auto-baixa pandoc 3.9.0.2)
- **pandoc 3.9.0.2** (auto-instalado em `~/AppData/Local/Pandoc/`)
- **texlive-xetex** (PDF — instalado via Dockerfile em prod)
- **tesseract-ocr-por** (alternativa ao EasyOCR)

### Dev tooling
- **ruff** (lint + format unificado)
- **pytest 9** + **pytest-asyncio 1.3** + **pytest-cov 7**
- **httpx 0.28** (test client ASGI)
- **mypy 1.10** (strict em src/)
- **hatchling** (build backend)

### Hardware testado
- **GPU**: NVIDIA RTX 3060, 12 GB VRAM, driver 595.79 → CUDA 12.8 wheels
- **CPU**: também funciona (~7x mais lento)

---

## 5. Instalação do zero

### Pré-requisitos
- Python 3.11+ (3.13 ou 3.14 recomendado)
- Git
- GPU NVIDIA com CUDA (opcional, dá 7x speedup)

### Passos

```powershell
# 1. clonar
git clone https://github.com/JacksonFuck/scanner-de-imagens.git
cd scanner-de-imagens

# 2. venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. instalar scanner core (CLI)
pip install -e ".[dev]"

# 4. instalar EasyOCR (não vem com docling-slim)
pip install easyocr

# 5. (opcional) PyTorch CUDA 12.8 — GPU acceleration
pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu128

# 6. instalar backend (Phase 1A+1B)
pip install -e ./apps/api[dev]

# 7. validar
python -m scanner --version           # CLI
python -m pytest -q                   # core: 48 passing (3 skipped sem pandoc/xelatex)
cd apps/api && python -m pytest -q    # api: 62 passing
```

### Subir API local

```powershell
$env:SCANNER_DATA_DIR = "/tmp/scanner-data"
$env:SCANNER_VAPID_PUBLIC_KEY = "stub"
$env:SCANNER_VAPID_PRIVATE_KEY = "stub"
$env:SCANNER_VAPID_EMAIL = "test@example.com"

uvicorn scanner_api.main:app --port 8000 --reload

# Em outro terminal:
curl http://localhost:8000/api/health
```

---

## 6. CLI — uso e features

### Comando

```powershell
python -m scanner convert <input> [opções]
```

### Opções

| Flag | Default | Descrição |
|------|---------|-----------|
| `-o, --output PATH` | `./output` | Pasta de saída |
| `-f, --format` | `md` | `md` \| `docx` \| `pdf` \| `all` \| `both` (deprecated, alias de `all`) |
| `--device` | `auto` | `auto` (GPU se disponível) \| `cuda` \| `cpu` |
| `--ocr-lang` | `pt,en` | Idiomas separados por vírgula |
| `--ocr-engine` | `easyocr` | `easyocr` \| `tesseract` |
| `--tessdata PATH` | (auto) | Pasta com `*.traineddata` (Tesseract) |
| `--merge / --no-merge` | (pergunta) | Consolidar múltiplas imagens em arquivo único |
| `--merge-name` | `combined` | Nome base do arquivo consolidado |
| `--no-ocr` | `False` | Desabilita OCR |
| `--no-tables` | `False` | Desabilita reconhecimento de tabelas |
| `-v, --verbose` | `False` | Logs DEBUG |

### Exemplos

```powershell
# Foto única → MD
python -m scanner convert foto.jpg -o ./output

# Pasta inteira → MD + DOCX + PDF, GPU, livro consolidado
python -m scanner convert ./fotos -o ./output -f all --device cuda --merge

# PDF só (sem DOCX)
python -m scanner convert ./doc.pdf -o ./output -f pdf

# Tesseract com tessdata local
python -m scanner convert ./fotos --ocr-engine tesseract --tessdata ./tessdata-portuguese

# Idiomas customizados
python -m scanner convert ./doc.pdf --ocr-lang "pt,en,es"
```

### Formatos: matriz de outputs

| `-f` | Gera |
|------|------|
| `md` | `.md` apenas |
| `docx` | `.md` (intermediário) + `.docx` |
| `pdf` | `.md` (intermediário) + `.pdf` |
| `all` | `.md` + `.docx` + `.pdf` |
| `both` | Igual a `all` (alias deprecated, emite warning até v0.3) |

### API Python

```python
from pathlib import Path
from scanner import scan, scan_batch, ScanRequest, OutputFormat

result = scan(ScanRequest(
    source=Path("foto.jpg"),
    output_dir=Path("./output"),
    formats=OutputFormat.ALL,
    device="cuda",
    ocr_languages=("pt", "en"),
))
print(result.markdown_path, result.docx_path, result.pdf_path, result.images)
```

---

## 7. Backend FastAPI — endpoints e features

### Endpoints HTTP

#### `GET /api/health`
Estado do servidor — usado pelo frontend para mostrar GPU/queue/disk.

```json
{
  "device": "cuda",
  "gpu_name": "NVIDIA GeForce RTX 3060",
  "queue_depth": 0,
  "workers_busy": 0,
  "db_size_mb": 0.05,
  "disk_free_gb": 234.5,
  "version": "0.1.0"
}
```

#### `POST /api/jobs`
Criar um job: upload + queue para worker.

**Request** (multipart/form-data):
- `files` (1+ arquivos): JPG/PNG/PDF
- `formats` (str): `md` | `docx` | `pdf` | `all` | `both`
- `merge` (bool): consolidar em arquivo único
- `title` (str opcional): título amigável
- `advanced` (str opcional): JSON-encoded `JobAdvancedOptions`

**Response** (`201 Created`):
```json
{ "job_id": "550e8400-e29b-41d4-a716-446655440000", "status": "queued" }
```

#### `GET /api/jobs?favorite=&status=&page=`
Listagem paginada (20/página) com filtros.

```json
[
  { "id": "...", "status": "done", "title": "Doc 1", "input_count": 5,
    "formats": "all", "created_at": "...", "is_favorite": 0 },
  ...
]
```

#### `GET /api/jobs/{id}`
Detalhe completo (inclui `files`).

```json
{
  "id": "...", "status": "done", "title": "...", "input_count": 5,
  "merge_mode": 1, "formats": "all", "created_at": "...",
  "finished_at": "...", "is_favorite": 0, "error_msg": null,
  "page_count": 12,
  "files": [
    { "role": "input", "filename": "p1.jpg", "size_bytes": 524288 },
    { "role": "output_md", "filename": "p1.md", "size_bytes": 8192 },
    { "role": "output_pdf", "filename": "p1.pdf", "size_bytes": 102400 },
    ...
  ]
}
```

#### `GET /api/jobs/{id}/files/{filename}`
Download seguro (Content-Disposition: attachment).
- Procura em `outputs/`, `images/`, `inputs/` (nessa ordem).
- Path traversal blocked: `../etc/passwd` → 400.

### WebSocket

#### `WS /ws/jobs/{id}`
Stream de eventos do `.progress.jsonl` como JSON.

Eventos emitidos pelo worker:
```json
{ "type": "started", "ts": 1735000000.0, "input_count": 5 }
{ "type": "progress", "ts": 1735000005.0, "current": 1, "total": 5, "current_file": "p1.jpg" }
{ "type": "progress", "ts": 1735000010.0, "current": 2, "total": 5, "current_file": "p2.jpg" }
...
{ "type": "done", "ts": 1735000040.0, "page_count": 12 }
```

Socket fecha automaticamente em `done` | `error` | `cancelled`.

### Variáveis de ambiente (`SCANNER_*`)

| Var | Default | Descrição |
|-----|---------|-----------|
| `SCANNER_DATA_DIR` | `/data` | Raiz para jobs e DB |
| `SCANNER_MAX_WORKERS` | `2` | ProcessPool size (ge=1, le=8) |
| `SCANNER_DEVICE` | `auto` | `auto` \| `cuda` \| `cpu` |
| `SCANNER_PURGE_HOURS` | `72` | TTL de jobs não-favoritados |
| `SCANNER_MAX_UPLOAD_MB` | `200` | Limite por request multipart |
| `SCANNER_VAPID_PUBLIC_KEY` | (obrigatório) | VAPID pública (Phase 1C) |
| `SCANNER_VAPID_PRIVATE_KEY` | (obrigatório) | VAPID privada (Phase 1C) |
| `SCANNER_VAPID_EMAIL` | (obrigatório) | Email VAPID (Phase 1C) |
| `SCANNER_API_BASE_URL` | `http://localhost:8000` | URL pública da API |

---

## 8. Pós-processador de PT-BR

### Quando usar

OCR antigo (Docling default sem `lang=['pt']`) gerou MDs com acentos perdidos: `condicoes`, `medicos`, `Reducao`. O pós-processador corrige sem re-rodar OCR.

### Comando

```powershell
python -m scanner.postprocess.ptbr_fixer \
    --input-dir output/gestao-ps \
    --output-dir output/gestao-ps-corrigido \
    --merge --merge-name "livro-final" \
    --copy-images
```

### O que faz

1. Aplica dicionário curado de ~150 palavras PT-BR sem acento → forma correta
2. Regex: corrige espaços antes de pontuação, `;` → vírgula em meio de palavra
3. Heurística: `0` → `O` no início de palavras em contexto português
4. Preserva blocos de código markdown (` ``` ` e inline `` ` ``)
5. `--merge`: gera arquivo único com sumário (ToC)
6. `--copy-images`: copia pastas `*-images/` junto

Cobre ~80% dos erros típicos. Ver `scanner/postprocess/ptbr_fixer.py` para o dicionário completo.

---

## 9. Testes

| Pacote | Tests | Cobertura |
|--------|-------|-----------|
| `tests/` (scanner core) | 48 (3 skipped sem pandoc/xelatex) | CLI, pipeline, engine, exports, postprocess |
| `apps/api/tests/` | 62 | settings, storage, db_models, health, progress, workers, jobs_api, ws, files |

**Totalizando ~110 testes** rodando em < 12s combinados, **nenhum carrega Docling de verdade** (smoke test único marcado `@slow`).

### Rodar

```powershell
# Core
python -m pytest -q

# API
cd apps/api
python -m pytest -q

# Com cobertura
python -m pytest --cov=scanner --cov-report=html
```

### Lint

```powershell
python -m ruff check src/ tests/
cd apps/api && python -m ruff check src/ tests/
```

---

## 10. Performance medida

### Batch real: 69 fotos jornal antigo

| Configuração | Tempo/foto | Tempo total |
|---|---|---|
| **CPU** (PyTorch+cpu) | ~35s | ~40 min estimado |
| **GPU** (RTX 3060 + cu128) | ~5s | **~9 min real** ⚡ |

**Speedup**: 7x com GPU.

### Tamanhos típicos (1 página fotografada)
- `.md`: 2-5 KB
- `.docx`: 12-50 KB
- `.pdf`: 80-200 KB
- imagens extraídas: 20-200 KB cada (PNG, scale 3x)

### Custo de tokens
- Pipeline padrão: **0 tokens LLM** (tudo OCR + algoritmos)
- Graphify modo AST: **0 tokens** (4667 nodes, 19987 edges)
- Pós-processador: **0 tokens** (regex + dicionário)

---

## 11. Decisões arquiteturais

Detalhe completo em `vault/projeto/decisoes.md`. Resumo cronológico:

| # | Tema | Decisão | Phase |
|---|------|---------|-------|
| 1 | Motor extração | Docling (não OpenDataloader-PDF) — aceita JPG/PNG nativos | inicial |
| 2 | OCR engine | EasyOCR primário; Tesseract opcional | 0 |
| 3 | OCR languages | `pt,en` explícito (default Docling não tem PT!) | 0 |
| 4 | Image scale | 3.0x (default 2.0) | 0 |
| 5 | Pós-processador | Dicionário PT-BR curado, em pacote `scanner.postprocess` | 0 |
| 6 | Output format | Adicionado PDF + ALL; mantido BOTH como alias deprecated | 0 |
| 7 | PDF toolchain | pandoc + xelatex (texlive-lang-portuguese) | 0 |
| 8 | Backend framework | FastAPI 0.115 + lifespan async | 1A |
| 9 | DB | SQLite + SQLAlchemy 2 async + Alembic | 1A |
| 10 | Storage | Filesystem (`/data/jobs/{id}/...`) — sem MinIO | 1A |
| 11 | Settings | Pydantic Settings + env vars `SCANNER_*` | 1A |
| 12 | Worker model | ProcessPoolExecutor + asyncio.Queue dispatcher | 1B |
| 13 | Progresso | `.progress.jsonl` apêndice + asyncio tail + WS broadcast | 1B |
| 14 | Path traversal | `resolve().relative_to(base)` em download | 1B |
| 15 | GPU | PyTorch 2.11+cu128 (única versão com wheels Python 3.14) | (descoberta) |

---

## 12. Memória persistente do projeto (Vault + Graphify)

### Vault Obsidian (`vault/`)

| Pasta | Conteúdo |
|-------|----------|
| `vault/projeto/` | MOCs: `arquitetura.md`, `decisoes.md`, `convencoes.md` |
| `vault/logs/` | Session logs (gerados por `/salvar`) |
| `vault/chats/` | Conversas Claude importadas (cron diário) |
| `vault/graphify/` | Notas auto-geradas pelo Graphify |

Abrir no Obsidian: "Open folder as vault" → selecionar a raiz do projeto.

### Slash commands

- `/retomar` (`.claude/commands/retomar.md`): lê últimos logs + decisões, resume estado
- `/salvar` (`.claude/commands/salvar.md`): cria session log no vault

### Knowledge graph

```powershell
graphify update .
```

Atual: **4667 nodes, 19987 edges, 60 communities** (post-Phase 1B).

Consultas:
```powershell
graphify query "como funciona o WebSocket de progresso"
graphify path "DoclingEngine" "POST /api/jobs"
graphify explain "WorkerPool"
```

---

## 13. Troubleshooting

### "ModuleNotFoundError: easyocr"
`docling-slim` não inclui EasyOCR. Instale:
```powershell
pip install easyocr
```

### "Could not find a version that satisfies the requirement torch (cu124)"
PyTorch CUDA não tem wheels para sua versão Python. Para 3.14, **somente cu128**:
```powershell
pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

### CUDA disponível mas não é usado
1. Confirmar: `python -c "import torch; print(torch.cuda.is_available())"`
2. Forçar via flag: `--device cuda`
3. Se ainda CPU, ver log: deve aparecer `Accelerator device: 'cuda:0'`

### Pandoc rate limit (HTTP 403)
Acontecia em runs grandes. **Resolvido em commit `9fd4d0c`**: `_ensure_pandoc()` agora procura em `~/AppData/Local/Pandoc/` antes de baixar.

### "Acentos virando ASCII (ção → cao)"
OCR rodou com idiomas errados. Use:
```powershell
python -m scanner convert ... --ocr-lang "pt,en"
```
Para corrigir MDs já gerados: `python -m scanner.postprocess.ptbr_fixer ...`.

### Encoding UnicodeError no Windows
PowerShell 5.1 usa cp1252. Sempre passe `encoding='utf-8'` em `Path.write_text()`.

### Múltiplos Pythons no PATH
Use venv dedicado:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Tests da api falham com path lock no Windows
Os fixtures fazem `engine.dispose()` no teardown — se ver erro de "file locked", garante que conftest.py está atualizado.

### B008 false positive do ruff em FastAPI
Já ignorado em `apps/api/pyproject.toml`. FastAPI **requer** `File(...)` e `Depends(...)` em arg defaults.

---

## 14. Histórico de fases

### Phase 0 — Backend refactor + PDF + ALL (commits `f34c3cd`..`4c905da`)
- `scanner.postprocess.ptbr_fixer` — promovido de `scripts/` para módulo importável
- `OutputFormat.PDF` + `OutputFormat.ALL` + alias deprecated `BOTH`
- `scanner/export/pdf.py` — pandoc + xelatex
- CLI: `-f all` substitui `-f both` (warning até v0.3)
- 48 testes (3 skipped sem toolchain de PDF)

### Phase 1A — FastAPI foundation (commits `10b79b3`..`33fe3c9`)
- Skeleton `apps/api/` (pyproject + Dockerfile + main.py + conftest)
- Settings module (Pydantic Settings + env vars `SCANNER_*`)
- Storage layout (`/data/jobs/{id}/{inputs,outputs,images}`)
- SQLAlchemy 2.0 async engine + session factory + Alembic init
- ORM models: `Job`, `JobFile`, `PushSubscription` + initial migration
- `GET /api/health` (device, queue, db_size, disk_free, version)
- 28 testes E2E via httpx ASGI

### Phase 1B — Workers + Jobs API + WebSocket (commits `7d98682`..`74b4963`)
- ProcessPoolExecutor + asyncio.Queue dispatcher
- `worker_main.py` subprocess: load Docling 1x, scan_batch, .progress.jsonl
- `ProgressBroker` pub/sub via asyncio + tail aiofiles
- `POST /api/jobs` — multipart upload + DB + queue submit
- `GET /api/jobs` — paginação + filtros (favorite, status)
- `GET /api/jobs/{id}` — detalhe com files (eager load)
- `WS /ws/jobs/{id}` — stream de progresso
- `GET /api/jobs/{id}/files/{filename}` — download seguro com path traversal protection
- 62 testes total no apps/api

---

## 15. O que falta (TODO)

Ver **[TODO.md](../TODO.md)** na raiz do projeto para a lista completa de itens pendentes (Phase 1C, 2, 3, 4 + outras melhorias).

Resumo:
- **Phase 1C**: Push notifications (VAPID) + purge cron + PATCH/DELETE jobs
- **Phase 2**: Frontend Next.js 15 consumindo a API
- **Phase 3**: PWA (service worker + manifest + offline)
- **Phase 4**: Docker Compose + deploy Hostinger + nginx reverse proxy
- **Outros**: GitHub Actions CI, badges no README, CHANGELOG

---

## Para a próxima sessão

Use `/retomar` ao iniciar. O comando lê:
1. Últimos 3 session logs em `vault/logs/`
2. `vault/projeto/decisoes.md`
3. `graphify-out/GRAPH_REPORT.md`

E imprime resumo do estado atual + próximos passos.

Ao finalizar, use `/salvar [slug]` para gerar log da sessão.

---

## Contato e licença

- **Autor**: Jackson (jacksontorax@gmail.com / GitHub: JacksonFuck)
- **Licença**: MIT
- **Repositório**: https://github.com/JacksonFuck/scanner-de-imagens
- **Branch ativa**: `feat/phase-0-backend-refactor` (24 commits ahead of master)
- **PR pronto**: https://github.com/JacksonFuck/scanner-de-imagens/pull/new/feat/phase-0-backend-refactor
