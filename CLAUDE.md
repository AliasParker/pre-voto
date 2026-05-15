# CLAUDE.md — pre.voto project state

## What is this project?

pre.voto is a pan-LATAM voting advice application (VAA) that helps citizens compare their positions with candidates before elections. Think "Wahl-O-Mat" for Latin America.

## Current state

- **Phase 1** (Infrastructure): Complete
- **Phase 2** (Schema & migrations): Complete
- **Phase 3** (API REST): Complete — merged to main (PR #4, fc7e0fe)
- **Phase 4** (Worker & jobs): Complete — merged to main
- **Phase 5** (Frontend): Complete — feature/fase-5-frontend
- **Phase 6–9**: Not started

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

## File structure

```
/
├── SPEC.md                    # Complete specification
├── docker-compose.yml         # Development services
├── docker-compose.prod.yml    # Production overrides
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── config.py          # Settings
│   │   ├── db.py              # Async engine
│   │   ├── tasks.py           # spawn_background_task() helper
│   │   ├── worker.py          # APScheduler worker process
│   │   ├── models/            # 13 SQLAlchemy models
│   │   ├── routers/           # API endpoints (7 routers)
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── matching.py    # Quiz affinity computation
│   │   │   ├── beehiiv.py     # Newsletter forwarding
│   │   │   ├── rss_aggregator.py  # RSS feed fetching + dedup
│   │   │   ├── wikimedia.py   # Candidate photo search
│   │   │   ├── poll_compute.py    # Weighted poll averages
│   │   │   └── newsletter.py  # Digest generation + send
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
