---
title: Scanner de Imagens — Web App + PWA (Design Spec)
date: 2026-05-02
status: draft
authors: [Jackson, Claude]
tags: [spec, design, web, pwa, fastapi, nextjs]
supersedes: null
---

# Scanner de Imagens — Web App + PWA

## 1. Contexto

O **Scanner de Imagens** existe hoje como CLI Python que recebe fotos de páginas (JPG/PNG) ou PDFs e gera Markdown estruturado + DOCX usando Docling 2.92 (IBM) com EasyOCR. O motor já está validado: 69/69 fotos do dataset "Gestão de PS" foram convertidas com sucesso, GPU acelera ~7× (5s/foto vs 35s CPU), e o pós-processador PT-BR (`scripts/postprocess_md.py`) corrige acentos e cedilha que o OCR perde.

O projeto está em `C:\Users\jacks\OneDrive\2º Cérebro\Scanner de imagens`, repo público em [github.com/JacksonFuck/scanner-de-imagens](https://github.com/JacksonFuck/scanner-de-imagens). Este spec define a evolução para uma aplicação **web + PWA mobile-first**, hospedada na VPS Hostinger do usuário.

## 2. Objetivos

- Expor o pipeline OCR via interface web acessível de qualquer browser e do celular
- Suportar entrada de imagens via **upload (drag-drop)**, **paste** (Ctrl+V), **galeria** do celular e **câmera** nativa
- Permitir escolha entre **arquivos separados** (1 MD por imagem) ou **arquivo único consolidado** (merge)
- Oferecer download em **MD, DOCX e PDF**
- Funcionar como **PWA L4 completo**: instalável, offline shell, background sync, push notifications
- Manter **biblioteca pessoal** com auto-purge (72h) + favoritos permanentes
- Compartilhar 100% do motor OCR com a CLI atual (zero fork de código)
- Deploy single-tenant via Docker Compose na Hostinger VPS Plano C (16 GB / 4 vCPU, sem GPU)

## 3. Não-objetivos (escopo explicitamente excluído)

- ❌ Multi-tenancy / cadastro público / gestão de usuários (futura iteração)
- ❌ OCR no client-side (offline) — modelos Docling não cabem no browser
- ❌ Edição manual do Markdown extraído pela UI (só preview e download)
- ❌ Integração com LLM externo para casos ambíguos (roadmap futuro)
- ❌ Mobile app nativo (React Native, Flutter) — PWA atende o caso de uso
- ❌ Microservices / Kubernetes / Redis — overkill para single-tenant
- ❌ Autenticação OAuth / SSO — basic auth Nginx é suficiente

## 4. Decisões registradas (do brainstorm)

| # | Decisão | Justificativa |
|---|---------|---------------|
| 1 | VPS = Hostinger Plano C (16+ GB, 4+ vCPU, **CPU-only** em produção) | Conforto para 2-3 workers paralelos. GPU continua disponível em dev local via `device=auto` já existente. |
| 2 | PDF via Pandoc + `xelatex` | Reusa toolchain existente (DOCX). Lida com acentos PT-BR. PDF "estilo artigo". Custo: ~250 MB de imagem Docker. |
| 3 | Acesso single-tenant via Nginx basic auth | Solo + future-proof para multi-user (paths já organizados em `/data/jobs/{job_id}/`). |
| 4 | Histórico híbrido: auto-purge 72 h + favoritos permanentes | Match com uso real (livros importantes ficam, conversões pontuais somem). SQLite. |
| 5 | PWA L4 completo desde o MVP | Push notifications úteis para jobs longos. iOS 16.4+ exige instalação na home screen. |
| 6 | Pós-processamento sempre ON. Painel "Avançado" colapsável. CLI mantida. | UX mobile-first limpa, com escape hatch para tuning. |

## 5. Arquitetura (Abordagem escolhida)

**FastAPI + ProcessPoolExecutor + Next.js 15 (sem Redis).**

```
┌─────────────────────────────────────────────────────────────────┐
│   Hostinger VPS (KVM 4)  ─  Docker Compose  ─  HTTPS via certbot │
├─────────────────────────────────────────────────────────────────┤
│   Nginx 1.27  (TLS + basic auth + reverse proxy + gzip)         │
│     ├─→ /          → web    (Next.js 3000)                       │
│     ├─→ /api/*     → api    (FastAPI 8000)                       │
│     └─→ /ws/*      → api    (FastAPI 8000, Upgrade headers)      │
│                                                                  │
│   FastAPI 0.115+  (asyncio + WebSocket)                         │
│     ├─→ ProcessPoolExecutor(max_workers=2)                      │
│     │     └─→ scanner.scan_batch()  (Docling + EasyOCR)         │
│     │     └─→ scanner.postprocess.fix_text()                    │
│     │     └─→ pandoc → DOCX, PDF                                │
│     ├─→ SQLite (/data/scanner.db)                               │
│     ├─→ pywebpush → push notifications (VAPID)                  │
│     └─→ Cron host: purga jobs > 72h não-favoritados             │
└─────────────────────────────────────────────────────────────────┘
```

**Por que essa combinação:**
- Reuso 100% do pacote Python `scanner/` — CLI e API consomem a mesma biblioteca
- ProcessPoolExecutor isola o trabalho pesado (CPU-bound) do event loop async da API
- Workers carregam Docling **uma vez** (~5s) e atendem N jobs — crítico em CPU
- Sem Redis = um serviço a menos, ~50 MB RAM economizados, deploy mais simples
- Migrar para fila externa (RQ/Celery) no futuro = mudança isolada em uma classe (~50 linhas)

## 6. Estrutura do monorepo

```
Scanner de imagens/
├── src/scanner/                        ← INTOCADO. Pacote OCR existente.
│   ├── cli.py                            (CLI continua funcionando)
│   ├── pipeline.py                       (scan, scan_batch, merge_results, OutputFormat)
│   ├── engine/docling_engine.py
│   ├── export/{markdown.py, docx.py, pdf.py}    ← pdf.py NOVO
│   └── postprocess/                    ← NOVO (movido de scripts/postprocess_md.py)
│       ├── __init__.py                   (fix_text, merge_into_book, ACCENT_MAP)
│       └── ptbr.py
│
├── apps/
│   ├── api/                            ← NOVO — Backend FastAPI
│   │   ├── pyproject.toml                 (dep: scanner em path local + fastapi + sqlalchemy + pywebpush)
│   │   ├── Dockerfile
│   │   ├── src/scanner_api/
│   │   │   ├── main.py                    (FastAPI app + lifespan: pool startup/shutdown)
│   │   │   ├── settings.py                (Pydantic Settings: env vars)
│   │   │   ├── routes/
│   │   │   │   ├── jobs.py                (POST/GET/PATCH/DELETE /api/jobs)
│   │   │   │   ├── files.py               (GET /api/jobs/{id}/files/{name})
│   │   │   │   ├── push.py                (VAPID + subscribe/unsubscribe)
│   │   │   │   ├── health.py              (device, queue depth, GPU info)
│   │   │   │   └── ws.py                  (WebSocket /ws/jobs/{id})
│   │   │   ├── workers/
│   │   │   │   ├── pool.py                (ProcessPoolExecutor lifecycle)
│   │   │   │   └── worker_main.py         (subprocess entry: load Docling 1x)
│   │   │   ├── db/
│   │   │   │   ├── models.py              (SQLAlchemy ORM: Job, JobFile, PushSubscription)
│   │   │   │   ├── schema.sql             (DDL canônico)
│   │   │   │   └── migrations/            (Alembic)
│   │   │   ├── storage.py                 (paths, write, ensure_dir, retention)
│   │   │   ├── progress.py                (asyncio pub/sub por job_id; tail .progress.jsonl)
│   │   │   ├── push.py                    (pywebpush wrapper)
│   │   │   └── tasks/
│   │   │       └── purge_expired.py       (entry point do cron)
│   │   └── tests/
│   │
│   └── web/                            ← NOVO — Frontend Next.js (clone DocRAG-Web)
│       ├── package.json                   (next 15, react 19, tailwind 4, lucide, react-dropzone, react-markdown)
│       ├── next.config.ts
│       ├── public/
│       │   ├── manifest.webmanifest
│       │   ├── sw.js                      (custom service worker)
│       │   └── icons/                     (192x192, 512x512 PNG)
│       ├── src/
│       │   ├── app/
│       │   │   ├── layout.tsx             (root + SW registration)
│       │   │   ├── page.tsx               (Home — uploader)
│       │   │   ├── jobs/page.tsx          (Histórico)
│       │   │   ├── jobs/[id]/page.tsx     (Detalhe + preview + downloads)
│       │   │   └── settings/page.tsx      (Push, install, health, purge)
│       │   ├── components/
│       │   │   ├── DropZone.tsx           (drag-drop + paste + galeria + câmera)
│       │   │   ├── JobCard.tsx
│       │   │   ├── ProgressBar.tsx
│       │   │   ├── MarkdownPreview.tsx    (react-markdown + remark-gfm)
│       │   │   ├── AdvancedPanel.tsx      (collapsible)
│       │   │   ├── DownloadButtons.tsx    (MD/DOCX/PDF + ★ favorito)
│       │   │   └── InstallPrompt.tsx
│       │   ├── hooks/
│       │   │   ├── useJobs.ts
│       │   │   ├── useJobProgress.ts      (WebSocket)
│       │   │   ├── usePush.ts
│       │   │   └── useInstallPrompt.ts
│       │   ├── lib/{api.ts, utils.ts, sw-register.ts, idb.ts}
│       │   └── types/index.ts
│       └── Dockerfile
│
├── infra/                              ← NOVO — Tudo de deploy
│   ├── docker-compose.yml                 (api + web + nginx)
│   ├── docker-compose.dev.yml             (override para dev local)
│   ├── nginx/
│   │   ├── default.conf
│   │   └── htpasswd                       (gitignored)
│   ├── scripts/
│   │   ├── purge_old_jobs.sh              (cron diário 72h)
│   │   ├── backup_data.sh                 (rsync /data → /backup)
│   │   └── generate_vapid_keys.py         (run-once VAPID setup)
│   └── certbot/                           (volume Let's Encrypt)
│
├── scripts/postprocess_md.py           ← REMOVIDO (movido)
├── docs/HANDOFF.md                     ← INTOCADO
├── docs/superpowers/specs/             ← este arquivo aqui
├── pyproject.toml                      ← scanner/ raiz (mantido)
├── README.md                           ← atualizado mencionando web app
├── .gitignore                          ← + apps/web/.next, /data, infra/nginx/htpasswd
└── CLAUDE.md                           ← INTOCADO
```

**Mudança crítica**: `scripts/postprocess_md.py` precisa virar módulo importável (`src/scanner/postprocess/`). Único ponto de atrito na migração — ~10 linhas.

## 7. Backend (FastAPI)

### 7.1. Endpoints REST

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `/api/jobs` | Multipart upload (1+ imagens) + opções. Retorna `{job_id, status: "queued"}` |
| GET | `/api/jobs?favorite={0,1}&status={..}&page={n}` | Lista paginada (20/page) |
| GET | `/api/jobs/{id}` | Detalhe + lista de `job_files` |
| PATCH | `/api/jobs/{id}` | `{title?, is_favorite?}` — toggle fav e edita título |
| DELETE | `/api/jobs/{id}` | Apaga job + arquivos do disco |
| GET | `/api/jobs/{id}/files/{filename}` | Download (Content-Disposition: attachment) |
| GET | `/api/health` | `{device, gpu_name, queue_depth, workers_busy, db_size_mb, disk_free_gb, version}` |
| GET | `/api/push/vapid-public-key` | Retorna VAPID pubkey |
| POST | `/api/push/subscribe` | `{endpoint, p256dh, auth, user_agent}` — registra |
| DELETE | `/api/push/subscribe/{endpoint}` | Remove subscription |
| WS | `/ws/jobs/{id}` | Stream de eventos: `progress`, `done`, `error`, `cancelled` |

### 7.2. Modelo de worker

- `ProcessPoolExecutor(max_workers=2)` instanciado em FastAPI lifespan
- Cada worker:
  1. No spawn, importa `docling.document_converter` e instancia `DoclingEngine` (carrega modelos ~5s)
  2. Loop: recebe `job_id` da queue → carrega `ScanRequest` do SQLite → roda `scanner.scan_batch()` → atualiza job_files no DB → escreve evento `done` em `/data/jobs/{id}/.progress.jsonl`
- Reporte de progresso via append em `.progress.jsonl` (1 linha JSON por evento). FastAPI tail desse arquivo via `aiofiles` + `asyncio.Event`, broadcast a clientes WebSocket conectados àquele `job_id`.
- **Por que arquivo e não IPC**: simples, debugável (pode `cat .progress.jsonl`), sobrevive a crash do worker.

### 7.3. SQLite schema

```sql
CREATE TABLE jobs (
  id           TEXT PRIMARY KEY,           -- UUID4
  status       TEXT NOT NULL CHECK(status IN ('queued','running','done','error','cancelled')),
  title        TEXT,                       -- editável; default = nome do 1º input
  input_count  INTEGER NOT NULL,
  merge_mode   INTEGER NOT NULL DEFAULT 0, -- 0=separados, 1=merge
  formats      TEXT NOT NULL,              -- 'md' | 'docx' | 'pdf' | 'all'
  advanced     TEXT,                       -- JSON: {ocr_engine, ocr_lang, do_tables, do_postprocess, device}
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at  TIMESTAMP,
  expires_at   TIMESTAMP,                  -- created_at + 72h, NULL se favorito
  is_favorite  INTEGER NOT NULL DEFAULT 0,
  error_msg    TEXT,
  page_count   INTEGER
);

CREATE TABLE job_files (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id      TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  role        TEXT NOT NULL CHECK(role IN ('input','output_md','output_docx','output_pdf','image')),
  filename    TEXT NOT NULL,
  size_bytes  INTEGER NOT NULL
);

CREATE TABLE push_subscriptions (
  endpoint    TEXT PRIMARY KEY,
  p256dh      TEXT NOT NULL,
  auth        TEXT NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  user_agent  TEXT
);

CREATE INDEX idx_jobs_expires_nonfav ON jobs(expires_at) WHERE is_favorite = 0;
CREATE INDEX idx_jobs_created_desc ON jobs(created_at DESC);
CREATE INDEX idx_job_files_job ON job_files(job_id);
```

### 7.4. OutputFormat (extensão do enum existente — sem breaking change imediato)

```python
# src/scanner/pipeline.py — versão atual:
class OutputFormat(StrEnum):
    MD = "md"
    DOCX = "docx"
    BOTH = "both"     # MD + DOCX (semântica antiga)

# Nova versão:
class OutputFormat(StrEnum):
    MD = "md"
    DOCX = "docx"
    PDF = "pdf"
    ALL = "all"       # MD + DOCX + PDF
    BOTH = "both"     # DEPRECATED: alias para 'all' por compat com CLI antiga.
                      # Emite DeprecationWarning. Removido em v0.3.0.
```

**Estratégia de compat**:
- `BOTH` permanece no enum durante v0.2.x — mapeado internamente para `ALL` em `pipeline.scan()` (mesma lista de outputs gerados).
- CLI flag `-f both` continua funcionando, mas o `convert` command imprime aviso `[deprecated] -f both → use -f all` no stderr.
- Testes existentes que usam `OutputFormat.BOTH` continuam passando (mesmo comportamento, agora produzindo MD+DOCX+PDF — leve ampliação de escopo, não regressão).
- v0.3.0 remove `BOTH` do enum. Documentado em CHANGELOG.

**Impacto na API web**: o backend FastAPI aceita apenas `'md' | 'docx' | 'pdf' | 'all'` no payload (não expõe `both`). Único consumer de `BOTH` é a CLI legada.

### 7.5. Variáveis de ambiente

| Var | Default | Descrição |
|-----|---------|-----------|
| `SCANNER_DATA_DIR` | `/data` | Raiz de jobs e DB |
| `SCANNER_MAX_WORKERS` | `2` | ProcessPool size |
| `SCANNER_DEVICE` | `auto` | `auto`\|`cuda`\|`cpu` (override do auto-detect) |
| `SCANNER_PURGE_HOURS` | `72` | TTL para jobs não-favoritados |
| `SCANNER_MAX_UPLOAD_MB` | `200` | Limite por request |
| `SCANNER_VAPID_PUBLIC_KEY` | (obrigatório) | Gerado por `infra/scripts/generate_vapid_keys.py` |
| `SCANNER_VAPID_PRIVATE_KEY` | (obrigatório) | Idem |
| `SCANNER_VAPID_EMAIL` | (obrigatório) | Contato para Mozilla/Google push services |
| `SCANNER_API_BASE_URL` | `http://localhost:8000` | Para CORS e construção de URLs absolutas |

## 8. Frontend (Next.js 15 + Tailwind 4)

### 8.1. Páginas

- **`/` (Home)** — Uploader full-screen no mobile. DropZone aceita drag-drop, click (galeria), Ctrl+V (paste), e tem botão "Tirar foto" que abre `<input capture="environment">`. Toggles: merge/separado, formatos (MD/DOCX/PDF). Painel "Avançado" colapsável. Botão CTA "Converter".
- **`/jobs/[id]`** — Live progress. WebSocket conectado. ProgressBar + lista de thumbnails das fotos sendo processadas. Botão "Cancelar" (soft cancel — worker termina o item atual e para). Quando completar: MarkdownPreview (react-markdown) + DownloadButtons + estrela favorito + título editável inline.
- **`/jobs`** — Lista (cards). Filtros: `Todos | Em andamento | Favoritos`. Busca por título. Cada card mostra thumbnail do 1º input, título, data, status badge, número de páginas, botões `Abrir | Baixar | Favoritar | Apagar`.
- **`/settings`** — Toggle push notifications (com permission flow), botão "Instalar app" (chama `prompt()` se disponível), display de `/api/health`, botão "Apagar todos os jobs não-favoritados" (com confirmação).

### 8.2. Estado e dados

- **Hooks customizados** (sem Redux/Zustand):
  - `useJobs(filter)`: fetch `/api/jobs`, retorna `{jobs, isLoading, refresh}`
  - `useJob(id)`: fetch `/api/jobs/{id}`
  - `useJobProgress(id)`: WebSocket `/ws/jobs/{id}`, retorna `{progress, status, currentFile}`
  - `usePush()`: `{isSubscribed, subscribe(), unsubscribe(), permission}`
  - `useInstallPrompt()`: `{canInstall, prompt(), wasInstalled}`
- **Estado local** (`useState`/`useReducer`) para forms e UI.
- **IndexedDB** (`idb` lib) para fila offline (`uploads-pending` store).

### 8.3. Mobile-first

- Layout único em coluna no mobile. Desktop ganha 2-coluna em `/jobs/[id]` (preview esquerda, downloads direita).
- DropZone full-screen no mobile, ocupa 70% da viewport com texto grande.
- Banner "Adicionar à Tela Inicial" aparece em iOS Safari não-instalado (display !== standalone).
- Botões com `min-height: 44px` (Apple HIG / Google Material para tap targets).

## 9. PWA (L4 completo)

### 9.1. Manifest (`public/manifest.webmanifest`)

```json
{
  "name": "Scanner de Imagens",
  "short_name": "Scanner",
  "description": "OCR de fotos de páginas → Markdown + DOCX + PDF",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait",
  "theme_color": "#0f172a",
  "background_color": "#ffffff",
  "categories": ["productivity", "utilities"],
  "icons": [
    {"src":"/icons/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},
    {"src":"/icons/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}
  ],
  "shortcuts": [
    {"name":"Tirar foto","url":"/?action=camera","icons":[{"src":"/icons/camera-96.png","sizes":"96x96"}]}
  ]
}
```

### 9.2. Service Worker (`public/sw.js`)

Custom (sem next-pwa para controle total):

- **install**: pré-cache shell (`/`, `/manifest.webmanifest`, ícones, `_next/static/css/*`)
- **fetch**:
  - `_next/static/*` → cache-first
  - `/api/*` → network-first com fallback offline (retorna `{offline: true}` JSON)
  - HTML routes → stale-while-revalidate
- **sync** event (`tag === "upload-pending"`):
  - Drena IndexedDB store `uploads-pending`
  - Para cada entrada: `fetch /api/jobs` com FormData reconstituída
  - On success: remove da IDB
- **push** event:
  - Parse payload `{job_id, title, status, message}`
  - `self.registration.showNotification(...)` com action button "Abrir"
- **notificationclick** event:
  - Foca aba existente ou abre `/jobs/{job_id}`

### 9.3. Push Notifications (VAPID)

- Setup uma vez: `python infra/scripts/generate_vapid_keys.py` produz `vapid_public.pem` + `vapid_private.pem`. Encoded base64url + injetado nas env vars do `docker-compose.yml`.
- Frontend: `usePush()` chama `/api/push/vapid-public-key`, faz `pushManager.subscribe({applicationServerKey})`, posta resultado em `/api/push/subscribe`.
- Backend: ao mudar status de job para `done`/`error`, lê todas as `push_subscriptions` (single-tenant: 1-3 subscriptions max — múltiplos devices do usuário) e envia via `pywebpush.webpush()`. Subs com 410 (Gone) são removidas.
- iOS-specific: requer `display: standalone` E PWA instalado via "Adicionar à Tela Inicial". Banner discreto aparece com instrução visual (1 vez, dismissable).

## 10. Deployment (Hostinger VPS)

### 10.1. Docker Compose

```yaml
# infra/docker-compose.yml (resumo)
services:
  api:
    build:
      context: ../
      dockerfile: apps/api/Dockerfile      # python:3.13-slim + scanner/ + pandoc + texlive-xetex + EasyOCR models
    volumes: [./data:/data]
    environment:
      SCANNER_DATA_DIR: /data
      SCANNER_MAX_WORKERS: 2
      SCANNER_DEVICE: auto
      SCANNER_VAPID_PUBLIC_KEY: ${VAPID_PUBLIC_KEY}
      SCANNER_VAPID_PRIVATE_KEY: ${VAPID_PRIVATE_KEY}
      SCANNER_VAPID_EMAIL: ${VAPID_EMAIL}
    expose: [8000]
    restart: unless-stopped

  web:
    build:
      context: ../
      dockerfile: apps/web/Dockerfile      # node:20-alpine, next build standalone
    expose: [3000]
    environment:
      NEXT_PUBLIC_API_BASE: /api
      NEXT_PUBLIC_WS_BASE: /ws
    restart: unless-stopped

  nginx:
    image: nginx:1.27-alpine
    ports: ["80:80","443:443"]
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - ./nginx/htpasswd:/etc/nginx/.htpasswd:ro
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on: [api, web]
    restart: unless-stopped
```

### 10.2. Nginx (excerto)

```nginx
server {
  listen 443 ssl http2;
  server_name scanner.seudominio.com;
  ssl_certificate     /etc/letsencrypt/live/scanner.seudominio.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/scanner.seudominio.com/privkey.pem;

  client_max_body_size 200M;
  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/markdown;

  auth_basic "Scanner";
  auth_basic_user_file /etc/nginx/.htpasswd;

  location /api/ { proxy_pass http://api:8000; proxy_set_header Host $host; }
  location /ws/  {
    proxy_pass http://api:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
  }
  location /     { proxy_pass http://web:3000; proxy_set_header Host $host; }
}
```

### 10.3. Cron (host)

```cron
0 3 * * * cd /home/jacks/scanner && docker compose exec -T api python -m scanner_api.tasks.purge_expired
```

### 10.4. Domínio + HTTPS

- Apontar A record do subdomínio para IP da VPS
- `certbot --nginx -d scanner.seudominio.com` (renovação automática)
- Definir credencial via `htpasswd -c infra/nginx/htpasswd jackson`

## 11. Migração (do estado atual ao web app)

Ordem de implementação (cada item = 1 commit lógico):

1. **Refactor `postprocess`**: mover `scripts/postprocess_md.py` → `src/scanner/postprocess/__init__.py`. Atualizar imports onde o script é referenciado. CLI continua funcionando.
2. **Adicionar PDF export**: criar `src/scanner/export/pdf.py` (`write_pdf` via pandoc + xelatex). Estender `OutputFormat` enum (`PDF`, `ALL`). Atualizar `pipeline.scan()` para gerar PDF quando solicitado. Atualizar CLI flag (`-f all` substitui `-f both`, com warning de deprecation por 1 release).
3. **Skeleton `apps/api/`**: FastAPI app + lifespan + pool + DB + storage + 1º endpoint (`/api/health`). Smoke test local.
4. **Endpoints jobs**: POST/GET/PATCH/DELETE + WebSocket progress. Worker conectando à pool.
5. **Endpoints push**: VAPID + subscribe. Integração `pywebpush`.
6. **Skeleton `apps/web/`**: Next.js scaffold com 4 páginas, hooks vazios, Tailwind setup.
7. **Componentes UI**: DropZone, JobCard, ProgressBar, MarkdownPreview, AdvancedPanel, DownloadButtons, InstallPrompt.
8. **Hooks de dados**: useJobs, useJobProgress, usePush, useInstallPrompt — integrar com API.
9. **Service Worker**: install/fetch/sync/push handlers + IndexedDB queue.
10. **Manifest + ícones** + install banner iOS.
11. **`infra/`**: docker-compose, Dockerfiles, Nginx config, scripts.
12. **Smoke test local**: `docker compose -f infra/docker-compose.dev.yml up`. Subir foto, processar, baixar MD/DOCX/PDF.
13. **Deploy Hostinger**: clone, env vars, htpasswd, certbot, `docker compose up -d`.

## 12. Testes

- **Unit (existing)**: pytest em `tests/` — pipeline, engine, postprocess
- **Integration (novo)**: `apps/api/tests/test_jobs.py` — `httpx.AsyncClient` testando upload→queue→complete→download
- **WebSocket**: `apps/api/tests/test_ws.py` — conecta WS, dispara job mock, valida sequência de eventos
- **Frontend**: smoke testing via `next build` (TS strict + ESLint). E2E Playwright opcional, fora do MVP.
- **Cobertura mínima MVP**: 70% no backend, sem hard requirement no frontend (validado manualmente)

## 13. Riscos conhecidos e mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Hostinger banir long-running connections (WebSocket) | Baixa | Alto | Configurar Nginx `proxy_read_timeout 3600s`. Fallback: polling HTTP a cada 2s. |
| RAM insuficiente com 2 workers + Next.js + Nginx | Média | Alto | Monitorar `/api/health.disk_free_gb` + alarme. Reduzir para 1 worker se necessário. |
| iOS PWA não receber push se não instalado | Alta | Médio | Banner de instrução prominente. Email de feedback do usuário se instalado. |
| Pandoc/xelatex não renderizar caracteres específicos | Média | Médio | Fallback para weasyprint (Opção B do brainstorm). Testar com fontes Noto. |
| Upload de imagem 50MP travar request | Média | Médio | `client_max_body_size 200M`. Processamento async — request volta `202` rápido. |
| LGPD em fotos com dados pessoais | Média | Alto (legal) | Single-tenant + auto-purge 72h + HTTPS + basic auth. Termo "uso pessoal" no README. |

## 14. Open questions / iterações futuras

- **Multi-user**: tabela `users`, FK `user_id` em `jobs` e `push_subscriptions`, paths viram `/data/users/{user_id}/jobs/{job_id}/`
- **LLM fix-up**: pós-processador chama Claude API para casos ambíguos no markdown (ex.: detectar que "A0nipulação" deveria ser "Manipulação")
- **Editor inline**: textarea no preview para corrigir o MD antes de baixar DOCX/PDF
- **Notion / Obsidian sync**: enviar MD direto para vault remoto via API
- **GPU compartilhada via API externa**: opção "modo turbo" usa serviço pago (RunPod/Modal) por foto cara
- **Upload por URL**: cole URL de imagem na web → backend faz fetch → processa
- **Multi-page PDF input** com escolha de páginas a processar

## 15. Critérios de aceite do MVP

- [ ] Subir 1 foto pelo desktop → receber MD, DOCX, PDF zipados ou separados
- [ ] Subir 5 fotos → escolher merge → receber arquivo único consolidado em todos os formatos
- [ ] Repetir tudo acima pelo celular (Chrome Android E Safari iOS)
- [ ] Instalar como PWA, abrir da home screen, fazer conversão offline (queue) → ao voltar online, processa automaticamente
- [ ] Receber push notification quando job termina (Android nativo, iOS instalado)
- [ ] Marcar job como favorito → continuar disponível após 72h
- [ ] Job não-favoritado é apagado automaticamente após 72h (cron)
- [ ] Página `/api/health` mostra device correto (CPU em produção, GPU em dev local)
- [ ] CLI continua funcionando exatamente como antes (`scanner convert ...`)
- [ ] Acesso via Nginx basic auth — credenciais erradas = 401

## 16. Referências

- Frontend pattern reference: `C:\Users\jacks\OneDrive\IA\Antigravity\DocRAG-Web\frontend` (Next.js 15 + Tailwind 4 + lucide + react-dropzone + WebSocket pattern)
- HANDOFF do projeto: `docs/HANDOFF.md`
- Knowledge graph (snapshot pré-mudança): `graphify-out/graph.json`
- Brainstorm origem: skill `superpowers:brainstorming` invocada em 2026-05-02
