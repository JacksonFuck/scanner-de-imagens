# TODO — Scanner de Imagens

> Roadmap do que ainda falta. Quando uma linha é riscada aqui, o conteúdo correspondente vira parágrafo factual em [docs/HANDOFF.md](docs/HANDOFF.md).

**Última atualização**: 2026-05-02 (post-Phase 1B)
**Estado**: Backend MVP completo (CLI + API + Workers + WebSocket + downloads). Falta frontend, push, deploy.

---

## 🚀 Phase 1C — Backend completion (~3-4h, ~7 tasks)

> **Status**: Plano não escrito ainda. Pronto para começar quando aprovado.

### Push notifications (Web Push + VAPID)
- [ ] `scripts/generate_vapid_keys.py` — gera par de chaves VAPID base64url uma vez
- [ ] `scanner_api/push.py` — wrapper sobre `pywebpush.webpush()` com retry
- [ ] `scanner_api/routes/push.py`:
  - [ ] `GET /api/push/vapid-public-key` — retorna chave pública
  - [ ] `POST /api/push/subscribe` — grava `PushSubscription` no DB
  - [ ] `DELETE /api/push/unsubscribe` — remove por endpoint
- [ ] Hook no `pool._on_job_done`: enviar notificação push quando `status='done'`
  - [ ] Construir payload: `{ "title": "Job concluído", "body": "<n> páginas em <X>s", "url": "/jobs/<id>" }`
  - [ ] Iterar todas `PushSubscription` no DB
  - [ ] Tratar 410/404 (subscription expirada) → deletar do DB
- [ ] Tests: keys obrigatórias, subscribe persiste, unsubscribe deleta, payload correto

### Mutations no Job (PATCH/DELETE)
- [ ] `PATCH /api/jobs/{id}`:
  - [ ] Body: `{ "is_favorite": 0|1, "title": "...", "expires_at": null|"..." }`
  - [ ] Side effect: se `is_favorite=1`, setar `expires_at = NULL` (job nunca expira)
- [ ] `DELETE /api/jobs/{id}`:
  - [ ] Cascade: deleta `JobFile` (já configurado no ORM) + remove pasta `/data/jobs/{id}/`
  - [ ] 204 No Content
  - [ ] 404 se job não existe
- [ ] Tests: toggle favorite, rename, expires_at NULL ao favoritar, delete cascata em disco

### Purge cron
- [ ] `scanner_api/tasks/purge_expired.py`:
  - [ ] Query: `SELECT * FROM jobs WHERE expires_at < NOW() AND is_favorite = 0`
  - [ ] Para cada job: deleta DB + filesystem
  - [ ] Idempotente (jobs já deletados não dão erro)
- [ ] Entry point: `python -m scanner_api.tasks.purge_expired`
- [ ] Documentar no Dockerfile/compose: cron diário às 4h
- [ ] Tests: jobs expirados removidos, favoritos preservados, idempotência

### Health endpoint expandido (post-Phase 1C)
- [ ] Adicionar `pending_purge` (count de jobs prontos para purga)
- [ ] Adicionar `total_subscriptions` (push subs ativas)

---

## 🎨 Phase 2 — Frontend Next.js (~6-8h, ~10 tasks)

> Spec: `docs/superpowers/specs/2026-05-02-web-app-pwa-design.md` Section 8

### Setup
- [ ] Scaffolding `apps/web/` com Next.js 15 + App Router + TypeScript
- [ ] Tailwind 4 + design tokens (cores, spacing — ref `vault/projeto/design.md`)
- [ ] Configurar proxy `/api` e `/ws` para localhost:8000 em dev (`next.config.ts`)
- [ ] Variáveis: `NEXT_PUBLIC_API_BASE_URL`

### Componentes core
- [ ] `lib/api.ts` — typed client gerado a partir de `JobSummary`/`JobDetail`/etc (manual, sem openapi-codegen no MVP)
- [ ] `lib/ws.ts` — wrapper sobre WebSocket com reconexão exponencial
- [ ] `lib/upload.ts` — multipart com progresso (XHR para suportar onProgress)

### Páginas
- [ ] `/` — Dashboard:
  - [ ] Drop zone (react-dropzone) com preview thumbnails
  - [ ] Toggle merge / formatos (`md` | `docx` | `pdf` | `all`)
  - [ ] Painel "Avançado" colapsável (OCR engine, lang, device)
  - [ ] Botão "Iniciar" → POST /api/jobs → redirect para `/jobs/<id>`
- [ ] `/jobs` — Lista:
  - [ ] Filtros: ativos/concluídos/favoritos
  - [ ] Card por job: thumb da 1ª foto, título, status badge, tempo decorrido
  - [ ] Pull-to-refresh + paginação infinita
- [ ] `/jobs/<id>` — Detalhe:
  - [ ] Conexão WS para progresso ao vivo
  - [ ] Lista de files com download (link direto)
  - [ ] Botões: Favoritar (PATCH), Deletar (DELETE), Compartilhar (Web Share API)
- [ ] `/health` (admin/debug) — JSON do `/api/health` com graceful loading

### UX
- [ ] Loading states (skeleton)
- [ ] Toast de erro genérico (Sonner)
- [ ] Confirmação de delete via modal
- [ ] Dark mode opcional

### Tests
- [ ] Vitest + Testing Library para 5-10 componentes críticos
- [ ] Playwright E2E: upload + ver progresso + download (mockando backend)

---

## 📱 Phase 3 — PWA (~3h, ~5 tasks)

> Spec: Section 9

