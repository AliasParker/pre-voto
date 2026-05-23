# ---- Builder ----
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app/ app/
COPY alembic.ini ./
COPY migrations/ migrations/

# ---- Runtime ----
FROM python:3.12-slim AS runtime

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN groupadd --system app && useradd --system --gid app app

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app app/
COPY --from=builder /app/alembic.ini ./
COPY --from=builder /app/migrations migrations/

ENV PATH="/app/.venv/bin:$PATH"

USER app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---- Test ----
FROM runtime AS test

USER root
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN mkdir -p /home/app/.cache/uv && chown -R app:app /home/app/.cache
RUN uv sync --frozen --no-install-project --extra test
COPY tests/ tests/

USER app
CMD ["pytest", "tests/", "-v"]
