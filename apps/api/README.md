# scanner-api

FastAPI backend for **Scanner de Imagens** — exposes the OCR pipeline as a single-tenant web API with async jobs, WebSocket progress, and push notifications.

## Status

**Phase 1A** — backend foundation (skeleton, settings, storage, DB, `/api/health`).

Following phases:
- **Phase 1B** — worker pool + jobs CRUD + WebSocket
- **Phase 1C** — push notifications + purge cron

See `docs/superpowers/specs/2026-05-02-web-app-pwa-design.md` for full architecture.

## Architecture

- **FastAPI 0.115+** with async lifespan
- **SQLAlchemy 2.0 + aiosqlite** for async ORM on SQLite
- **Alembic** for schema migrations
- **ProcessPoolExecutor** isolates Docling-heavy worker processes from event loop
- **WebSocket** for live job progress (Phase 1B)
- **Web Push (VAPID)** for completion notifications (Phase 1C)

The API consumes [`scanner`](../../src/scanner/) as a library (no fork of OCR logic).

## Development

From the **monorepo root**:

```bash
# Install both packages as editable
pip install -e .              # scanner core
pip install -e ./apps/api     # scanner-api

# Run dev server (requires VAPID stub env vars; see settings.py)
SCANNER_DATA_DIR=/tmp/scanner \
SCANNER_VAPID_PUBLIC_KEY=stub \
SCANNER_VAPID_PRIVATE_KEY=stub \
SCANNER_VAPID_EMAIL=t@e.com \
uvicorn scanner_api.main:app --reload --port 8000

# Tests
cd apps/api && pytest
```

## Production

`Dockerfile` produces a single image with pandoc + texlive-xetex + tesseract for the full OCR + export toolchain. Deploy via `infra/docker-compose.yml` (Phase 4).

## License

MIT
