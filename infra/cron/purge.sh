#!/usr/bin/env bash
# Purge expired jobs (artifacts past retention TTL).
# Schedule via cron (see infra/README.md), e.g. daily at 04:00.
set -euo pipefail

cd "$(dirname "$0")/../.."
docker compose -f infra/docker-compose.yml exec -T api python -m scanner_api.tasks.purge_expired
