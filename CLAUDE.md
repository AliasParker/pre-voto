# CLAUDE.md — pre.voto project state

## What is this project?

pre.voto is a pan-LATAM voting advice application (VAA) that helps citizens compare their positions with candidates before elections. Think "Wahl-O-Mat" for Latin America.

## Current state

- **Phase 1** (Infrastructure): Complete
- **Phase 2** (Schema & migrations): Complete
- **Phase 3** (API REST): Complete — merged to main (PR #4, fc7e0fe)
- **Phase 4** (Worker & jobs): Complete — merged to main
- **Phase 5** (Frontend): Complete — merged to main
- **Phase 6** (OG cards & sharing): Complete — feature/fase-6-og-cards
- **Phase 7** (Deployment to production): Complete — infra/ scripts and docs
- **Phase 8–9**: Not started

## Tech stack

- **Frontend**: Astro 4 + Svelte 5 + Tailwind 4
- **Backend**: FastAPI (Python 3.12) + SQLAlchemy 2.0 (async) + asyncpg
- **Database**: PostgreSQL 16 with pgvector
- **Cache/Queue**: Redis 7
- **Worker**: APScheduler (cron) + asyncio tasks (ad-hoc)
- **Reverse Proxy**: Caddy 2
- **Package manager**: uv (backend), npm (frontend)
- **Containers**: Docker Compose

## Key commands

```bash
# Start everything
docker compose up -d

# Run migrations
docker compose exec api alembic upgrade head

# Seed demo data
docker compose exec api python -m app.scripts.seed_colombia_2026

# psql
docker compose exec postgres psql -U prevoto

# Run tests
docker compose run --rm api-test

# Worker standalone
docker compose up worker

# Trigger jobs manually (admin API)
curl -X POST http://localhost/admin/jobs/pull-rss -H "X-Admin-Key: $ADMIN_KEY"
curl -X POST http://localhost/admin/jobs/refresh-photos -H "X-Admin-Key: $ADMIN_KEY"

# Frontend dev server (standalone, outside Docker)
cd frontend && npm run dev

# Frontend build
cd frontend && npm run build

# ---- Production (VPS) ----

# Bootstrap a fresh VPS (run as root)
ssh root@VPS_IP 'bash -s' < infra/bootstrap-vps.sh

# Deploy (pull + build + migrate + health check)
ssh deploy@VPS_IP 'bash /opt/prevoto/infra/deploy.sh'

# Manual backup
ssh deploy@VPS_IP 'bash /opt/prevoto/infra/backup-postgres.sh'

# Restore from backup
ssh deploy@VPS_IP 'bash /opt/prevoto/infra/restore-postgres.sh 20260518'
```

**Note:** Publishing new articles or updating candidate data requires a frontend rebuild (`npm run build` or redeploy) since the frontend uses static site generation.

## Database

13 tables following SPEC.md Appendix C:

| Table | Has updated_at | Has deleted_at | Has is_demo |
|-------|---------------|---------------|-------------|
| countries | yes | no | no |
| elections | yes | no | no |
| candidates | yes | no | yes |
| statements | yes | no | yes |
| candidate_positions | yes | no | no |
| articles | yes | yes | yes |
| sources | no | no | no |
| news_items | no | no | no |
| newsletter_sends | no | no | no |
| polls | no | yes | no |
| poll_averages | no | no | no |
| subscribers | no | no | no |
| quiz_completions | no | no | no |

Extensions: pgcrypto, pg_trgm, vector

Trigger `update_updated_at_column()` fires BEFORE UPDATE on tables with `updated_at`.

## Architecture rules

- SPEC.md is the source of truth for requirements
- Never push directly to main
- Never commit .env files
- **Frontend dependency rule**: Never run `npm install` on the host Mac. All npm operations must happen inside the container. To add a package: edit `frontend/package.json` manually (or run `docker compose exec frontend npm install <package>`), then rebuild with `docker compose build frontend && docker compose up -d frontend`. The dev container mounts `src/` and `public/` but **not** `node_modules` — the container's `node_modules` comes from the image build via `npm ci`. Host-side installs silently diverge from the container and cause runtime errors.
- **Frontend verification rule**: `astro check` alone does not catch missing Svelte runtime imports. After any dependency or component change, verify pages load in the actual running container (curl or browser), not just via type-checking.
- `is_demo=True` marks seed/demo data — will need admin cleanup endpoint
- Append-only tables (sources, news_items, newsletter_sends, polls, poll_averages, subscribers, quiz_completions) have no `updated_at`
- No IVFFlat/HNSW indexes on vector columns yet (low volume)

## Lessons from Phase 5 (apply in all future phases)

1. **Frontend dependency management**: Any change to `frontend/package.json` requires `docker compose build frontend && docker compose up -d frontend` for the container to pick it up. Never run `npm install` on the host Mac — the container's `node_modules` comes from the Docker image (`npm ci` at build time), and host-side installs silently diverge from what runs in the container, causing runtime errors that are invisible to linters.

2. **Post-phase validation**: `astro check` only validates TypeScript — it does not detect missing Svelte runtime dependencies or broken rendering. Before declaring a phase complete, the app must be running and every critical page must be verified in runtime (curl with HTTP 200, or browser). This final browser validation is done by the user; Claude Code's pre-close report must include curl evidence (status codes) for each critical page.

## Lessons from Phase 6 (apply in all future phases)

1. **Caddy routing for SSG + dynamic OG**: Static site generation (Astro SSG) cannot serve per-user OG meta tags. The solution is conditional Caddy routing: when a quiz URL has share query params (`?top=...&pct=...`), Caddy rewrites to `/share/{country}/quiz` and proxies to the backend, which serves minimal HTML with correct og:image meta tags + a JS redirect via hash fragment (`#top=...&pct=...`). Without the query params, the request falls through to the static frontend. This pattern is reusable for any future SSG page that needs dynamic OG meta.

2. **Font format compatibility**: Pillow requires TTF/OTF fonts — WOFF2 (used by the frontend) is not compatible. Keep separate font files in `backend/app/static/fonts/` for image generation. Both the frontend woff2 and backend TTF should come from the same font family version to ensure visual consistency.

3. **OG text localization**: Use neutral, language-agnostic patterns for OG card text (e.g., `"pre.voto · {country} {year}"` instead of `"Elecciones {country} {year}"`) to avoid localization issues across multiple LATAM countries.

4. **Never rationalize unexpected errors — verify against known-good state**: When an endpoint returns an unexpected error code (e.g., 404 for a route that worked in the previous phase), do NOT invent plausible explanations ("404 in dev mode because X isn't in static paths"). Instead: (a) identify the last known-good state (the closing commit of the previous phase), (b) verify whether the route worked there, (c) bisect to find what broke it. A rationalized explanation prevents investigation and lets bugs reach main.

5. **Docker image cache invalidation**: When adding a Python dependency to `pyproject.toml` and regenerating `uv.lock`, Docker's build cache may not detect the file change. Always use `docker compose build --no-cache api` after modifying `uv.lock` to ensure the new dependency is installed. Verify the API container starts without import errors before proceeding.

6. **Astro dev server caches `getStaticPaths()` per page**: If the API is down when a page is first requested in dev mode, `getStaticPaths()` returns empty paths (because `apiFetch` silently returns `[]` on error), and the dev server caches that empty result. Subsequent requests to that route will 404 even after the API recovers. Fix: restart the frontend container (`docker compose restart frontend`) to clear the cache. This is dev-mode only; production builds fail visibly if the API is unreachable at build time.

7. **Pre-close route validation script**: Before declaring any phase complete, run this verification against all critical routes and report the results:
   ```bash
   for p in "/" "/co/" "/co/quiz" "/co/candidatos" "/co/candidatos/candidata-demo-alfa" "/co/articulos" "/co/encuestas" "/metodologia" "/sobre" "/privacidad"; do
     s=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost$p")
     echo "$s  $p"
   done
   ```
   Condition: 10/10 must return 200. Any non-200 is a blocker.

## Lessons from OG share improvements (PR #35, a391ccf)

1. **OG image URLs must be absolute**: Social media crawlers (WhatsApp, Telegram, X/Twitter) cannot resolve relative URLs in `og:image` meta tags. Always use `settings.public_site_url` to build absolute URLs for OG meta tags. The fix was in `backend/app/routers/og.py` — `og_image_url` changed from `/api/og/quiz?...` to `{settings.public_site_url}/api/og/quiz?...`.

2. **Design token alignment between backend and frontend**: The OG image generator (`backend/app/services/og_image.py`) has its own color constants that must match the frontend CSS variables in `frontend/src/styles/global.css`. When the frontend brand color is `#8B2626`, the backend must use the same value — not an approximation. Current aligned values:
   - `COLOR_BRAND = "#8B2626"` (terracotta, matches `--color-brand` in light mode)
   - `COLOR_PAPER = "#FAFAF8"` (matches `--color-paper`)
   - `COLOR_INK_SOFT = "#4a4a4a"` (matches `--color-ink-soft`)

3. **Production VPS SSH access**: The VPS hostname `pre.voto` may not resolve for SSH. Use the IP directly: `ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP`. The SSH key is `~/.ssh/prevoto` (ed25519). Deploy command: `bash /opt/prevoto/infra/deploy.sh`.

4. **OG card logo rendering**: The logo in the OG card uses segmented text rendering (Pillow `textbbox` to measure each segment's width): "pre" in ink + "." in brand color + "voto" in ink. This matches the frontend header style. A 5px terracotta accent line runs across the top of the card.

## File structure

```
/
├── SPEC.md                    # Complete specification
├── docker-compose.yml         # Development services
├── docker-compose.prod.yml    # Production overrides
├── infra/
│   ├── README.md              # Zero-to-production deployment guide
│   ├── bootstrap-vps.sh       # Idempotent VPS setup (Ubuntu 24.04)
│   ├── deploy.sh              # Pull + build + migrate + health check
│   ├── backup-postgres.sh     # pg_dump → gzip → R2 (cron daily)
│   ├── restore-postgres.sh    # Restore from R2 backup
│   └── .env.production.template  # Production env with secure defaults
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── config.py          # Settings
│   │   ├── db.py              # Async engine
│   │   ├── tasks.py           # spawn_background_task() helper
│   │   ├── worker.py          # APScheduler worker process
│   │   ├── models/            # 13 SQLAlchemy models
│   │   ├── routers/           # API endpoints (8 routers)
│   │   │   └── og.py          # OG image (og_router) + share HTML (share_router)
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── matching.py    # Quiz affinity computation
│   │   │   ├── beehiiv.py     # Newsletter forwarding
│   │   │   ├── rss_aggregator.py  # RSS feed fetching + dedup
│   │   │   ├── wikimedia.py   # Candidate photo search
│   │   │   ├── poll_compute.py    # Weighted poll averages
│   │   │   ├── newsletter.py  # Digest generation + send
│   │   │   └── og_image.py    # Pillow-based OG card PNG generation
│   │   ├── static/
│   │   │   └── fonts/         # Inter TTF for Pillow (Regular + Bold)
│   │   ├── jobs/              # Job wrappers + scheduler config
│   │   │   ├── pull_rss.py
│   │   │   ├── refresh_photos.py
│   │   │   ├── compute_poll_avg.py
│   │   │   ├── send_newsletter.py
│   │   │   └── schedule.py    # APScheduler job registration
│   │   └── scripts/           # seed_colombia_2026.py
│   ├── migrations/versions/   # Alembic migrations (0001, 0002)
│   └── alembic.ini
└── frontend/
    ├── public/
    │   ├── fonts/             # Self-hosted Inter + JetBrains Mono (woff2)
    │   ├── favicon.svg
    │   └── robots.txt
    ├── astro.config.mjs       # Static output, Svelte, sitemap
    └── src/
        ├── components/
        │   ├── Header.astro
        │   ├── Footer.astro
        │   ├── CandidateCard.astro
        │   ├── ArticleCard.astro
        │   ├── PollSummary.astro
        │   ├── NewsletterSignup.astro
        │   ├── Disclaimer.astro
        │   └── islands/
        │       ├── QuizApp.svelte        # VAA quiz island
        │       ├── PollAggregator.svelte  # SVG line chart
        │       ├── ResultsShare.svelte    # Share buttons
        │       ├── DarkModeToggle.svelte  # Theme toggle
        │       ├── CountdownTimer.svelte  # Election countdown
        │       └── _HealthCheck.svelte
        ├── layouts/
        │   └── BaseLayout.astro           # SEO, dark mode, skip-to-content
        ├── lib/
        │   ├── api.ts                     # API client (build + client-side)
        │   ├── i18n.ts                    # es + pt-BR translations
        │   ├── types.ts                   # TS types mirroring backend schemas
        │   ├── countries.ts               # Country metadata + locale mapping
        │   ├── markdown.ts                # marked wrapper
        │   └── quiz.ts                    # Affinity computation (mirrors backend)
        ├── pages/
        │   ├── index.astro                # Pan-LATAM landing
        │   ├── metodologia.astro
        │   ├── sobre.astro
        │   ├── privacidad.astro
        │   └── [country]/
        │       ├── index.astro            # Country landing + countdown
        │       ├── quiz.astro             # Quiz shell + QuizApp island
        │       ├── candidatos/
        │       │   ├── index.astro        # Candidate grid
        │       │   └── [slug].astro       # Candidate detail
        │       ├── encuestas.astro        # Polls + chart
        │       └── articulos/
        │           ├── index.astro        # Article list
        │           └── [slug].astro       # Article detail
        └── styles/
            └── global.css                 # Fonts, dark mode, Tailwind theme
```
