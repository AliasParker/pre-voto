# pre.voto

Plataforma civic-tech pan-LATAM de voto informado. Brújula electoral (VAA) + newsletter de análisis pre-electoral.

## Setup local

```bash
git clone https://github.com/your-org/pre.voto.git && cd pre.voto
cp .env.example .env
docker compose up -d
```

Abre `http://localhost` para ver el placeholder. La API responde en `http://localhost/api/health`.

## Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Caddy | 80, 443 | Reverse proxy |
| Frontend | 3000 (interno) | Astro dev server |
| API | 8000 (interno) | FastAPI |
| Worker | — | Background jobs |
| PostgreSQL | 5432 (interno) | Base de datos con pgvector |
| Redis | 6379 (interno) | Cache + cola |
| Mailpit | 8025 | UI de email para dev |

## Comandos utiles

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs de un servicio especifico
docker compose logs -f api

# Conectar a PostgreSQL
docker compose exec postgres psql -U prevoto prevoto

# Rebuild despues de cambiar Dockerfile o dependencias
docker compose up -d --build

# Parar todo
docker compose down

# Parar todo y borrar volumenes (datos)
docker compose down -v
```

## Estructura del proyecto

```
.
├── frontend/        # Astro 4 + Svelte 5 + Tailwind 4
├── backend/         # FastAPI (Python 3.12)
├── docs/            # Documentacion del proyecto
├── infra/           # Scripts de infraestructura
├── Caddyfile        # Config Caddy (dev)
├── Caddyfile.prod   # Config Caddy (produccion)
├── docker-compose.yml
└── docker-compose.prod.yml
```

Ver `SPEC.md` para la especificacion completa del proyecto.
