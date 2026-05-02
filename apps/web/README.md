# scanner-web

Frontend Next.js 15 (App Router) para o Scanner de Imagens.

## Stack

- Next.js 15 + React 19 RC
- TypeScript strict
- Tailwind CSS v4
- lucide-react, react-dropzone, sonner
- WebSocket para progresso ao vivo

## Setup

```bash
cd apps/web
cp .env.local.example .env.local
npm install
npm run dev
```

API esperada em `http://localhost:8000` (configurável via `NEXT_PUBLIC_API_BASE_URL`). O `next.config.ts` faz rewrite de `/api/*` e `/ws/*` para o backend em dev.

## Comandos

| Comando | Ação |
|---------|------|
| `npm run dev` | Dev server (porta 3000) |
| `npm run build` | Build de produção |
| `npm start` | Servir build |
| `npm run lint` | ESLint |

## Estrutura

```
apps/web/
├── app/                # App Router pages
│   ├── layout.tsx
│   ├── page.tsx        # Dashboard / novo scan
│   ├── jobs/page.tsx   # Lista
│   ├── jobs/[id]/      # Detalhe + WS
│   └── health/
├── components/         # UI atomica (StatusBadge, ProgressBar, JobCard, DropZone, Spinner)
├── lib/                # api.ts, ws.ts, types.ts, cn.ts
└── public/
```

## PWA features

O frontend é uma Progressive Web App:

- **Instalável** — manifest + ícones (192/512 SVG maskable). Botão "Instalar app" aparece quando `beforeinstallprompt` dispara.
- **Push notifications** — VAPID end-to-end. Botão "Ativar notificações" assina via `pushManager.subscribe`, registra no backend (`POST /api/push/subscribe`); o SW exibe `Notification` quando o backend envia push (job concluído).
- **Offline-first / cache resiliente** — Service Worker com 3 estratégias:
  - `/api/*` → network-first (fallback de cache)
  - `_next/static/*` + assets → cache-first
  - HTML → network-first (fallback de cache para `/`, `/jobs`, `/health` pré-cacheados)

Arquivos relevantes: `public/manifest.json`, `public/sw.js`, `public/icon-{192,512}.svg`, `components/{ServiceWorkerRegistrar,EnablePush,InstallPrompt}.tsx`.

## Pendente (Phase 4+)

- Tests E2E (Playwright) — incluir cenário PWA (SW registra, push end-to-end com VAPID mock)
- Theme toggle manual (atual segue prefers-color-scheme)
- Auth (quando backend tiver)
- Ícones PNG raster opcionais (maior compat com algumas plataformas)
