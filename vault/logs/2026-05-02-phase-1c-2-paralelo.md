---
title: 2026-05-02 — Phase 1C + Phase 2 em paralelo (subagentes)
tags: [log, sessao, fastapi, nextjs, push-notifications, vapid, paralelismo]
created: 2026-05-02
updated: 2026-05-02
status: closed
type: log
---

# 2026-05-02 — Phase 1C + Phase 2 em paralelo (subagentes)

## Objetivo da sessão

Executar Phase 1C (push notifications + PATCH/DELETE jobs + purge cron) e Phase 2 (frontend Next.js scaffold) em paralelo, aproveitando a separação de file ownership entre `apps/api/` e `apps/web/`.

## O que foi feito

### Phase 1C — Backend completion (subagente A, 4 commits)

- **`0b42efa`** — Web Push notifications:
  - `scripts/generate_vapid_keys.py` (gera par VAPID via cryptography)
  - `apps/api/src/scanner_api/push.py` (wrapper sobre `pywebpush.webpush()`, deleta sub em 410/404)
  - `apps/api/src/scanner_api/routes/push.py` (GET vapid-public-key, POST subscribe, DELETE unsubscribe)
  - Hook `_finalize_job` em `workers/pool.py` dispara push quando status=done
  - Bridge `asyncio.run_coroutine_threadsafe` entre ProcessPoolExecutor done-callback e o asyncio loop
  - Migration 0001 já tinha tabela `push_subscriptions` — sem nova migration
  - 9 testes em `test_push.py`

- **`1b3be27`** — PATCH/DELETE jobs:
  - `JobUpdate` schema (is_favorite, title, expires_at)
  - PATCH com side effect: `is_favorite=True` → `expires_at=NULL`
  - DELETE com `shutil.rmtree(missing_ok=True)` no diretório do job
  - 7 testes

- **`0894b2a`** — Purge cron:
  - `apps/api/src/scanner_api/tasks/purge_expired.py` com `__main__` callable
  - Query: `expires_at < now() AND is_favorite=False`
  - Idempotente (jobs já deletados não erram)
  - 2 testes

- **`b9a993e`** — Health expandido com `pending_purge` e `total_subscriptions`

**Resultado**: 62 → 82 testes passing (+20).

### Phase 2 — Frontend scaffold (subagente B, 5 commits)

- **`e785a3f`** — Scaffold:
  - `apps/web/` criado manualmente (sem `create-next-app` por causa de prompts interativos)
  - Next.js 15 + React 19 RC + TypeScript + Tailwind 4 beta + App Router
  - `next.config.ts` com rewrites `/api` → `localhost:8000` em dev
  - Deps: lucide-react, react-dropzone, sonner, clsx, tailwind-merge

- **`f752519`** — Lib core:
  - `lib/types.ts` (espelha schemas Pydantic)
  - `lib/api.ts` (typed client: getHealth, listJobs, getJob, createJob, patchJob, deleteJob, fileUrl)
  - `lib/ws.ts` (WS wrapper com reconexão exponencial)
  - `lib/cn.ts` (clsx + tailwind-merge)

- **`cf2abc8`** — Componentes UI:
  - StatusBadge, ProgressBar, JobCard, DropZone, Spinner

- **`875df7e`** — Páginas:
  - `/` Dashboard (dropzone + opções + POST /api/jobs)
  - `/jobs` lista com filtros e paginação
  - `/jobs/[id]` detalhe com WebSocket ao vivo
  - `/health` JSON renderizado

- **`3f6567a`** — Docs (apps/web/README, root README mention, TODO Phase 2 progress)

### Fixes pós-build (commit `b5b8615`)

Após instalar deps e rodar build, dois problemas surgiram:

1. **ERESOLVE** — `react-dropzone@14.4.1` declara peer `react ">= 16.8 || 18.0.0"` (não inclui React 19 RC). Solução: `apps/web/.npmrc` com `legacy-peer-deps=true`.
2. **CVE-2025-66478** — Next.js 15.0.3 tem vulnerabilidade. Bump para `^15.5.0` (resolveu para 15.5.15).

Build verde:
```
Route (app)              Size   First Load JS
○ /                    19.5 kB        138 kB
○ /_not-found            991 B        103 kB
○ /health              1.33 kB        111 kB
○ /jobs                2.82 kB        116 kB
ƒ /jobs/[id]           3.54 kB        122 kB
+ shared                              102 kB
```

## Decisões tomadas

