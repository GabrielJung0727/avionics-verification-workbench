# `web/frontend/` — portfolio + docs site

A Next.js 15 + next-intl + Tailwind static site that doubles as the
project's portfolio landing page **and** its documentation hub. Korean
and English are supported via path-based i18n (`/ko`, `/en`).

The tone is intentionally an **engineering dashboard**, not a SaaS
landing page: dark navy / graphite, sparse amber / cyan accents, monospace
labels, thin grid lines.

## Quick start

```bash
cd web/frontend
npm install
npm run dev      # http://localhost:3000  → redirects to /ko
```

Production:

```bash
npm run build    # static export under ./out/
```

The site is generated as fully static HTML (`output: 'export'` in
`next.config.mjs`), so it can be hosted on GitHub Pages, GitLab Pages,
Cloudflare Pages, Netlify, S3, or any static host.

## Pages (9 each, ko + en — 18 prerendered routes)

| Path | Purpose |
|---|---|
| `/` | Hero, four pillars, what-it-does-and-doesn't, metrics, ASCII architecture |
| `/platform` | Two-layer story (M1–M6 + Phase A–E), audience |
| `/workbench` | M1–M6 milestone cards |
| `/intelligence` | Phase A–E cards + hard-line panel |
| `/demo` | One-command flow + 10-step timeline + artefact list |
| `/standards` | DO-178C / ARP4754A / EASA AI / FAA AI / DO-160G(out) / DO-254(out) |
| `/docs` | Curated link hub into the GitHub `docs/` tree |
| `/results` | Latest test / coverage / model / evidence numbers |
| `/about` | Project intent, position fit, contact, disclaimer |

## Adding / changing copy

- All UI strings live in `src/messages/{ko,en}.json`. Keys are mirrored.
- Page layouts in `src/app/[locale]/<page>/page.tsx` consume the dict
  via `getTranslations(...)`.
- The hard-line banner at the top of every page is `src/components/HardLineBanner.tsx`.

## i18n

- `src/i18n/routing.ts` declares `["ko", "en"]`, default `ko`,
  `localePrefix: "always"`.
- `src/middleware.ts` adds locale prefixes for unmatched paths.
- The language switch in the top-right preserves the current path.

## Live mode (optional)

The site is fully usable as a static portfolio. When the FastAPI backend
under `web/backend/` (and optionally the Phase B intelligence endpoint
from `scripts/serve_intelligence.py`) is running, four pages light up
with real data:

| Page | Live element | Source |
|---|---|---|
| `/` (Home) | `BackendStatus` + `LiveSummary` (8 cards) | `GET /api/results/summary` |
| `/results` | `LiveSummary` above the static groups | same |
| `/intelligence` | `LiveModels` cards (registry + assurance metadata) | `GET /api/registry/models` |
| `/demo` | `PredictWidget` form calling escape predictor | `POST /api/predict/fault_escape` (proxied to intelligence endpoint) |

The top-right `Live` / `Backend offline` badge in the nav reflects current
backend state. Every live component **degrades gracefully** to a friendly
"backend unreachable" line when offline — the static portfolio remains
intact.

### Configuring the backend URL

```bash
cp .env.example .env.local
# edit NEXT_PUBLIC_BACKEND_URL if needed (default: http://localhost:8000)
npm run dev
```

The variable is `NEXT_PUBLIC_*` so it's baked into the static export at
build time.

### Three-tier dev loop

```bash
# shell A — Phase B intelligence endpoint (predict)
python scripts/serve_intelligence.py             # :8081

# shell B — read-only backend (results / lakehouse / registry / proxy)
INTELLIGENCE_ENDPOINT=http://127.0.0.1:8081 \
  uvicorn web.backend.app.main:app --port 8000   # :8000

# shell C — frontend
cd web/frontend && npm run dev                   # :3000
```

## Stack

- Next.js 15 (App Router, RSC, static export)
- next-intl 3.26 (i18n + middleware)
- Tailwind CSS 3.4 (engineering-dashboard palette)
- React 19
- TypeScript 5.6

## Disclaimer

Every page carries a banner reminding readers that nothing here is
substantiated certification evidence — see
[`docs/regulatory/disclaimer.md`](https://github.com/GabrielJung0727/avionics-verification-workbench/blob/main/docs/regulatory/disclaimer.md).
