#!/usr/bin/env bash
set -euo pipefail

# Apply DB migrations before starting the API.
# Idempotent: alembic upgrade head is safe to run repeatedly.
echo "[entrypoint] Running alembic upgrade head..."
cd /app/apps/api
alembic upgrade head
cd /app

echo "[entrypoint] Starting uvicorn..."
exec "$@"