- **Paralelismo via subagentes**: dois agentes simultâneos em diretórios disjuntos (`apps/api/` vs `apps/web/`) — zero overlap, commits intercalados mas atômicos com prefixos `feat(api):` / `feat(web):`.
- **ProcessPool → asyncio bridge**: `asyncio.run_coroutine_threadsafe` no `_finalize_job` é a forma correta de fazer trabalho async dentro de done-callback do ProcessPoolExecutor.
- **Frontend sem create-next-app**: scaffold manual evita prompts interativos e dá controle exato sobre versões. Trade-off: precisa configurar `next-env.d.ts`, `postcss.config.mjs`, etc à mão.
- **Build sem `npm install` no agente**: agente B só preparou config; verificação real do build foi feita posteriormente. Pegou problemas (ERESOLVE + CVE) que teriam sido invisíveis dentro do agente.
- **`legacy-peer-deps=true` permanente** no `.npmrc`: enquanto algumas libs (react-dropzone) não atualizam peers para React 19. Quando libs atualizarem, podemos remover.

## Arquivos modificados / criados

### Backend Phase 1C
- `scripts/generate_vapid_keys.py`
- `apps/api/src/scanner_api/push.py`
- `apps/api/src/scanner_api/routes/push.py`
- `apps/api/src/scanner_api/tasks/__init__.py`
- `apps/api/src/scanner_api/tasks/purge_expired.py`
- `apps/api/src/scanner_api/main.py` (registers push_router)
- `apps/api/src/scanner_api/routes/__init__.py` (exports push_router)
- `apps/api/src/scanner_api/routes/jobs.py` (PATCH/DELETE)
- `apps/api/src/scanner_api/routes/health.py` (pending_purge + total_subscriptions)
- `apps/api/src/scanner_api/schemas.py` (JobUpdate)
- `apps/api/src/scanner_api/workers/pool.py` (_finalize_job + push dispatch)
- `apps/api/tests/test_push.py` (9 tests)
- `apps/api/tests/test_jobs_mutations.py` (7 tests)
- `apps/api/tests/test_purge_expired.py` (2 tests)
- `apps/api/tests/test_health.py` (+1 test)

### Frontend Phase 2
- `apps/web/package.json`, `tsconfig.json`, `next.config.ts`, `postcss.config.mjs`, `next-env.d.ts`, `.gitignore`, `.env.local.example`, `.npmrc`, `package-lock.json`, `README.md`
- `apps/web/lib/{types,api,ws,cn}.ts`
- `apps/web/components/{StatusBadge,ProgressBar,JobCard,DropZone,Spinner}.tsx`
- `apps/web/app/{layout,page,globals.css}`
- `apps/web/app/jobs/{page,[id]/page}.tsx`
- `apps/web/app/health/page.tsx`

### Root
- `.gitignore` (+`pytest-of-*/`, +`node_modules/`, +`.next/`)
- `README.md` (mention apps/web)
- `TODO.md` (Phase 2 progress)

## Resultado

- ✅ 82 testes backend passing (8.95s)
- ✅ 0 testes frontend ainda (Vitest/Playwright fica para Phase 3)
- ✅ Backend Phase 1C: push + PATCH/DELETE + purge cron + health expandido
- ✅ Frontend Phase 2: scaffold + lib + componentes + 4 páginas, build Next 15.5.15 verde
- ✅ Graphify: 4820 nodes / 20333 edges / 142 communities (+153 nodes, +346 edges, +82 communities)
- ✅ 11 commits novos na branch `feat/phase-0-backend-refactor`
- ⏭️ Push e PR pendentes (decisão do usuário)

## Pendências / próximos passos

- [ ] Rodar dev server backend + frontend juntos e validar fluxo end-to-end manualmente
- [ ] Rodar `python -m scanner_api.tasks.purge_expired` em ambiente de teste (idempotência)
- [ ] Phase 3: PWA (service worker + manifest + push UI client-side)
- [ ] Phase 4: Docker Compose + nginx + Hostinger
- [ ] Backlog: Vitest + Playwright tests para frontend
- [ ] Decisão: i18n? auth? hosting final? (ver TODO § Decisões)
- [ ] Abrir PR `feat/phase-0-backend-refactor` → `master`

## Links

- [[../projeto/decisoes]]
- [[../projeto/arquitetura]]
- [[../../docs/HANDOFF]]
- [[../../TODO]]
- [[2026-05-02-phases-1a-1b-completas]] (sessão anterior)
