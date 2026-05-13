# CLAUDE.md — pre.voto project state

## What is this project?

pre.voto is a pan-LATAM voting advice application (VAA) that helps citizens compare their positions with candidates before elections. Think "Wahl-O-Mat" for Latin America.

## Current state

- **Phase 1** (Infrastructure): Complete
- **Phase 2** (Schema & migrations): Complete
- **Phase 3** (API REST): Not started
- **Phase 4** (Worker & jobs): Not started
- **Phase 5–9**: Not started

## Tech stack

- **Frontend**: Astro 4 + Svelte 5 + Tailwind 4
- **Backend**: FastAPI (Python 3.12) + SQLAlchemy 2.0 (async) + asyncpg
- **Database**: PostgreSQL 16 with pgvector
- **Cache/Queue**: Redis 7
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
```

## Database

12 tables following SPEC.md Appendix C:

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
- Append-only tables (sources, news_items, polls, poll_averages, subscribers, quiz_completions) have no `updated_at`
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
│   │   ├── models/            # 12 SQLAlchemy models
│   │   └── scripts/           # seed_colombia_2026.py
│   ├── migrations/versions/   # Alembic migrations
│   └── alembic.ini
└── frontend/
    └── src/                   # Astro + Svelte
```
