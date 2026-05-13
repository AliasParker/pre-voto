# pre.voto — Backend

FastAPI backend for pre.voto.

## Setup

The backend runs inside Docker. See the root `README.md` for full setup.

## Migrations (Alembic)

All database migrations use Alembic with async SQLAlchemy.

```bash
# Apply all pending migrations
docker compose exec api alembic upgrade head

# Check current migration version
docker compose exec api alembic current

# Generate a new migration after model changes
docker compose exec api alembic revision --autogenerate -m "description"

# Rollback one migration
docker compose exec api alembic downgrade -1
```

## Seed Data

The seed script creates demo data for Colombia 2026. It is idempotent (safe to run multiple times).

```bash
docker compose exec api python -m app.scripts.seed_colombia_2026
```

This creates:
- 1 country (Colombia)
- 1 election (presidential first round, 2026-05-31)
- 5 demo candidates (`is_demo=True`)
- 8 statements across policy categories
- 40 candidate positions
- 5 RSS sources (Colombian media)

## Database Access

```bash
# psql shell
docker compose exec postgres psql -U prevoto

# Quick queries
docker compose exec postgres psql -U prevoto -c "SELECT count(*) FROM candidates"
docker compose exec postgres psql -U prevoto -c "\dt"
```

## Project Structure

```
backend/
├── alembic.ini              # Alembic configuration
├── pyproject.toml            # Dependencies (managed by uv)
├── Dockerfile
├── app/
│   ├── main.py               # FastAPI application
│   ├── config.py              # Settings (env vars)
│   ├── db.py                  # Async engine & session factory
│   ├── worker.py              # Background worker
│   ├── models/                # SQLAlchemy ORM models
│   ├── routers/               # FastAPI route handlers (Phase 3)
│   ├── schemas/               # Pydantic request/response models (Phase 3)
│   ├── services/              # Business logic (Phase 4)
│   ├── jobs/                  # Scheduled jobs (Phase 4)
│   ├── scripts/               # CLI scripts (seed, etc.)
│   └── utils/
├── migrations/
│   ├── env.py                 # Alembic async config
│   ├── script.py.mako         # Migration template
│   └── versions/              # Migration files
└── tests/
```
