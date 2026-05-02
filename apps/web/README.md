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

## Pendente (Phase 3+)

- Tests E2E (Playwright)
- Theme toggle manual (atual segue prefers-color-scheme)
- Auth (quando backend tiver)
