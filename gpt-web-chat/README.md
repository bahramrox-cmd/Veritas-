# gpt-web-chat

GPT-style browser chat built with [Chat SDK](https://chat-sdk.dev/docs), the Web adapter, and Vercel AI Gateway.

## Getting Started

1. Copy the example environment file:

```bash
copy .env.example .env.local
```

2. Set `AI_GATEWAY_API_KEY` in `.env.local` (or use Vercel OIDC after linking the project). Optionally change `AI_GATEWAY_MODEL`.

3. Start the app:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000). Messages go to `/api/chat`.

If Turbopack waits for the filesystem to settle and mentions `desktop.ini` under `node_modules`, OneDrive is touching those folders. Exclude `gpt-web-chat/node_modules` and `gpt-web-chat/.next` from OneDrive sync, or run the app from a path outside OneDrive. Polling (`watchOptions.pollIntervalMs`) is a last resort.

The auth stub in `src/lib/auth-stub.ts` currently returns a local user. Replace it before exposing this beyond your machine.

## Endpoints

- Web chat UI: `/`
- Web chat API: `/api/chat`
- Web webhook: `/api/webhooks/web`

## Scripts

| Command | Description |
| --- | --- |
| `npm run dev` | Start the development server |
| `npm run build` | Create a production build |
| `npm run start` | Start the production server |
| `npm run typecheck` | Type-check the project |

## Learn More

- [Chat SDK Documentation](https://chat-sdk.dev/docs)
- [Web adapter](https://chat-sdk.dev/adapters/official/web)
- [AI Gateway](https://vercel.com/docs/ai-gateway)
