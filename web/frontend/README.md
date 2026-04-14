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
