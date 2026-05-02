# Scanner de Imagens — Infra

Local-ready stack for any Linux VPS. Three containers (api + web + nginx) orchestrated via docker-compose. Hosting/domain not assumed — substitute `${DOMAIN}` in `nginx/scanner.conf` and `.env` per deployment.

## Quickstart (local)

```bash
cd infra
cp .env.example .env
# Edit .env: set DOMAIN, generate VAPID keys.
docker compose up -d --build
```

API: `http://localhost/api/health`. Frontend: `http://localhost/`.

For local dev without TLS, comment out the `443` server block in `nginx/scanner.conf` and the redirect in the `:80` block.

## VAPID key generation

```bash
npx web-push generate-vapid-keys
# or
python -c "from py_vapid import Vapid01; v=Vapid01(); v.generate_keys(); print('PRIV:', v.private_pem().decode()); print('PUB:', v.public_pem().decode())"
```

Paste into `.env` (`SCANNER_VAPID_PUBLIC_KEY`, `SCANNER_VAPID_PRIVATE_KEY`, `SCANNER_VAPID_EMAIL`).

## HTTPS via Certbot (one-time)

After DNS A-record points to the VPS:

```bash
# 1. Boot stack with HTTP-only nginx temporarily (comment :443 server block)
docker compose up -d nginx

# 2. Issue cert
docker run --rm \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d "${DOMAIN}" \
  --email admin@${DOMAIN} --agree-tos --no-eff-email

# 3. Substitute ${DOMAIN} in nginx/scanner.conf, restore :443 block, reload
sed -i "s/\${DOMAIN}/${DOMAIN}/g" nginx/scanner.conf
docker compose restart nginx
```

Renewal: `docker run --rm -v ...:/etc/letsencrypt -v ...:/var/www/certbot certbot/certbot renew` (cron weekly).

## Cron — purge expired jobs

```bash
chmod +x infra/cron/purge.sh
crontab -e
# Append:
0 4 * * * /path/to/repo/infra/cron/purge.sh >> /var/log/scanner-purge.log 2>&1
```

## Backup `/data/scanner.db`

```bash
# Daily backup at 03:00, keep 14 days
0 3 * * * cp /path/to/repo/infra/data/scanner.db /backups/scanner-$(date +\%F).db && find /backups -name 'scanner-*.db' -mtime +14 -delete
```

## Logs

```bash
docker compose -f infra/docker-compose.yml logs -f          # all
docker compose -f infra/docker-compose.yml logs -f api      # one service
docker compose -f infra/docker-compose.yml logs -f --tail=200 nginx
```

## Operational notes

- `./data` is bind-mounted into `api:/data` — contains `scanner.db` (SQLite) + `jobs/<id>/` artifacts. Persist this between deploys.
- Healthcheck on api hits `/api/health` every 30s.
- Frontend rebuilds capture `NEXT_PUBLIC_API_BASE_URL` at build time — bump `--build` after changing `DOMAIN`.
- `nginx/scanner.conf` uses `${DOMAIN}` — substitute before first run (envsubst, sed, or templating tool).
