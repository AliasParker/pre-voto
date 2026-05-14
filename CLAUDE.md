# CLAUDE.md — pre.voto project state

## What is this project?

pre.voto is a pan-LATAM voting advice application (VAA) that helps citizens compare their positions with candidates before elections. Think "Wahl-O-Mat" for Latin America.

## Current state

- **Phase 1** (Infrastructure): Complete
- **Phase 2** (Schema & migrations): Complete
- **Phase 3** (API REST): Complete — merged to main (PR #4, fc7e0fe)
- **Phase 4** (Worker & jobs): In progress — feature/fase-4-worker
- **Phase 5–9**: Not started

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
```

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
- `is_demo=True` marks seed/demo data — will need admin cleanup endpoint
- Append-only tables (sources, news_items, newsletter_sends, polls, poll_averages, subscribers, quiz_completions) have no `updated_at`
- No IVFFlat/HNSW indexes on vector columns yet (low volume)

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
    └── src/                   # Astro + Svelte
```
