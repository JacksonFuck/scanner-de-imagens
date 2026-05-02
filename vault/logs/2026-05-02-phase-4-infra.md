---
title: 2026-05-02 — Phase 4 infra (docker-compose + nginx + GHA)
tags: [log, sessao, docker, nginx, ci, deploy]
created: 2026-05-02
updated: 2026-05-02
status: closed
type: log
---

# 2026-05-02 — Phase 4 infra (docker-compose + nginx + GHA)

## Objetivo

Preparar todo o ferramental de deploy local-ready (qualquer VPS Linux) sem amarrar a Hostinger ainda. Decisões de hosting/domínio/auth ficam para depois.

## O que foi feito (4 commits)

- **`7724902`** `feat(infra)`: `apps/web/Dockerfile` multi-stage (deps → builder → runner) com node:22-alpine + Next.js standalone. `apps/web/.dockerignore`, `apps/web/next.config.ts` ganha `output: "standalone"`.
- **`02fd586`** `feat(infra)`: `infra/docker-compose.yml` (api + web + nginx, healthcheck via urllib em vez de curl), `infra/.env.example` (DOMAIN + 3 VAPID), `infra/nginx/scanner.conf` (HTTP→HTTPS + /api proxy + /ws proxy com Upgrade headers + 100M body), `infra/cron/purge.sh`, `infra/README.md`.
- **`a6ebe40`** `feat(ci)`: `.github/workflows/ci.yml` — backend pytest+ruff || frontend next build em paralelo.
- **`89d5b96`** `docs(infra)`: TODO + README + HANDOFF status updates.

## Decisões

- **Web Dockerfile com Next standalone**: imagem final ~150MB vs ~400MB do mode default. Standalone copia só `.next/standalone` + `public/` + `.next/static`.
- **Healthcheck via Python urllib**: imagem da api não tem curl/wget. `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"` funciona com a stdlib que já está instalada.
- **`${DOMAIN}` literal no nginx.conf**: nginx não interpola env vars em config files por default. README documenta `sed -i "s/\${DOMAIN}/seudominio.com/g" infra/nginx/scanner.conf` ou `envsubst` no deploy.
- **WebSocket proxy**: `proxy_http_version 1.1` + `Upgrade $http_upgrade` + `Connection "upgrade"` + `proxy_read_timeout 3600s` (1h, suficiente para job de OCR longo).
- **Cron entry NÃO instalada automaticamente**: `infra/cron/purge.sh` é só o script. Instalação da entry crontab fica como passo manual no README — preserva controle do operador.
- **GHA sem deploy**: workflow só faz build/test em paralelo. Deploy job fica para quando hosting estiver decidido (precisa de SSH key + secrets).

## Resultado

- ✅ Build frontend ainda passa pós `output: "standalone"` (verificado)
- ✅ Stack docker-compose pronta: `cd infra && cp .env.example .env && docker compose up -d`
- ✅ CI no GitHub vai rodar testes + build em todo PR/push
- ✅ Graphify: 4833 nodes / 20343 edges / 75 communities (mudanças de infra são YAML/conf, não geram nodes)
- ⏭️ VPS setup é manual (DNS, certbot, secrets) — README cobre

## Manual follow-ups para o usuário

1. `chmod +x infra/cron/purge.sh` no host Linux
2. `python scripts/generate_vapid_keys.py` → preencher `infra/.env`
3. Comprar domínio + apontar DNS A-record para o VPS
4. Instalar Docker + Compose no VPS
5. Certbot para SSL inicial (snippet no `infra/README.md`)
6. `sed`/`envsubst` para substituir `${DOMAIN}` em `infra/nginx/scanner.conf`
7. Cron entry diária para `purge.sh` (4h sugerido)
8. Backup script para `/data/scanner.db`
9. Quando decidir hosting: adicionar workflow de deploy no GHA + secrets

## Pendências

- [ ] PR `feat/phase-0-backend-refactor` → `master` (decisão do usuário)
- [ ] Decidir hosting (Hostinger/Render/Fly.io)
- [ ] Decidir auth no MVP (single-user vs multi-user)
- [ ] PNG icons raster para PWA em iOS antigo
- [ ] Tests E2E Playwright
- [ ] Workflow de deploy no GHA (depende de hosting)

## Links

- [[2026-05-02-phase-3-pwa]] (sessão anterior)
- [[../../TODO]]
- [[../../docs/HANDOFF]]
- [[../../infra/README]]
