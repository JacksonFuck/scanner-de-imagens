# Scanner de Imagens

> OCR de fotografias de páginas de livros e artigos → **Markdown estruturado** + export opcional para **DOCX e PDF**, preservando imagens, tabelas e qualidade.

Sistema dual: **CLI** para uso local + **API REST/WebSocket** para integração web.

📖 **[Documentação completa em docs/HANDOFF.md](docs/HANDOFF.md)** — instalação, arquitetura, decisões, troubleshooting.
📋 **[TODO.md](TODO.md)** — roadmap (Phase 1C, 2, 3, 4 + backlog).

---

## Status

| Componente | Estado | Detalhes |
|---|---|---|
| **CLI** (`python -m scanner`) | ✅ Funcional | MD + DOCX + PDF + ALL |
| **API REST** (`uvicorn scanner_api.main:app`) | ✅ Funcional | Endpoints CRUD + downloads + path traversal protection |
| **WebSocket** (`/ws/jobs/{id}`) | ✅ Funcional | Stream de progresso ao vivo |
| **Worker pool** | ✅ Funcional | ProcessPoolExecutor + asyncio.Queue |
| **Pós-processador PT-BR** | ✅ Funcional | ~150 palavras + regex |
| **Push notifications** | ⏭️ Phase 1C | VAPID keys + service worker |
| **PATCH/DELETE /api/jobs** | ⏭️ Phase 1C | Favoritar, renomear, apagar |
| **Frontend Next.js** | 🟡 Phase 2 (scaffold) | `apps/web/` — Next.js 15 + Tailwind 4 + WS live |
| **PWA** | ⏭️ Phase 3 | Service worker + manifest + push UI |
| **Deploy Docker + Hostinger** | ⏭️ Phase 4 | docker-compose + nginx + Let's Encrypt |

---

## Stack

- **Engine OCR**: [Docling](https://github.com/DS4SD/docling) 2.92 (IBM) + EasyOCR 1.7
- **CLI**: Typer + Rich
- **Backend**: FastAPI 0.115 + SQLAlchemy 2.0 async + aiosqlite + Alembic
- **Worker**: ProcessPoolExecutor (isola Docling do event loop)
- **Export**: pypandoc + pandoc 3.9 + xelatex
- **GPU**: PyTorch 2.11+cu128 (Python 3.14 compat)

110 testes passing, ruff clean.

---

## Frontend (`apps/web/`)

Aplicação Next.js 15 (App Router) que consome a API. Inclui dashboard com dropzone, lista paginada de jobs (filtros: ativos, concluídos, favoritos), detalhe com progresso ao vivo via WebSocket, favoritar/deletar e download de outputs. Stack: TypeScript strict, Tailwind 4, lucide-react, react-dropzone, sonner.

```bash
cd apps/web
cp .env.local.example .env.local
npm install && npm run dev
```

Detalhes: [`apps/web/README.md`](apps/web/README.md).

---

## Quickstart (CLI)

```bash
# Instalar
git clone https://github.com/JacksonFuck/scanner-de-imagens.git
cd scanner-de-imagens
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pip install easyocr

# (opcional) GPU
pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu128

# Converter foto única
python -m scanner convert ./foto.jpg -o ./output -f md

# Pasta inteira → MD + DOCX + PDF, GPU, livro consolidado
python -m scanner convert ./fotos -o ./output -f all --device cuda --merge
```

---

## Quickstart (Backend)

```bash
# Instalar API
pip install -e ./apps/api[dev]

# Subir local
SCANNER_DATA_DIR=/tmp/scanner SCANNER_VAPID_PUBLIC_KEY=stub \
SCANNER_VAPID_PRIVATE_KEY=stub SCANNER_VAPID_EMAIL=t@e.com \
uvicorn scanner_api.main:app --port 8000 --reload

# Testar
curl http://localhost:8000/api/health
# {"device":"cuda","gpu_name":"NVIDIA GeForce RTX 3060",
#  "queue_depth":0,"workers_busy":0,"db_size_mb":0.05,
#  "disk_free_gb":234.5,"version":"0.1.0"}
```

---

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/api/health` | Estado: device/queue/disk/version |
| `POST` | `/api/jobs` | Upload multipart + queue para worker |
| `GET` | `/api/jobs?favorite=&status=&page=` | Listagem paginada |
| `GET` | `/api/jobs/{id}` | Detalhe com files |
| `GET` | `/api/jobs/{id}/files/{filename}` | Download seguro |
| `WS` | `/ws/jobs/{id}` | Stream de progresso ao vivo |

Detalhes em [docs/HANDOFF.md § 7](docs/HANDOFF.md#7-backend-fastapi--endpoints-e-features).

---

## Performance

| Configuração | Tempo/foto | 69 fotos |
|---|---|---|
| CPU (PyTorch+cpu) | ~35s | ~40 min |
| GPU (RTX 3060 + cu128) | ~5s | **~9 min** |

7x speedup com GPU. Custo de tokens LLM: **0**.

---

## Estrutura do monorepo

```
.
├── src/scanner/                  # Pacote core (CLI)
│   ├── cli.py, pipeline.py, errors.py
│   ├── engine/docling_engine.py
│   ├── export/{markdown,docx,pdf}.py
│   └── postprocess/ptbr_fixer.py
├── apps/api/                     # Pacote backend
│   └── src/scanner_api/
│       ├── main.py, settings.py, storage.py, progress.py, schemas.py
│       ├── db/{engine,models,migrations/}
│       ├── workers/{pool,worker_main}.py
│       └── routes/{health,jobs,files,ws}.py
├── tests/                        # 48 tests do core
├── apps/api/tests/               # 62 tests do backend
├── docs/HANDOFF.md               # Documentação âncora
├── docs/superpowers/             # Specs + plans
├── TODO.md                       # Roadmap
├── vault/                        # Obsidian (memória persistente)
├── graphify-out/                 # Knowledge graph (4667 nodes)
└── scripts/                      # Utilitários standalone
```

---

## Licença

MIT — Jackson (jacksontorax@gmail.com)
