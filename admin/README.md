# Knowledge Gateway — Admin Panel

Internal admin panel for the Knowledge Gateway API. SPA built with **Vite + React + TypeScript**,
**Refine** (headless data/auth layer) and **shadcn/ui** (Tailwind CSS v4). Linting and formatting
are handled by **Biome**.

## Stack

- Vite 8, React 19, TypeScript 6
- Refine 5 (`@refinedev/core`, `@refinedev/react-router`) — headless CRUD, auth, routing
- shadcn/ui + Tailwind CSS v4 for components, next-themes for light/dark mode
- Biome 2 for lint + format, Vitest 4 for tests

## Development

```bash
npm install
npm run dev        # http://localhost:5173
```

The dev server proxies `/api` → `http://127.0.0.1:8080` (see `vite.config.ts`), so the session
cookie is same-origin. Run the backend locally with `SESSION_COOKIE_SECURE=false` (plain HTTP) and a
`BOOTSTRAP_ADMIN_PASSWORD` set, then sign in with the admin name + that password.

Scripts:

- `npm run dev` — dev server
- `npm run build` — type-check + production build to `dist/`
- `npm run test` — run the Vitest suite (`npm run test:watch` for watch mode)
- `npm run lint` — Biome check
- `npm run format` — Biome check with `--write`

## Tests

Vitest covers the framework-agnostic logic — the fetch wrapper (`lib/api.ts`), the data provider
and the auth provider — by stubbing `fetch`. No DOM/browser is needed; the environment is `node`.
Tests live next to the code as `*.test.ts`.

## Structure

```
src/
├── App.tsx                     # Refine + router + resources; pages are lazy-loaded (code-split)
├── main.tsx
├── types.ts                    # API response types
├── lib/
│   ├── api.ts                  # fetch wrapper (credentials: include, error normalisation)
│   └── utils.ts                # cn() for shadcn
├── providers/
│   ├── dataProvider.ts         # maps Refine CRUD → limit/offset + { total, <items> } responses
│   ├── authProvider.ts         # cookie session against /auth/{login,logout,me}
│   └── notificationProvider.ts # sonner toasts
├── components/
│   ├── layout.tsx              # authenticated shell (sidebar + theme toggle + logout)
│   ├── resource-table.tsx      # generic list table (columns, row actions, loading skeleton)
│   ├── form-dialog.tsx         # create/edit dialog driven by field descriptors
│   ├── form-fields.tsx         # field renderers used by form-dialog
│   ├── detail-dialog.tsx       # read-only record view
│   ├── confirm-dialog.tsx      # destructive-action confirmation
│   ├── filters.tsx             # list filter controls (select/search)
│   ├── data-pagination.tsx     # limit/offset pagination controls
│   ├── user-api-keys-dialog.tsx# per-user API keys (direct apiFetch + react-query,
│   │                           #   /users/{id}/api-keys doesn't fit the generic data provider)
│   ├── page-header.tsx, page-fallback.tsx, copy-button.tsx, relative-time.tsx, theme-toggle.tsx
│   └── ui/                     # shadcn components
└── pages/                      # one route per resource, lazy-loaded from App.tsx
    ├── login.tsx
    ├── dashboard.tsx           # overview cards
    ├── users.tsx               # users + rate limits + API keys dialog
    ├── providers.tsx           # inference providers
    ├── embedding-models.tsx
    ├── knowledge-bases.tsx
    ├── llm-models.tsx
    ├── documents.tsx           # list + upload into a knowledge base
    ├── search.tsx              # direct vector search against a knowledge base
    ├── requests.tsx            # chat completion request logs
    └── analytics.tsx           # usage stats (per-model / per-knowledge-base)
```

## Adding a resource

1. Add the resource to the `resources` array in `App.tsx`, a lazy import for its page, and a
   `<Route>` for it.
2. Build the page with Refine hooks (`useList`, `useOne`, `useCreate`, `useUpdate`, `useDelete`) —
   the data provider already speaks the backend's `limit`/`offset` + `{ total, <items>: [...] }`
   contract, so no per-resource wiring is needed. Reuse the shared building blocks
   (`resource-table`, `form-dialog`, `filters`, `data-pagination`).
3. For endpoints that don't fit the generic CRUD contract (e.g. `/users/{id}/api-keys`), call
   `apiFetch` directly with react-query — see `user-api-keys-dialog.tsx`.
4. Add shadcn components as needed: `npx shadcn@latest add <component>`.