- [ ] `public/manifest.json` (name, short_name, theme_color, icons 192/512)
- [ ] `public/sw.ts` — Service Worker:
  - [ ] Cache estratégia `network-first` para `/api/*`
  - [ ] Cache `cache-first` para assets estáticos (`_next/static`)
  - [ ] Listener `push` → `Notification.show()`
  - [ ] Listener `notificationclick` → abre `/jobs/<id>`
- [ ] Componente `<InstallPrompt>` (beforeinstallprompt event)
- [ ] Componente `<EnablePush>` — pede permissão + assina + envia para `POST /api/push/subscribe`
- [ ] Tests: SW registra, push notification chega, deep link abre tela certa

---

## 🚢 Phase 4 — Deploy Hostinger (~4h, ~6 tasks)

> Spec: Section 10

### Infra
- [ ] `infra/docker-compose.yml`:
  - [ ] Service `api` (apps/api/Dockerfile, expõe 8000, monta `./data:/data`)
  - [ ] Service `web` (apps/web/Dockerfile, expõe 3000)
  - [ ] Service `nginx` (reverse proxy, SSL via Let's Encrypt)
- [ ] `infra/nginx/scanner.conf` — proxy `/api` e `/ws` para api:8000, demais para web:3000
- [ ] `infra/cron/purge.sh` — chamada diária `docker compose exec api python -m scanner_api.tasks.purge_expired`

### Setup VPS
- [ ] Instalar Docker + Compose no VPS Hostinger
- [ ] Domínio + DNS apontando
- [ ] Certbot + auto-renew
- [ ] Backup script `/data/scanner.db` (cron diário)
- [ ] Monitoring básico: log to file + alerting opcional

### CI/CD
- [ ] GitHub Actions: build Docker images on push to `master`
- [ ] Workflow de deploy via SSH (rsync ou docker-compose pull + up -d)

---

## 🔧 Backlog (não-prioridade, mas valioso)

### Quality of life
- [ ] CHANGELOG.md em formato Keep-a-Changelog
- [ ] Badges no README (build, license, version, py3.13)
- [ ] Pre-commit hooks (`ruff`, `mypy`, no-large-files)
- [ ] Coverage report no CI + threshold 85%
- [ ] mypy strict completo (atualmente só `src/scanner` — `apps/api` ainda permissivo)

### Funcionalidade
- [ ] CLI: `--scale` configurável (atualmente fixado em 3.0 no engine)
- [ ] Pré-processamento de imagens curvadas (deskew/dewarp via Pillow)
- [ ] Suporte a outros formatos: scanner físico (TWAIN/WIA), webcam capture
- [ ] Pipeline com múltiplos OCR engines em paralelo + voting
- [ ] Integração Claude API para revisão semântica do markdown final

### Observability
- [ ] Logs estruturados (JSON) para produção
- [ ] Tracing OpenTelemetry (pelo menos `POST /api/jobs` → worker)
- [ ] Métricas Prometheus (queue_depth, jobs_done, errors_total)
- [ ] Dashboard Grafana

### Segurança
- [ ] Rate limiting (slowapi ou nginx)
- [ ] Auth: API key simples ou OAuth (single-tenant não precisa, mas boom-day)
- [ ] CSP headers no nginx
- [ ] Audit log de operações sensíveis (DELETE jobs)

### Docs
- [ ] Tutorial passo-a-passo: "Do zero ao primeiro job em 10 minutos"
- [ ] Vídeo demo (gif animado no README)
- [ ] OpenAPI export → Swagger UI no `/api/docs`
- [ ] Diagrama Mermaid da arquitetura no README

### Refactor / dívidas técnicas
- [ ] `_path_safe_dict` em `workers/pool.py` — pode usar `pydantic_core.to_jsonable_python()`
- [ ] `progress.py:signal()` está sendo importado mas pouco usado — avaliar remover ou conectar com worker subprocess
- [ ] `apps/api/tests/test_db_models.py` warning de "identity key conflict" — refactor da fixture

---

## 🤔 Decisões a tomar

Coisas que precisam validação humana antes de codar:

- [ ] **Sistema de autenticação**: necessário no MVP? (single-user vs multi-user)
- [ ] **Escolha de hosting**: Hostinger VPS é confirmado? Ou Render/Fly.io?
- [ ] **Domínio**: comprar agora ou usar subdomain?
- [ ] **Push notifications**: realmente necessárias no MVP? (alternativa: poll com badge)
- [ ] **Tema**: design tokens vão para um lugar canônico? (Tailwind config vs CSS vars vs tokens.json)
- [ ] **i18n**: PT-BR only ou bilingue (PT + EN)?
- [ ] **PDF compression**: gerar PDF em "tamanho original" ou comprimir? (impacta storage)

---

## ✅ Concluído (referência rápida)

- [x] Phase 0 — Backend refactor + PDF export + OutputFormat.ALL (5 commits)
- [x] Phase 1A — FastAPI foundation: skeleton, settings, storage, DB, /api/health (6 commits)
- [x] Phase 1B — Workers + Jobs CRUD + WebSocket + downloads (5 commits + graphify)
- [x] Knowledge graph (Graphify) — 4667 nodes, 19987 edges
- [x] Vault Obsidian + slash commands (`/retomar`, `/salvar`)
- [x] Pipeline import de chats Claude → Obsidian
- [x] Pós-processador PT-BR (~150 palavras)
- [x] GPU support (PyTorch cu128)
- [x] OCR PT explícito (`lang=['pt','en']`)
- [x] Tesseract como engine alternativo
- [x] 110 testes passing (~12s combinado, sem Docling real)
- [x] Repositório público no GitHub
