# pre.voto — Backend

FastAPI backend for pre.voto.

## Setup

The backend runs inside Docker. See the root `README.md` for full setup.

## API Endpoints

### Public

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/countries` | Active countries with next election |
| GET | `/countries/{code}` | Country detail with elections |
| GET | `/candidates/{country}` | Candidates for active election |
| GET | `/candidates/{country}/{slug}` | Candidate detail with positions |
| GET | `/quiz/{country}/statements` | Statements for quiz |
| POST | `/quiz/{country}/submit` | Submit quiz answers, get affinity results |
| GET | `/articles/{country}` | Articles (paginated, `?offset=0&limit=20`) |
| GET | `/articles/{country}/{slug}` | Article detail |
| GET | `/polls/{country}` | Polls for active election |
| GET | `/polls/{country}/average` | Latest poll average |
| POST | `/subscribers` | Subscribe to newsletter (rate-limited 5/hr) |

### Admin (requires `X-Admin-Key` header)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/admin/candidates` | Create candidate |
| PATCH | `/admin/candidates/{id}` | Update candidate |
| POST | `/admin/candidates/{id}/positions` | Bulk upsert positions |
| POST | `/admin/statements` | Create statement |
| POST | `/admin/articles` | Create article |
| POST | `/admin/polls` | Create poll |
| POST | `/admin/jobs/pull-rss` | Stub (501) |
| POST | `/admin/jobs/refresh-photos` | Stub (501) |

Caddy strips `/api` prefix, so all paths above are accessed externally as `/api/...`.

### Error format

All errors follow:
```json
{"error": {"code": "...", "message": "...", "detail": ...}}
```

### Rate limiting

- Public endpoints: 60 req/min per IP
- Subscribers: 5 req/hour per IP
- Uses Redis DB 1 for rate limit storage

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

## CSV Import

Import candidate positions from a CSV file.

### Usage

```bash
# Bind-mount a local directory for CSV files
docker compose exec api python -m app.scripts.import_positions_csv /data/imports/positions.csv
```

Or mount from host:
```bash
docker compose run --rm -v $(pwd)/data/imports:/data api python -m app.scripts.import_positions_csv /data/positions.csv
```

### CSV Format

```csv
candidate_slug,statement_id,value,source_quote,source_url,source_date,coded_by,notes
maria-valencia,d1000000-0000-0000-0000-000000000001,2,"Cita de ejemplo","https://example.com",2025-01-15,equipo,
carlos-restrepo,d1000000-0000-0000-0000-000000000002,-1,,,,,nota adicional
```

**Columns:**
- `candidate_slug` (required): slug del candidato
- `statement_id` (required): UUID del statement o texto exacto
- `value` (required): -2, -1, 0, 1, o 2
- `source_quote` (optional): cita de fuente
- `source_url` (optional): URL válida
- `source_date` (optional): fecha ISO (YYYY-MM-DD)
- `coded_by` (optional): quién codificó la posición
- `notes` (optional): notas adicionales

The script is idempotent — running it twice with the same CSV will not create duplicates.

## Database Access

```bash
# psql shell
docker compose exec postgres psql -U prevoto

# Quick queries
docker compose exec postgres psql -U prevoto -c "SELECT count(*) FROM candidates"
docker compose exec postgres psql -U prevoto -c "\dt"
```

## Tests

```bash
# Install test dependencies
docker compose exec api pip install -e ".[test]"

# Run all tests
docker compose exec api pytest

# Run with coverage
docker compose exec api pytest --cov=app/routers --cov-report=term-missing

# Run specific test file
docker compose exec api pytest tests/test_matching.py -v
```

## Project Structure

```
backend/
├── alembic.ini              # Alembic configuration
├── pyproject.toml            # Dependencies (managed by uv)
├── Dockerfile
├── app/
│   ├── main.py               # FastAPI application + middleware + routers
│   ├── config.py              # Settings (env vars)
│   ├── db.py                  # Async engine & session factory
│   ├── deps.py                # FastAPI dependencies (auth, country lookup)
│   ├── limiter.py             # Rate limiter (slowapi + Redis)
│   ├── worker.py              # Background worker
│   ├── models/                # SQLAlchemy ORM models (12 tables)
│   ├── routers/               # FastAPI route handlers
│   │   ├── countries.py       # /countries
│   │   ├── candidates.py      # /candidates
│   │   ├── quiz.py            # /quiz
│   │   ├── articles.py        # /articles
│   │   ├── polls.py           # /polls
│   │   ├── subscribers.py     # /subscribers
│   │   └── admin.py           # /admin (protected)
│   ├── schemas/               # Pydantic request/response models
│   ├── services/              # Business logic
│   │   ├── matching.py        # Quiz affinity algorithm
│   │   └── beehiiv.py         # Newsletter forwarding
│   ├── scripts/               # CLI scripts
│   │   ├── seed_colombia_2026.py
│   │   └── import_positions_csv.py
│   ├── jobs/                  # Scheduled jobs (Phase 4)
│   └── utils/
├── migrations/
│   ├── env.py                 # Alembic async config
│   ├── script.py.mako         # Migration template
│   └── versions/              # Migration files
└── tests/                     # pytest test suite
```
