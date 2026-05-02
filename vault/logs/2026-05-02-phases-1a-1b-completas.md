---
title: 2026-05-02 — Phases 1A + 1B completas + docs renovadas
tags: [log, sessao, fastapi, websocket, docs, handoff]
created: 2026-05-02
updated: 2026-05-02
status: closed
type: log
---

# 2026-05-02 — Phases 1A + 1B completas + docs renovadas

## Objetivo da sessão

Continuar do ponto em que Phase 1B Task 4 (WebSocket) estava in_progress — finalizar Task 4, fazer Task 5 (download files), atualizar Graphify, push para remoto, e renovar toda a documentação (HANDOFF + criar TODO).

## O que foi feito

### Phase 1B Task 4 — WebSocket /ws/jobs/{id} (commit `46d2fe1` aprox)
- `routes/ws.py`: handler com `WebSocketDisconnect` tratado + `contextlib.suppress(RuntimeError)` no close idempotente
- `ProgressBroker.stream()` consumido como async generator
- 3 testes via `starlette.testclient.TestClient`: streams events, terminate on error, timeout for nonexistent job

### Phase 1B Task 5 — GET /api/jobs/{id}/files/{filename} (commit `eac6dee`)
- `routes/files.py`: procura em `outputs/`, `images/`, `inputs/` (ordem prioridade)
- Path traversal protection: `candidate.resolve().relative_to(base.resolve())` rejeita `../scanner.db`
- Content-Disposition: attachment força download
- 6 testes: 404 job/arquivo inexistente, download de input/output, path traversal blocked (URL-encoded), prioridade outputs > inputs

### Final review Phase 1B
- 62 testes passing no apps/api (settings, storage, db_models, health, progress, workers, jobs_api, ws, files)
- Ruff clean
- Graphify update: 4667 nodes / 19987 edges / 60 communities
- Push para `origin/feat/phase-0-backend-refactor`

### Documentação renovada
- **docs/HANDOFF.md**: reescrito do zero (~1000 linhas → ~600 linhas mais densas e factuais). Estrutura completa: visão geral, arquitetura, monorepo, stack, instalação, CLI, API endpoints, pós-processador, testes, performance, decisões, troubleshooting, histórico de fases, link para TODO.
- **TODO.md** (novo na raiz): roadmap completo Phase 1C, 2, 3, 4 + backlog (quality-of-life, observability, segurança, refactor) + decisões pendentes + concluído (referência).
- **README.md**: reescrito apontando para HANDOFF, com tabela de status por componente, quickstart CLI + Backend, endpoints, performance, estrutura.
- **CLAUDE.md** (raiz): expandida seção "Estrutura do projeto" para refletir `apps/api/`. Adicionada seção "Comandos importantes".

## Decisões tomadas

- **HANDOFF separado de TODO**: HANDOFF descreve estado factual atual; TODO descreve o que falta. Quando linha do TODO é riscada → vira parágrafo no HANDOFF. Evita docs aspiracional que envelhece mal.
- **Branch única `feat/phase-0-backend-refactor`** para todas as fases até abrir PR final. Cada fase é uma série atômica de commits com prefixo (`feat(api):`, `chore(graphify):`, `docs(plan):`).
- **WebSocket via TestClient síncrono**: httpx async não suporta WS — Starlette TestClient é a saída idiomática para tests.
- **Path traversal**: `resolve().relative_to(base)` em vez de regex de `..` é mais robusto (cobre URL encoding, symlinks, paths absolutos).

## Arquivos modificados / criados

### Phase 1B
- `apps/api/src/scanner_api/routes/ws.py` (criado)
- `apps/api/src/scanner_api/routes/files.py` (criado)
- `apps/api/src/scanner_api/routes/__init__.py` (atualizado: ws_router, files_router)
- `apps/api/src/scanner_api/main.py` (atualizado: include_router)
- `apps/api/tests/test_ws.py` (criado)
- `apps/api/tests/test_files.py` (criado)

### Docs
- [[../../docs/HANDOFF]] (reescrito)
- [[../../TODO]] (novo)
- `README.md` (reescrito)
- [[../CLAUDE]] (atualizado)

### Graphify
- `graphify-out/graph.json`, `graph.html`, `GRAPH_REPORT.md` (atualizado)

## Resultado

- ✅ 110 testes passing total (48 core + 62 api)
- ✅ Ruff clean em ambos os pacotes
- ✅ Backend MVP completo: workers + jobs CRUD + WebSocket + downloads
- ✅ Push para origin (24 commits ahead of master)
- ✅ Docs em estado factualmente correto (HANDOFF) + roadmap claro (TODO)

## Pendências / próximos passos

- [ ] Phase 1C: push notifications + purge cron + PATCH/DELETE
- [ ] Phase 2: frontend Next.js (consome a API atual)
- [ ] Decidir auth, hosting final, design tokens — ver TODO § "Decisões a tomar"
- [ ] Abrir PR `feat/phase-0-backend-refactor` → `master`

## Links

- [[../projeto/decisoes]]
- [[../projeto/arquitetura]]
- [[../../docs/HANDOFF]]
- [[../../TODO]]
- [[2026-05-02-bootstrap-mvp]] (sessão anterior)
- [[2026-05-02-handoff-and-github]] (sessão anterior)
