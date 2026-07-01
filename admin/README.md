# Knowledge Gateway — Admin Panel

Internal admin panel for the Knowledge Gateway API. SPA built with **Vite + React + TypeScript**,
**Refine** (headless data/auth layer) and **shadcn/ui** (Tailwind CSS v4). Linting and formatting
are handled by **Biome**.

## Stack

- Vite 8, React 19, TypeScript 6
- Refine 5 (`@refinedev/core`, `@refinedev/react-router`) — headless CRUD, auth, routing
- shadcn/ui + Tailwind CSS v4 for components
- Biome 2 for lint + format

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
- `npm run lint` — Biome check
- `npm run format` — Biome check with `--write`

## Structure

```
src/
├── App.tsx                     # Refine + router + resources + routes
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
│   ├── layout.tsx              # authenticated shell (sidebar + logout)
│   └── ui/                     # shadcn components
└── pages/
    ├── login.tsx
    └── users.tsx               # example resource (list + delete + pagination)
```

## Adding a resource

1. Add the resource to the `resources` array in `App.tsx` and a `<Route>` for its page.
2. Build the page with Refine hooks (`useList`, `useOne`, `useCreate`, `useUpdate`, `useDelete`) —
   the data provider already speaks the backend's `limit`/`offset` + `{ total, <items>: [...] }`
   contract, so no per-resource wiring is needed.
3. Add shadcn components as needed: `npx shadcn@latest add <component>`.

## Deployment

`npm run build` emits static files to `dist/`. Serve them from the same origin as the API (the
server-side nginx that already reverse-proxies `/api/v1` to the backend container), so the httpOnly
session cookie works without CORS.
