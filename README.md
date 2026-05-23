# pre.voto

Brújula electoral de código abierto para Latinoamérica. Compara tus posiciones con las de los candidatos presidenciales en 20 temas, con cada codificación respaldada por fuentes verificables.

**[pre.voto](https://pre.voto)** | [Metodología](https://pre.voto/metodologia) | [Datos abiertos](https://pre.voto/datos) | [FAQ](https://pre.voto/faq)

## Qué es

pre.voto es una VAA (Voting Advice Application) pan-LATAM. No es una encuesta, no recomienda voto, no tiene afiliación partidaria. Tu resultado es para tu uso personal.

- **Colombia 2026**: activo — 20 statements, 12 candidatos, 240 codificaciones
- **Brasil 2026**: en preparación
- **México / Argentina 2027**: planificado

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| Frontend | Astro 4 + Svelte 5 + Tailwind 4 |
| Backend | FastAPI (Python 3.12) + SQLAlchemy 2.0 (async) |
| Base de datos | PostgreSQL 16 + pgvector |
| Cache/Cola | Redis 7 |
| Worker | APScheduler + asyncio |
| Reverse proxy | Caddy 2 |
| Contenedores | Docker Compose |
| Package managers | uv (backend), npm (frontend) |

## Setup local

```bash
git clone https://github.com/AliasParker/pre-voto.git
cd pre-voto
cp .env.example .env
docker compose up -d
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.seed_colombia_2026
```

Abre `http://localhost` para ver el frontend. API health check en `http://localhost/api/health`.

## Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Caddy | 80, 443 | Reverse proxy |
| Frontend | 3000 (interno) | Astro SSG dev server |
| API | 8000 (interno) | FastAPI |
| Worker | — | Background jobs (RSS, fotos, encuestas, newsletter) |
| PostgreSQL | 5432 (interno) | Base de datos con pgvector |
| Redis | 6379 (interno) | Cache + cola |
| Mailpit | 8025 | UI de email para dev |

## Comandos

```bash
# Logs
docker compose logs -f api

# Tests
docker compose run --rm api-test

# psql
docker compose exec postgres psql -U prevoto

# Frontend build
docker compose build frontend && docker compose up -d frontend

# Trigger jobs manualmente
curl -X POST http://localhost/admin/jobs/pull-rss -H "X-Admin-Key: $ADMIN_KEY"
```

## Estructura

```
.
├── frontend/          # Astro 4 + Svelte 5 + Tailwind 4
│   └── src/
│       ├── pages/     # Rutas estáticas (SSG)
│       ├── components/# Astro components + Svelte islands
│       ├── lib/       # API client, i18n, quiz logic, types
│       └── styles/    # Global CSS + Tailwind theme
├── backend/
│   └── app/
│       ├── routers/   # API endpoints (13 routers)
│       ├── models/    # SQLAlchemy models (13 tablas)
│       ├── schemas/   # Pydantic schemas
│       ├── services/  # Business logic
│       ├── jobs/      # Scheduled jobs
│       └── scripts/   # Seed scripts
├── infra/             # VPS bootstrap, deploy, backup
├── LICENSES/          # Full license texts (REUSE spec)
├── DATA.md            # Documentación del dataset abierto
└── CONTRIBUTING.md    # Guía de contribución
```

## Datos abiertos

Los datos editoriales están disponibles via API pública bajo CC-BY 4.0:

```bash
curl https://pre.voto/api/opendata/co/statements
curl https://pre.voto/api/opendata/co/candidates
curl https://pre.voto/api/opendata/co/positions
```

Documentación completa en [DATA.md](DATA.md) y [pre.voto/datos](https://pre.voto/datos).

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md). En resumen:

- **Errores editoriales**: [errores@pre.voto](mailto:errores@pre.voto) o issue en GitHub
- **Código**: issue primero, fork, PR con tests
- **Nuevo país**: [hola@pre.voto](mailto:hola@pre.voto)

## Licencia

- **Código**: [AGPL-3.0-or-later](LICENSES/AGPL-3.0-or-later.txt)
- **Datos editoriales**: [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Marca "pre.voto"**: reservada — ver [LICENSE](LICENSE)

## Contacto

- Consultas: [hola@pre.voto](mailto:hola@pre.voto)
- Errores: [errores@pre.voto](mailto:errores@pre.voto)
- X: [@prevotoLATAM](https://x.com/prevotoLATAM)
