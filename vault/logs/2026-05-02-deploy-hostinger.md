---
title: 2026-05-02 — Deploy production em scan.jacksonuti.cloud
tags: [log, sessao, deploy, hostinger, vps, docker, nginx, certbot, ssl]
created: 2026-05-02
updated: 2026-05-02
status: closed
type: log
---

# 2026-05-02 — Deploy production em scan.jacksonuti.cloud

## Objetivo

Subir o Scanner de Imagens em produção: VPS Hostinger compartilhada + nginx do host + Docker compose para api+web + SSL Let's Encrypt + DNS via API Hostinger.

## URL de produção

https://scan.jacksonuti.cloud — backend MVP completo (CLI + API + WS + push + PWA).

## Arquitetura final

```
┌─────────────────────────────────────────────────────────┐
│  Hostinger VPS srv1327529 (168.231.93.16, Ubuntu 6.8)   │
│  4 vCPU · 15 GiB RAM · 193 GB / · CPU only (no GPU)     │
│                                                         │
│  nginx host (1.24)                                      │
│  ├── docrag.jacksonuti.cloud → 127.0.0.1:8005          │
│  ├── prompts.jacksonuti.cloud, sibicc.j.c, etc.        │
│  └── scan.jacksonuti.cloud (NEW) ──┐                    │
│                                     │                    │
│  Docker compose (host-nginx variant)│                    │
│  ├── infra-web-1   ─ 127.0.0.1:3000 ◄ /, /jobs, etc.   │
│  └── infra-api-1   ─ 127.0.0.1:8000 ◄ /api/, /ws/      │
│                      └─ volume ./data:/data            │
└─────────────────────────────────────────────────────────┘
```

## Decisões tomadas

- **Compartilhar nginx do host** em vez de subir nginx no compose — evita conflito de portas 80/443 com os 8 outros subdomains já hospedados.
- **`docker-compose.host-nginx.yml`** — variante sem o serviço nginx, expõe api/web em `127.0.0.1:8000` e `127.0.0.1:3000` apenas (não acessíveis externamente, só via nginx host).
- **DNS via API REST da Hostinger** — `PUT /api/dns/v1/zones/{domain}` com Personal Access Token. Schema: `{ overwrite: false, zone: [{ name: "scan", type: "A", ttl: 14400, records: [{ content: IP }] }] }`. Resposta `200 — Request accepted`.
- **`scripts/generate_vapid_keys.py` rodado localmente**, chaves gravadas em `infra/.env` na VPS com chmod 600. **NÃO** commitadas.
- **Certbot --nginx --redirect** — issue + auto-instalação no site existente em uma chamada. Redirect 301 HTTP→HTTPS automático.
- **Frontend usa paths relativos** (lib/api.ts não usa NEXT_PUBLIC_API_BASE_URL, ws.ts usa `window.location.host`) — same-origin via nginx funciona sem rebuild com URL hardcoded.

## O que foi feito (cronologia)

1. **Probe SSH** — VPS já tem Docker 29.3.1, Compose v5.1.1, nginx 1.24, certbot 2.9.0, 8 sites configurados.
2. **Análise do padrão docrag** — ler `/etc/nginx/sites-enabled/docrag` para replicar estilo (proxy_pass + WebSocket headers + timeouts).
3. **Repo clonado** em `/opt/scanner-de-imagens` na branch `feat/phase-0-backend-refactor` (commit `40fbe98`).
4. **VAPID keys** geradas localmente, gravadas em `/opt/scanner-de-imagens/infra/.env`.
5. **`docker-compose.host-nginx.yml` + `infra/nginx-site/scan.jacksonuti.cloud`** criados localmente, commitados (`40fbe98`), pushed.
6. **DNS A record** criado via Hostinger REST API: `scan.jacksonuti.cloud → 168.231.93.16`. Verificado via `nslookup ... 1.1.1.1` — propagou imediatamente.
7. **Nginx site** copiado para `/etc/nginx/sites-{available,enabled}/`, `nginx -t` OK, `systemctl reload nginx` OK.
8. **Docker build** em background — ~10 min (Python 3.13-slim + Docling + texlive-xetex + tesseract-por). Resultado: `scanner-api:local`, `scanner-web:local`.
9. **`docker compose up -d`** — containers up em 8s, health: `device=cpu`, version 0.1.0.
10. **Certbot** — `--nginx -d scan.jacksonuti.cloud --redirect --email jacksontorax@gmail.com`. Cert expira 2026-07-31, auto-renew configurado.
11. **Smoke test externo** — HTTPS api/health → 200 JSON, HTTPS / → 200 (20 KB), HTTP → 301 → HTTPS.

## Arquivos novos commitados

- `infra/docker-compose.host-nginx.yml` (sem serviço nginx, ports em 127.0.0.1)
- `infra/nginx-site/scan.jacksonuti.cloud` (template HTTP-only; certbot enriquece com SSL)

Commit: `40fbe98` `feat(infra): host-nginx variant + scan.jacksonuti.cloud nginx site`

## Resultado

- ✅ Deploy completo em produção
- ✅ HTTPS válido (Let's Encrypt, expira 2026-07-31)
- ✅ HTTP→HTTPS 301 redirect
- ✅ API + frontend + WebSocket todos acessíveis pelo subdomain único
- ✅ Auto-renew de cert configurado pelo certbot
- ✅ Containers `restart: unless-stopped` — sobrevivem reboot

## Pendências / próximos passos

- [ ] **Revogar o Personal Access Token Hostinger** usado para criar o DNS — está visível no histórico desta sessão. hPanel → Profile → API → Revoke.
- [ ] Cron diário para `python -m scanner_api.tasks.purge_expired` dentro do container (ou criar `infra/cron/purge.sh` adaptado para o host)
- [ ] Backup automatizado de `/opt/scanner-de-imagens/infra/data/scanner.db`
- [ ] Decidir auth (single-user vs multi-user) — VPS é hoje completamente aberta
- [ ] Rate limiting no nginx (slowapi backend ou nginx limit_req)
- [ ] PR `feat/phase-0-backend-refactor` → `master`
- [ ] Monitoring/observability (logs estruturados, talvez Grafana)

## Custos & limites

- Disco da VPS: caiu de 49 GB livres → 38 GB pós build → 42 GB após cleanup; PyTorch CPU + texlive consomem ~10 GB
- Performance: CPU only → ~35s/foto (vs ~5s na máquina local com RTX 3060). 69 fotos = ~40 min na VPS
- VAPID keys: gravadas só em `infra/.env` (chmod 600), NÃO no git

## Links

- https://scan.jacksonuti.cloud — produção
- https://scan.jacksonuti.cloud/api/docs — Swagger UI
- [[2026-05-02-phase-4-infra]] (sessão anterior — preparou infra/)
- [[../../docs/HANDOFF]]
