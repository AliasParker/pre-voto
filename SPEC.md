# pre.voto — Especificación completa para Claude Code

> Plan de construcción por fases. Cada fase está pensada como un sprint independiente: una sola conversación con Claude Code debería completar una fase. No saltes fases hacia adelante — las dependencias importan.

---

## Cómo usar este documento con Claude Code

1. Crea un repo vacío en GitHub (privado por ahora): `pre.voto`.
2. Clónalo localmente y copia este archivo como `SPEC.md` en la raíz.
3. En el directorio del repo, ejecuta `claude`.
4. **Primer prompt sugerido**:

   > "Lee SPEC.md completo. Antes de escribir cualquier código, hazme entre 3 y 7 preguntas si tienes dudas reales sobre la arquitectura, alcance o decisiones técnicas. Luego propón un plan detallado para ejecutar SOLO la Fase 1 (infraestructura local + bootstrap del repo), y espera mi aprobación antes de tocar archivos. No avances a Fase 2 sin que te lo pida explícitamente."

5. Para cada fase siguiente, abre una **nueva conversación** con Claude Code (no acumules contexto innecesario) y dale el prompt correspondiente al final de cada fase.

**Regla operativa importante**: Claude Code debe ejecutar siempre primero `git status` y trabajar en branches por feature (`feature/fase-1-infra`, `feature/fase-2-schema`, etc.), nunca directamente en `main`.

---

## 0. Contexto y visión

**Qué es pre.voto.** Plataforma civic-tech pan-LATAM de voto informado. El producto central es un VAA (Voting Advice Application): quiz de 20-30 afirmaciones de política pública donde el usuario obtiene afinidad porcentual con cada candidato. El quiz alimenta un newsletter quincenal de análisis pre-electoral, que monetiza vía membresía + grants de fundaciones democráticas.

**Modelo de URL por país**: `pre.voto/co` (Colombia), `pre.voto/br` (Brasil), `pre.voto/mx` (México), etc. La landing raíz `pre.voto` es pan-regional con selector de país.

**Ventana electoral inmediata (prioridad de lanzamiento):**

1. **Colombia** — 1ra vuelta presidencial 31 mayo 2026 ← **lanzamiento día 1**
2. **Perú** — 2da vuelta presidencial 7 junio 2026
3. **Brasil** — generales 4 octubre 2026 (requiere representante legal local)
4. **México** — intermedias federales 6 junio 2027

**Lo que NO construimos en MVP** (registrar como out-of-scope explícito):

- SaaS para campañas o partidos políticos (destruye neutralidad).
- Generación de imágenes con IA de personas reales (ilegal en BR por Resolución TSE 23.732/2024, restringido en MX por Plan B 2026).
- Sistema de votación electrónica real.
- App móvil nativa (web responsive es suficiente).
- Pagos o checkout propios (la membresía la maneja Beehiiv).

**Principio rector cuando haya duda**: si la decisión es entre "elegante técnicamente" vs "pragmático para un solo founder con <$1k USD", **elegir pragmático siempre**. Si es entre "moderno y vistoso" vs "serio y neutral", **elegir neutral siempre**. Somos civic tech, no startup de moda.

---

## 1. Decisiones técnicas con rationale

| Capa | Tecnología | Por qué |
|---|---|---|
| Frontend | Astro 4 + Tailwind 4 + Svelte 5 (islas) | Astro es content-first: páginas estáticas rapidísimas para SEO + islas interactivas solo donde se necesita. Tailwind 4 para velocidad. Svelte 5 (no React) en islas porque produce bundles ~3× menores. |
| Backend | FastAPI (Python 3.12) | Async nativo, OpenAPI auto-generado, tipado, ecosistema Python para NLP, scraping y embeddings. |
| Worker | Python con APScheduler + asyncio tasks | Misma imagen Docker que el API, distinto entrypoint. Reduce complejidad operativa. |
| DB | PostgreSQL 16 con extensión pgvector | Estándar, gratuito. pgvector incluido desde día 1 para búsqueda semántica de propuestas (lo necesitarás antes de lo que crees, no quieras migrar después). |
| Cache + cola | Redis 7 | Sesiones, rate limiting. Tareas ad-hoc via asyncio (migrar a arq cuando el throughput lo requiera). |
| Reverse proxy | Caddy 2 | TLS automático con Let's Encrypt. Config de 8 líneas vs 80 de nginx. |
| CDN + protección | Cloudflare (free tier) | DNS, DDoS, cache edge, WAF, Origin Cert para TLS end-to-end. |
| Hosting | Hetzner Cloud (CX22) | €4.59/mes, mejor €/performance del mercado. Datacenter US (Ashburn) para LATAM. |
| Newsletter | Beehiiv (free → Grow $39/mes en >2.5K subs) | Mejor que Substack en LATAM (moneda local, ad network nativo, API integrable). |
| Backups | Cloudflare R2 + rclone | 10GB gratis, $0 de egress. |
| Analytics | Plausible self-hosted (en mismo VPS) | Sin cookies → sin popup. GDPR/LGPD friendly. |
| Búsqueda | Meilisearch self-hosted (cuando haya >100 artículos) | Una sola binary, gratis. |
| Captura email | Beehiiv API directa | No reinventamos. |
| Imágenes políticos | Wikimedia Commons API | Gratis, licencias CC, política de atribución clara. |
| Imágenes editoriales | Unsplash + Pexels APIs | Gratis, ilimitado en práctica. |

**Cosas que Claude Code NO debe meter**:

- **Sin React**, en ninguna parte (queremos bundles mínimos en móvil).
- **Sin Next.js**, mismo motivo (overkill para sitio content-first).
- **Sin Vercel/Netlify/Supabase managed** (queremos portabilidad y aprendizaje de la infra).
- **Sin localStorage para datos persistentes del usuario** (no necesitamos rastreo, todo del quiz se procesa en cliente y se descarta).
- **Sin trackers ni cookies de marketing** (es civic tech, no e-commerce).
- **Sin diseño con muchos gradientes, glassmorphism, modo glow** — diseño serio, tipográfico, accesible. Más Wahl-O-Mat que Linear.

---

## 2. Estructura del repositorio

```
pre.voto/
├── README.md                       # Setup local en 3 minutos
├── SPEC.md                          # Este documento
├── docker-compose.yml               # Stack desarrollo (todos los servicios)
├── docker-compose.prod.yml          # Override para producción
├── .env.example
├── .gitignore
├── Caddyfile
│
├── frontend/
│   ├── astro.config.mjs
│   ├── package.json
│   ├── tailwind.config.mjs
│   ├── tsconfig.json
│   ├── Dockerfile
│   ├── public/
│   │   ├── favicon.svg
│   │   ├── og/                     # Open Graph images por país
│   │   └── fonts/                  # Inter variable, self-hosted
│   └── src/
│       ├── content/                 # Markdown (artículos, páginas estáticas)
│       │   ├── articles/{country}/
│       │   ├── pages/
│       │   └── config.ts
│       ├── components/
│       │   ├── Layout.astro
│       │   ├── Header.astro
│       │   ├── Footer.astro
│       │   ├── CountrySelector.astro
│       │   ├── ArticleCard.astro
│       │   ├── CandidateCard.astro
│       │   ├── PollSummary.astro
│       │   ├── NewsletterSignup.astro
│       │   ├── Disclaimer.astro
│       │   └── islands/
│       │       ├── QuizApp.svelte      # El VAA completo
│       │       ├── PollAggregator.svelte
│       │       └── ResultsShare.svelte
│       ├── layouts/
│       │   ├── BaseLayout.astro
│       │   └── ArticleLayout.astro
│       ├── pages/
│       │   ├── index.astro            # Landing pan-LATAM
│       │   ├── [country]/
│       │   │   ├── index.astro         # Landing por país
│       │   │   ├── quiz.astro          # Página del VAA
│       │   │   ├── candidatos.astro
│       │   │   ├── encuestas.astro
│       │   │   └── articulos/
│       │   │       ├── index.astro
│       │   │       └── [slug].astro
│       │   ├── metodologia.astro
│       │   ├── sobre.astro
│       │   ├── privacidad.astro
│       │   └── 404.astro
│       ├── lib/
│       │   ├── api.ts                 # Cliente del backend
│       │   ├── quiz.ts                # Algoritmo de matching (cliente)
│       │   ├── i18n.ts                # ES + PT
│       │   └── types.ts
│       └── styles/
│           └── global.css
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml                 # uv-managed
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # Entrypoint FastAPI
│   │   ├── worker.py                  # Entrypoint del worker
│   │   ├── config.py                  # Settings (pydantic-settings)
│   │   ├── db.py                      # SQLAlchemy session factory
│   │   ├── deps.py                    # Dependencies de FastAPI
│   │   ├── models/                    # SQLAlchemy declarative
│   │   │   ├── country.py
│   │   │   ├── candidate.py
│   │   │   ├── statement.py
│   │   │   ├── position.py
│   │   │   ├── article.py
│   │   │   ├── poll.py
│   │   │   └── subscriber.py
│   │   ├── schemas/                   # Pydantic
│   │   ├── routers/
│   │   │   ├── countries.py
│   │   │   ├── quiz.py
│   │   │   ├── candidates.py
│   │   │   ├── articles.py
│   │   │   ├── polls.py
│   │   │   ├── subscribers.py
│   │   │   └── admin.py
│   │   ├── services/
│   │   │   ├── rss_aggregator.py
│   │   │   ├── wikimedia.py
│   │   │   ├── beehiiv.py
│   │   │   ├── matching.py             # Algoritmo VAA (server-side mirror)
│   │   │   └── og_image.py             # Generación de cards para compartir
│   │   ├── jobs/
│   │   │   ├── pull_rss.py
│   │   │   ├── refresh_photos.py
│   │   │   ├── send_newsletter_digest.py
│   │   │   └── compute_poll_average.py
│   │   └── utils/
│   ├── migrations/                     # Alembic
│   │   ├── env.py
│   │   └── versions/
│   └── tests/
│       ├── conftest.py
│       └── ...
│
├── infra/
│   ├── bootstrap-vps.sh                # Provisioning de VPS recién creado
│   ├── deploy.sh                       # git pull + rebuild + migrate + restart
│   ├── backup-postgres.sh              # Cron diario → R2
│   ├── restore-postgres.sh             # Restore desde R2 (testeo)
│   ├── cloudflare-origin-cert.txt      # Plantilla con instrucciones
│   └── README.md                       # Runbook operacional
│
└── docs/
    ├── content-guide.md                # Guía editorial (tono, neutralidad)
    ├── statement-codification.md        # Metodología VAA paso a paso
    ├── candidate-onboarding.md          # Cómo agregar un candidato
    ├── country-launch.md                # Checklist para lanzar nuevo país
    └── incident-response.md             # Qué hacer si algo se cae
```

---

## Fase 1 — Bootstrap del repo + infraestructura local

**Objetivo**: en un solo `docker compose up -d` debe levantarse todo el stack en local con datos seed mínimos, accesible en `http://localhost`.

### 1.1 Archivos a crear

- `README.md` con setup en 3 comandos.
- `.gitignore` (Python, Node, Docker, secretos).
- `.env.example` con todas las variables necesarias documentadas (ver Apéndice B).
- `docker-compose.yml` con servicios: `caddy`, `frontend`, `api`, `worker`, `postgres`, `redis`, `mailhog` (para newsletter dev).
- `docker-compose.prod.yml` con overrides: sin `mailhog`, sin volúmenes de bind, secrets via env file.
- `Caddyfile` para dev (HTTP) y `Caddyfile.prod` (HTTPS con Origin Cert de Cloudflare).
- `frontend/Dockerfile` (multi-stage: build con Node 22 alpine, serve estático con caddy o nginx alpine).
- `backend/Dockerfile` (Python 3.12-slim, uv como gestor de deps, comando configurable).
- Estructura básica de carpetas vacías con `.gitkeep`.

### 1.2 docker-compose.yml estructura

Servicios y sus comandos:

- `caddy`: imagen `caddy:2-alpine`, monta `./Caddyfile`, expone 80 y 443.
- `frontend`: build desde `./frontend`, expone 3000 internamente.
- `api`: build desde `./backend`, comando `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` en dev.
- `worker`: misma imagen que `api`, comando `python -m app.worker`.
- `postgres`: `pgvector/pgvector:pg16`, healthcheck con `pg_isready`, volumen para data.
- `redis`: `redis:7-alpine`, persistencia AOF activada.
- `mailhog` (solo dev): `mailhog/mailhog` puerto 8025.

Todas con `restart: unless-stopped` y red interna compartida.

### 1.3 Caddyfile (dev)

```caddy
:80 {
  handle /api/* {
    uri strip_prefix /api
    reverse_proxy api:8000
  }
  handle {
    reverse_proxy frontend:3000
  }
}
```

### 1.4 Caddyfile (producción)

```caddy
pre.voto, www.pre.voto {
  tls /etc/caddy/origin.crt /etc/caddy/origin.key
  encode gzip zstd
  
  handle /api/* {
    uri strip_prefix /api
    reverse_proxy api:8000
  }
  handle {
    reverse_proxy frontend:3000
  }
  
  header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "DENY"
    Referrer-Policy "strict-origin-when-cross-origin"
    Permissions-Policy "geolocation=(), camera=(), microphone=()"
    -Server
  }
}
```

### 1.5 Aceptación de Fase 1

- `git clone` + `cp .env.example .env` + `docker compose up -d` → todo arriba.
- `http://localhost` muestra una página placeholder con "pre.voto — pronto".
- `http://localhost/api/health` devuelve `{"status": "ok"}`.
- `docker compose logs` no muestra errores recurrentes.

### Prompt para Claude Code (Fase 1)

> "Ejecuta la Fase 1 del SPEC.md. Crea toda la estructura de archivos vacía con `.gitkeep`, escribe el `docker-compose.yml`, `Caddyfile`, ambos `Dockerfile`, `.env.example` exhaustivamente comentado, y un endpoint placeholder en FastAPI (`/health`) más una página placeholder en Astro. Al terminar quiero poder hacer `docker compose up -d` y abrir `http://localhost`. Confirma que sigue todas las restricciones del SPEC (sin React, sin Next.js, etc.)."

---

## Fase 2 — Modelo de datos y migraciones

**Objetivo**: schema completo de Postgres aplicado vía Alembic, con datos seed para Colombia.

### 2.1 Modelo conceptual

Entidades principales:

- **Country** — código ISO, nombre, idioma, fecha elección activa, estado (activo/archivado).
- **Election** — un país puede tener múltiples elecciones (1ra vuelta, 2da vuelta, intermedia). Cada una con tipo, fecha, descripción.
- **Candidate** — nombre, partido, foto (URL Wikimedia), bio corta, fuentes oficiales, color asignado, asociado a una Election.
- **Statement** — afirmación del quiz, categoría (economía/seguridad/social/etc), texto, peso. Asociado a una Election.
- **CandidatePosition** — posición de un candidato en un statement: valor (-2 a +2), cita textual fuente, URL fuente, fecha de fuente, codificador (persona/yo), notas. Tabla pivote candidate × statement.
- **Article** — slug, título, contenido markdown, autor, fecha publicación, country, tags, hero image URL, hero image attribution.
- **Source** — fuente RSS: URL, nombre, país, idioma, último fetch.
- **NewsItem** — item agregado de RSS: título, URL, fuente, fecha, snippet, country, status (raw/curated/published).
- **Poll** — encuesta: encuestadora, fecha campo, tamaño muestra, % por candidato (JSON), source URL, país, election.
- **PollAverage** — agregado computado: para una election en una fecha, % por candidato, intervalo, # encuestas incluidas.
- **Subscriber** — email, country, lang, suscrito a (lista IDs), fecha suscripción, status, beehiiv_id.
- **QuizCompletion** — datos agregados ANÓNIMOS para analítica: country, fecha, # statements respondidos, top match (candidate_id), session_id efímero. NUNCA respuestas individuales identificables.

### 2.2 Reglas duras del schema

- Todas las tablas con `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`.
- Todas con `created_at TIMESTAMPTZ DEFAULT now()` y `updated_at TIMESTAMPTZ DEFAULT now()`.
- Trigger `update_updated_at` en cada tabla.
- Soft delete vía `deleted_at TIMESTAMPTZ NULL` donde aplique (Article, NewsItem, Poll).
- Constraint en `CandidatePosition.value CHECK (value BETWEEN -2 AND 2)`.
- Constraint en `Statement.weight CHECK (weight BETWEEN 1 AND 3)` — 3 categorías de importancia.
- Índices en: `country_id` (en todas), `election_id`, `slug` (Article), `email` (Subscriber, único), `(country_id, published_at)` para listings.
- Habilitar extensión `pgvector` desde la primera migración. Reservar columna `embedding vector(1536)` en `Statement` y `Article` (rellena después).

### 2.3 Migraciones

- Configurar Alembic con autogeneración.
- Migración inicial: enable extensions (`pgcrypto`, `vector`, `pg_trgm`), todas las tablas, triggers, índices.
- Migración seed: datos mínimos para Colombia 2026 1ra vuelta (5 candidatos placeholder, 8 statements placeholder, 5 RSS sources).

### 2.4 Aceptación de Fase 2

- `alembic upgrade head` corre sin errores en una base vacía.
- `psql` permite consultar todas las tablas y los datos seed están presentes.
- Script `seed_colombia_2026.py` reproduce los datos seed idempotentemente.
- README de `/backend` documenta cómo correr migraciones.

### Prompt para Claude Code (Fase 2)

> "Ejecuta la Fase 2 del SPEC.md. Define los modelos SQLAlchemy en `/backend/app/models/` siguiendo la lista de entidades y reglas duras. Configura Alembic. Crea la migración inicial y una migración de seed para Colombia 2026 1ra vuelta con 5 candidatos ficticios marcados como `is_demo=True` y 8 statements de ejemplo. NO crees endpoints todavía (eso es Fase 3). Al final, `alembic upgrade head` y el script de seed deben correr limpio."

---

## Fase 3 — API REST (FastAPI)

**Objetivo**: API completo con OpenAPI auto-generado, listo para consumir desde el frontend.

### 3.1 Endpoints públicos

| Método | Path | Descripción |
|---|---|---|
| GET | `/api/health` | Healthcheck para Caddy. |
| GET | `/api/countries` | Lista países activos con próxima elección. |
| GET | `/api/countries/{code}` | Detalle país + elección activa. |
| GET | `/api/quiz/{country}/statements` | Statements de la elección activa, en orden. |
| POST | `/api/quiz/{country}/submit` | Recibe respuestas, devuelve afinidad calculada server-side, persiste analítica anónima. |
| GET | `/api/candidates/{country}` | Candidatos de la elección activa con foto, partido, bio breve. |
| GET | `/api/candidates/{country}/{slug}` | Detalle de un candidato + sus posiciones en los statements. |
| GET | `/api/articles/{country}` | Lista paginada artículos publicados. |
| GET | `/api/articles/{country}/{slug}` | Artículo individual. |
| GET | `/api/polls/{country}` | Encuestas individuales + promedio. |
| GET | `/api/polls/{country}/average` | Promedio agregado actual. |
| POST | `/api/subscribers` | Captura email para newsletter. Forwarda a Beehiiv. |

### 3.2 Endpoints admin (autenticados con API key simple en header)

| Método | Path | Descripción |
|---|---|---|
| POST | `/api/admin/candidates` | Crear candidato. |
| PATCH | `/api/admin/candidates/{id}` | Editar candidato. |
| POST | `/api/admin/candidates/{id}/positions` | Bulk-set posiciones. |
| POST | `/api/admin/statements` | Crear statement. |
| POST | `/api/admin/articles` | Crear artículo (markdown). |
| POST | `/api/admin/polls` | Crear poll. |
| POST | `/api/admin/jobs/pull-rss` | Disparar pull manual de RSS. |
| POST | `/api/admin/jobs/refresh-photos` | Refrescar fotos de Wikimedia. |

Admin auth: header `X-Admin-Key` validado contra `ADMIN_API_KEY` del env. No es robusto pero es suficiente día 1 para uso propio. Subir a OAuth proper en Fase 7.

### 3.3 Reglas de implementación

- Toda respuesta JSON debe seguir Pydantic schemas en `/backend/app/schemas/`.
- Toda request validada por schemas.
- Rate limiting con `slowapi`: 60 req/min por IP en endpoints públicos, 5 req/hora en `/api/subscribers` (anti-spam).
- CORS: solo `pre.voto`, `www.pre.voto`, `localhost:3000`, `localhost:4321`.
- Logging estructurado (JSON) con `structlog`. Cada request loggea: method, path, status, latency, ip (hash, no plain), country requested.
- `/api/quiz/submit` NUNCA guarda respuestas individuales identificables. Lo único que persiste: `(country, date, statements_answered, top_match_candidate_id, session_hash)` donde `session_hash = sha256(ip + user_agent + day)` truncado a 16 chars. Es solo para deduplicar completions en analítica.
- Endpoint `/api/quiz/submit` calcula afinidad en servidor para evitar manipulación, pero el frontend YA calculó la misma cosa en cliente — debe coincidir (testeable).

### 3.4 Algoritmo de matching (server-side)

```python
def compute_affinity(user_answers: dict[uuid, int], candidate_positions: dict[uuid, int], statement_weights: dict[uuid, int]) -> float:
    """
    user_answers: {statement_id: -2..+2}
    candidate_positions: {statement_id: -2..+2}
    statement_weights: {statement_id: 1..3}
    Returns: 0.0..100.0 affinity percentage.
    """
    total_weight = 0
    weighted_distance = 0
    for sid, user_v in user_answers.items():
        if user_v is None:
            continue
        if sid not in candidate_positions:
            continue
        cand_v = candidate_positions[sid]
        w = statement_weights.get(sid, 1)
        distance = abs(user_v - cand_v)
        weighted_distance += distance * w
        total_weight += 4 * w
    if total_weight == 0:
        return 0.0
    return round((1 - weighted_distance / total_weight) * 100, 1)
```

Debe replicarse byte-por-byte en `frontend/src/lib/quiz.ts` para que cliente y server coincidan.

### 3.5 Aceptación de Fase 3

- Swagger UI en `/api/docs` muestra todos los endpoints.
- `pytest` corre con cobertura mínima 60% en routers.
- `curl http://localhost/api/quiz/co/statements` devuelve los statements seed.
- `POST /api/quiz/co/submit` con un payload de prueba devuelve afinidades correctas.

### Prompt para Claude Code (Fase 3)

> "Ejecuta la Fase 3 del SPEC.md. Implementa los routers de FastAPI listados, con sus Pydantic schemas, rate limiting con slowapi, CORS, structlog, y el algoritmo de matching server-side. Incluye tests con pytest para al menos: el algoritmo, el endpoint `/quiz/submit`, y el rate limiting. Documenta cómo correr tests en el README de `/backend`."

---

## Fase 4 — Worker y jobs en background

**Objetivo**: pipeline automatizado de agregación de noticias, fotos y newsletters.

### 4.1 Jobs a implementar

**`pull_rss`** — corre cada 30 min:
- Lee tabla `sources`, fetchea cada RSS con `feedparser`.
- Para cada item nuevo (deduplica por URL): inserta en `news_items` con status `raw`.
- Loggea cuántos items nuevos.
- Rate-limita peticiones (1 por segundo por dominio).

**`refresh_photos`** — corre diario:
- Para cada candidato sin `photo_url` o con `photo_url` >30 días: query Wikimedia Commons API.
- Estrategia: buscar primero por nombre exacto, luego por nombre + país.
- Guarda URL + autor + licencia en `candidates.photo_*`.
- Falla suave: si no encuentra, deja `photo_url` null para que el frontend muestre placeholder de iniciales.

**`compute_poll_average`** — corre cuando se agrega una nueva poll:
- Calcula promedio ponderado de las últimas N encuestas (configurable, default 10).
- Pondera por tamaño muestral y recencia (decay exponencial con τ=14 días).
- Persiste en `poll_averages` con timestamp.

**`send_newsletter_digest`** — disparado manualmente desde admin endpoint:
- Genera contenido del newsletter en markdown desde últimos 14 días: top artículos, encuestas recientes, eventos próximos.
- Envía via Beehiiv API a la lista del país correspondiente.
- Loggea el envío en una tabla `newsletter_sends`.

### 4.2 Scheduler

- Usar APScheduler con `BackgroundScheduler`.
- Cron expressions en `app/jobs/schedule.py`.
- El worker corre indefinidamente; señal `SIGTERM` lo apaga limpiamente terminando jobs en curso.
- Logging de cada inicio/fin de job con duración.

### 4.3 Cola para tareas ad-hoc

- `spawn_background_task()` helper basado en `asyncio.create_task()`.
- Mantiene referencias fuertes al set `_background_tasks` para prevenir garbage collection.
- Excepciones capturadas y logueadas via structlog (no propagan).
- Ejemplo: `POST /admin/jobs/refresh-photos` despacha via `spawn_background_task(job_refresh_photos())` y retorna 202 inmediatamente.
- Migración futura: cuando el throughput sostenido exceda ~1 task/segundo, migrar a arq o similar cola Redis-backed.

### 4.4 Servicio RSS aggregator — código de partida

```python
import feedparser
import httpx
from sqlalchemy.dialects.postgresql import insert
from app.models import Source, NewsItem

async def pull_source(source: Source, db):
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(source.feed_url, headers={"User-Agent": "pre.voto-bot/1.0 (+https://pre.voto)"})
    parsed = feedparser.parse(resp.text)
    new_count = 0
    for entry in parsed.entries:
        url = entry.get("link")
        if not url:
            continue
        stmt = insert(NewsItem).values(
            source_id=source.id,
            country_id=source.country_id,
            title=entry.get("title", "")[:500],
            url=url,
            snippet=entry.get("summary", "")[:1000],
            published_at=entry.get("published_parsed"),
            status="raw",
        ).on_conflict_do_nothing(index_elements=["url"])
        result = await db.execute(stmt)
        if result.rowcount > 0:
            new_count += 1
    source.last_pulled_at = datetime.utcnow()
    await db.commit()
    return new_count
```

### 4.5 Servicio Wikimedia — patrón

Endpoint: `https://commons.wikimedia.org/w/api.php` con parámetros para buscar imagen del título del artículo Wikipedia del candidato. Guardar la URL `imageinfo` del primer resultado relevante, autor de `extmetadata.Artist`, licencia de `extmetadata.LicenseShortName`. Atribución obligatoria en el frontend con esos datos.

### 4.6 Aceptación de Fase 4

- `docker compose up worker` corre indefinidamente sin errores.
- Después de 30 min hay items en `news_items` desde feeds reales de prueba (configura 2 sources colombianos válidos en seed).
- Endpoint admin `POST /api/admin/jobs/pull-rss` dispara pull inmediato y devuelve conteo.
- Endpoint admin `POST /api/admin/jobs/refresh-photos` actualiza fotos de los 5 candidatos seed con foto de Wikimedia (los candidatos seed deben tener nombres genéricos suficientemente buscables, por ejemplo políticos históricos conocidos para que el test sea reproducible — Claude Code decide).

### Prompt para Claude Code (Fase 4)

> "Ejecuta la Fase 4 del SPEC.md. Implementa el worker con APScheduler + RQ, los 4 jobs descritos, los servicios `rss_aggregator.py` y `wikimedia.py`. Asegura que `docker compose up worker` lo levanta. Incluye al menos 1 test integración para el job de RSS contra un mock. Documenta en `/backend/README.md` cómo correr el worker en standalone para debugging."

---

## Fase 5 — Frontend Astro

**Objetivo**: sitio público completo, mobile-first, accesible, con quiz funcional.

### 5.1 Identidad visual (design system)

**Colores** (definir en `tailwind.config.mjs`):

- `ink`: `#1a1a1a` (texto primario)
- `ink-soft`: `#404040` (texto secundario)
- `ink-faint`: `#737373` (texto terciario, captions)
- `paper`: `#fafafa` (background)
- `paper-warm`: `#f5f3ef` (background secundario, cards)
- `line`: `#e5e5e5` (bordes)
- `brand`: `#D85A30` (el coral de pre.voto, acento, links, CTAs)
- `brand-dark`: `#993C1D` (hover)
- Para identificar candidatos: paleta de 6 colores neutros distinguibles asignables dinámicamente (`#1D9E75`, `#BA7517`, `#378ADD`, `#7F77DD`, `#993556`, `#5F5E5A`). NUNCA usar rojo o azul de forma que sugiera partidos específicos del país.

**Modo oscuro**: soportado, toggle manual + respeta `prefers-color-scheme`. Las mismas variables con dark counterparts.

**Tipografía**:

- Sans: **Inter Variable** self-hosted (no Google Fonts → privacidad + velocidad). Pesos 400, 500, 700. Tracking ligero negativo en displays.
- Mono: **JetBrains Mono Variable** para citas, código, datos.
- Escala: 14, 16, 18, 22, 28, 36, 48px. Line-height: 1.5 cuerpo, 1.2 displays.

**Espaciado**: múltiplos de 4. Padding de cards mínimo 16px móvil, 24px desktop. Max-width de contenido legible: 65ch.

**Tono visual**: serio, periodístico, accesible. Cero gradientes, cero glassmorphism, cero neon. Bordes 0.5-1px, radius 6-12px. Sombras solo focus ring.

**Iconografía**: Lucide (no FontAwesome). 16-20px en línea con texto, 24px decorativo.

**Accesibilidad mínima**:

- Contraste WCAG AA en todo texto.
- Foco visible siempre (no `outline: none`).
- Skip-to-content link.
- `aria-label` en botones icon-only.
- `lang` correcto en `<html>` por país.
- Quiz navegable solo con teclado.

### 5.2 Páginas

**`/` (Landing pan-LATAM)**

- Header: logo `pre.voto` (texto con dot coral), nav (Cómo funciona, Metodología, Sobre).
- Hero: H1 "Voto informado para Latinoamérica." + subcopy de 2 líneas + selector de país visual (grid de 4-6 países con bandera/nombre, los activos clickeables, los próximos en gris con fecha).
- Sección "Cómo funciona" en 3 pasos.
- Sección "Próximas elecciones" — timeline horizontal/vertical con las 5 ventanas electorales.
- Footer: enlaces, contacto, licencia (CC-BY), GitHub del proyecto.

**`/[country]/` (Landing por país)**

- Hero con la elección activa: "Colombia decide el 31 de mayo" + countdown.
- CTA primario gigante: "Hacer la brújula electoral" (3 min).
- Secundarios: ver candidatos, ver encuestas, leer análisis.
- Strip de últimos 3 artículos.
- Strip de últimas encuestas (promedio).
- Newsletter signup.

**`/[country]/quiz` (El VAA)**

- Esta es la página estrella. Es una isla Svelte completa (`QuizApp.svelte`).
- Funciona offline después de la primera carga (precachea statements + candidate positions via service worker… NO, mejor sin service worker para no complicar; cachea en memoria post-fetch).
- Tres pantallas: bienvenida → quiz → resultados. (Como el mockup que ya armamos).
- Estados intermedios persistidos en `sessionStorage` para no perder progreso si recarga.
- Al terminar: POST a `/api/quiz/submit`, recibe afinidades, muestra resultados.
- En resultados: barras de afinidad, breakdown clickeable por statement, opción de descargar/compartir card (genera SVG → PNG con `satori` o equivalente del lado servidor), CTA al newsletter.
- Sin tracking individual. Disclaimer permanente: "Esto NO es una encuesta de opinión; es una herramienta pedagógica".

**`/[country]/candidatos`**

- Grid de cards de candidatos.
- Click en card → `/[country]/candidatos/[slug]` con bio + sus posiciones en cada statement con cita fuente y enlace.

**`/[country]/encuestas`**

- Promedio agregado actual (con metodología).
- Lista de encuestas individuales (tabla scrolleable horizontal en móvil).
- Disclaimer sobre limitaciones legales (especialmente Colombia post-Ley 2494/2025).

**`/[country]/articulos`**

- Lista paginada de artículos.
- Cada uno como ArticleCard con hero image, título, dek, fecha, autor, tags.

**`/[country]/articulos/[slug]`**

- Artículo individual. Markdown renderizado limpio. Hero image grande. Atribución de foto si es de Wikimedia. Newsletter signup al final. Compartir.

**`/metodologia`** — Cómo codificamos posiciones, cómo calculamos afinidad, qué hacemos y qué no.

**`/sobre`** — Quién está detrás, financiamiento, código abierto, contacto.

**`/privacidad`** — Política clara, especialmente sobre el quiz (procesado en cliente, nada se guarda individualmente, etc.).

### 5.3 Componentes Astro clave

- `<Layout title slug country>` — base layout con head, header, footer.
- `<Header country>` — logo + nav + país actual + toggle dark mode.
- `<Footer>` — enlaces, licencia, GitHub.
- `<CandidateCard candidate>` — foto (con fallback iniciales si no hay), nombre, partido, color.
- `<ArticleCard article>` — hero, título, dek, meta.
- `<PollSummary average>` — barras de promedio actual.
- `<NewsletterSignup country>` — form que POSTea a `/api/subscribers`.
- `<Disclaimer variant="quiz|polls|methodology" />` — disclaimers reutilizables.

### 5.4 Islas Svelte

- `QuizApp.svelte` — el VAA completo (referenciar al mockup ya construido).
- `PollAggregator.svelte` — gráfica de líneas de promedios en el tiempo.
- `ResultsShare.svelte` — botones de share (X, WhatsApp, Telegram, copy link).

### 5.5 i18n

- `es` como default, `pt-BR` para Brasil.
- `astro-i18n` o simple JSON dicts en `/src/lib/i18n.ts`.
- Locale derivado del `[country]` param: `co|mx|ar|cl|pe → es`, `br → pt-BR`.

### 5.6 SEO y Open Graph

- Cada página con `<title>`, `<meta description>` específicos.
- Open Graph image por defecto + custom para artículos.
- Card OG del quiz "Tu afinidad con los candidatos" generada server-side cuando se comparte (endpoint `/api/og/quiz?country=co&top=cepeda&pct=82`).
- JSON-LD: `Article` schema en artículos, `Organization` en `/sobre`.
- `sitemap.xml` auto-generado por Astro.
- `robots.txt` con allow + sitemap.

### 5.7 Performance targets

- Lighthouse Performance >95 en móvil.
- Lighthouse Accessibility 100.
- Lighthouse SEO 100.
- LCP <1.5s en 4G simulada.
- Bundle JS <50KB gzip por página (excluyendo islas).

### 5.8 Aceptación de Fase 5

- Todas las páginas listadas existen y renderizan con datos del API.
- Quiz funciona end-to-end con los 8 statements y 5 candidatos seed.
- Mobile (375px) y desktop (1280px) ambos pulidos.
- Modo oscuro funciona en todas las páginas.
- Lighthouse en /co/quiz: Performance >90, A11y 100, SEO 100.

### Prompt para Claude Code (Fase 5)

> "Ejecuta la Fase 5 del SPEC.md. Construye todas las páginas y componentes listados, con el design system definido. La isla QuizApp.svelte debe replicar el flujo del mockup discutido (bienvenida, quiz con statements de la API, resultados con afinidades). Implementa i18n para `es` y `pt-BR`. Asegúrate de que Lighthouse en /co/quiz alcance los targets. Documenta en `/frontend/README.md` cómo correr en dev y cómo agregar una nueva página."

---

## Fase 6 — Generación de OG cards y compartir

**Objetivo**: cuando alguien comparte su resultado, el preview en redes muestra una card visual con su top match.

### 6.1 Endpoint generador

`GET /api/og/quiz?country=co&top=maria-restrepo&pct=82&second=andres-vega&second_pct=71`

- Devuelve PNG 1200×630.
- Tipografía Inter, layout con logo pre.voto + texto "Mi afinidad: 82% con María Restrepo" + bar comparativa.
- Implementar con `python-pillow` o con `satori-python` (más moderno, JSX-like). Recomendado: pillow simple para mantener stack en Python.
- Cache de 24h con headers `Cache-Control: public, max-age=86400`.
- Cloudflare cachea encima.

### 6.2 Botones de compartir

En la pantalla de resultados, después de calcular afinidad:

- X/Twitter: pre-llenado con "Hice la brújula electoral de pre.voto y mi afinidad principal es con [candidato] ([pct]%). Hazla tú: [URL]"
- WhatsApp: similar adaptado al medium.
- Telegram: similar.
- Copy link: copia URL con query params para recuperar el resultado.

URL compartida: `https://pre.voto/co/quiz?r=<base64 de top+pct>` — el frontend al detectar `?r=` muestra directamente el resultado (sin recálculo del lado servidor; no guardamos resultados).

### 6.3 Aceptación de Fase 6

- Abrir `https://pre.voto/api/og/quiz?country=co&top=...` muestra PNG legible.
- Compartir el link del resultado en X muestra la card como preview.
- Los botones de share abren el client correspondiente con texto correcto.

### Prompt para Claude Code (Fase 6)

> "Ejecuta la Fase 6 del SPEC.md. Implementa el endpoint `/api/og/quiz` que genera PNG 1200×630 con pillow, cacheable. Implementa el componente `ResultsShare.svelte` con los 4 botones. Asegura que el preview en X/Facebook funciona (testea con el debugger de Meta y la card validator de X)."

---

## Fase 7 — Deployment a producción

**Objetivo**: pre.voto en vivo en un VPS Hetzner, con TLS via Cloudflare, backups corriendo.

### 7.1 Bootstrap del VPS — `infra/bootstrap-vps.sh`

Script idempotente que en un Ubuntu 24.04 recién creado:

1. `apt update && apt upgrade -y`.
2. Crea usuario `deploy` con sudo, sin password (solo SSH key).
3. Deshabilita login root por SSH, deshabilita password auth.
4. Instala `ufw`, configura: deny incoming, allow 22, 80, 443. Enable.
5. Instala Docker + Docker Compose plugin oficial.
6. Instala `rclone` y configura remote `r2:` desde variables de entorno.
7. Instala `unattended-upgrades` con security patches automáticos.
8. Crea `/opt/prevoto`, clona el repo (vía deploy key).
9. Provee plantilla `.env.production` que el operador debe completar manualmente.
10. Configura swap (2GB) por si acaso.
11. Configura zona horaria UTC.
12. Imprime "next steps" al final.

### 7.2 Deployment script — `infra/deploy.sh`

Ejecutable desde local con SSH a la VPS:

```bash
ssh deploy@$VPS_HOST 'cd /opt/prevoto && git pull && docker compose -f docker-compose.yml -f docker-compose.prod.yml pull && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build && docker compose exec -T api alembic upgrade head && docker compose exec -T api python -m app.scripts.warmup'
```

Con health check al final que confirme `https://pre.voto/api/health` devuelve 200.

### 7.3 Cloudflare

Documentar en `/infra/README.md` los pasos exactos:

1. Cambiar nameservers de `pre.voto` a Cloudflare.
2. Crear A record `pre.voto` → IP VPS, proxied (nube naranja).
3. Crear A record `www.pre.voto` → IP VPS, proxied.
4. SSL/TLS mode: **Full (strict)**.
5. Generar Origin Certificate (15-year, *.pre.voto, pre.voto). Guardar como `origin.crt` y `origin.key` en VPS en `/etc/caddy/`.
6. Page Rules: cachear `/_astro/*`, `/fonts/*`, `/og/*` por 1 año.
7. Cache Rules: cachear HTML por 5 min (status 200), bypass para `/api/*`.
8. WAF: rate limit `/api/*` a 100 req/min por IP.
9. Speed → Brotli: on.
10. Security level: Medium.

### 7.4 Backups

`infra/backup-postgres.sh` (cron diario 3am UTC):

```bash
docker compose exec -T postgres pg_dump -U prevoto prevoto | gzip | rclone rcat r2:prevoto-backups/$(date +%Y%m%d).sql.gz
rclone delete --min-age 30d r2:prevoto-backups/  # retención 30 días
```

`infra/restore-postgres.sh` — script de restore para testear mensualmente.

### 7.5 Monitoreo

- **Uptime**: UptimeRobot free tier monitoreando `https://pre.voto/api/health` cada 5 min con alerta a email.
- **Logs**: `docker compose logs` rotados via `logrotate` config en `/etc/logrotate.d/docker`.
- **Métricas básicas**: Plausible Analytics self-hosted como otro servicio del compose (Fase 8 opcional).

### 7.6 Aceptación de Fase 7

- Bootstrap script en VPS fresca llega al final sin errores.
- Deploy script ejecutado deja `https://pre.voto` accesible con TLS válido.
- Cloudflare cachea correctamente.
- Backup automático corre y aparece en R2.
- Restore script restaura exitosamente en un VPS de prueba.

### Prompt para Claude Code (Fase 7)

> "Ejecuta la Fase 7 del SPEC.md. Crea todos los scripts en `/infra/`, el `docker-compose.prod.yml` override, y el `Caddyfile.prod`. Documenta en `/infra/README.md` el procedimiento paso a paso de cero a producción. Incluye troubleshooting de los 5 errores más comunes (DNS propagation, certificado origin mal copiado, firewall bloqueando, alembic stuck, OOM)."

---

## Fase 8 — Launch Colombia (operacional, no técnico)

**Objetivo**: pre.voto/co en vivo con contenido real para 1ra vuelta del 31 mayo.

Esta fase es 80% trabajo editorial, 20% técnico.

### 8.1 Contenido a producir

- **25 statements** finales para Colombia 2026 (no los 8 seed). Cubrir: economía (4), seguridad y diálogos (3), política exterior (2), social/aborto/género (3), drogas/glifosato (2), medio ambiente (2), reforma política (2), salud (2), educación (2), Venezuela (1), reforma pensional (1), implementación acuerdo de paz (1).
- **Posiciones codificadas** para los 5-7 candidatos con mejor intención de voto, con 1-2 citas fuente por posición. Fuentes admisibles: plan de gobierno oficial registrado ante el CNE, debates registrados en video, entrevistas en medios serios (El Tiempo, El Espectador, Semana, La Silla Vacía), tweets oficiales de la cuenta verificada del candidato.
- **6-10 artículos** publicados antes del lanzamiento: 1 explicador del sistema electoral, 1 perfil por candidato top, 1 análisis de últimas encuestas, 1 metodología de pre.voto, 1 sobre cómo se codificaron las posiciones.
- **Página `/metodologia`** completa y firmada por el equipo (aunque seas tú solo).

### 8.2 Setup operacional

- **Newsletter en Beehiiv**: lista "pre.voto Colombia", primer email programado para 7 días antes de elección.
- **Cuentas sociales mínimas**: @prevotoLATAM en X, perfil en LinkedIn. Bio: "Brújula electoral pan-LATAM. Voto informado, independiente, código abierto."
- **GitHub público del repo** (al menos del frontend o de la metodología, no necesariamente backend completo). Esto da credibilidad de transparencia.
- **Consejo asesor declarado**: lista de 3-5 personas (académicos, periodistas) que validan neutralidad. Pueden ser informales al inicio pero deben aparecer en `/sobre`.

### 8.3 Compliance Colombia día 1

- Disclaimer permanente en `/co/quiz`: "Esta herramienta no constituye una encuesta de opinión pública en los términos de la Ley 2494 de 2025. Es una herramienta pedagógica de afinidad ideológica basada en posiciones públicas autocodificadas."
- Veda electoral Colombia: bloquear `/co/quiz` el día de la elección. Implementar como feature flag `quiz_disabled_during_veda` que se activa por país y rango de fechas.
- Política de privacidad muy explícita sobre que no se almacenan respuestas individuales del quiz.

### 8.4 Distribución día de lanzamiento

- Thread en X con resultado del quiz hecho por ti, etiquetando a 20 cuentas civic-tech LATAM relevantes.
- Email personal a 30 contactos del ecosistema (periodistas, académicos, otros civic tech).
- Submit a Hacker News (en inglés) con framing técnico ("Show HN: pre.voto — open-source Voting Advice Application for Latin America").
- Submit a r/Colombia, r/colombia_politica.
- Mensaje a 3-5 medios colombianos pidiendo amplificación: La Silla Vacía, Cuestión Pública, Vorágine, El Espectador.

### 8.5 Aplicaciones a grants en paralelo

- **Pulsante Rapid Response Fund** (Avina) — ciclo mensual. Aplicar primer semana post-lanzamiento.
- **NED** (National Endowment for Democracy) — siguiente ciclo. Framing: "Pan-LATAM civic tech platform addressing the regional gap in voter information."
- **Google News Initiative LATAM** — cuando se abra siguiente convocatoria.

### Prompt para Claude Code (Fase 8 — solo lo técnico)

> "Para la Fase 8 del SPEC.md, implementa solo lo técnico: el feature flag de veda electoral por país, el disclaimer de Ley 2494/2025 visible en `/co/quiz`, y un comando admin `python -m app.scripts.set_veda --country co --start 2026-05-29 --end 2026-05-31` que activa/desactiva el lock. El contenido editorial lo produzco yo."

---

## Fase 9 — Iteración y país siguiente

Después de Colombia, **postmortem público obligatorio**: artículo con métricas (completions, conversiones a newsletter, top statements polarizantes según afinidades agregadas). Esto es SEO gold perpetuo y construye credibilidad.

Para Brasil, la Fase 9 requiere antes:

- Contratar representante legal en Brasil (~$200-500/mes via abogado o servicio). NO LANZAR SIN ESTO.
- Implementar bilingüismo `pt-BR` completo.
- Configurar mecanismo de takedown <24h por orden judicial (endpoint admin + log auditable).
- Etiquetado obligatorio "Conteúdo gerado com auxílio de IA" en cualquier resumen escrito con LLM, según Resolução TSE 23.732/2024.

Repetir el ciclo: codificar statements brasileños (escala mayor, ~30 statements), codificar posiciones de Lula + opositores principales, lanzar `pre.voto/br` 6-8 semanas antes del 4 de octubre.

---

## Apéndice A — Plantilla de prompts para Claude Code

Para cada fase, usar siempre este preámbulo:

> "Voy a pedirte ejecutar la Fase X del archivo SPEC.md que está en la raíz. Antes de tocar archivos:
> 
> 1. Lee SPEC.md completo otra vez si no lo tienes en contexto.
> 2. Lee la fase ya completada inmediatamente anterior para entender el estado.
> 3. Haz `git status` y confirma que estamos en una rama limpia.
> 4. Crea una rama nueva `feature/fase-X-<nombre>` desde main.
> 5. Resume tu plan de ejecución en máximo 10 puntos y espera mi 'go'.
> 6. Después de mi 'go', ejecuta paso por paso, commiteando frecuentemente con mensajes descriptivos.
> 7. Al terminar, abre un PR draft con la descripción de cambios y los criterios de aceptación marcados.
> 
> No avances si encuentras ambigüedad real — pregúntame."

Reglas globales para Claude Code:

- Nunca push directo a main.
- Nunca borres datos sin confirmación explícita.
- Nunca subas secrets al repo (usar `.env`, jamás commitearlo).
- Si la fase implica tocar producción, pídeme confirmación dos veces.
- Si encuentras tarea fuera de scope de la fase, abre issue en lugar de hacerla.

---

## Apéndice B — Variables de entorno

`.env.example` debe documentar todas. Lista completa esperada:

```
ENV=development  # development | production

POSTGRES_USER=prevoto
POSTGRES_PASSWORD=changeme-use-openssl-rand
POSTGRES_DB=prevoto
DATABASE_URL=postgresql+asyncpg://prevoto:changeme@postgres:5432/prevoto

REDIS_URL=redis://redis:6379/0

ADMIN_API_KEY=changeme-use-openssl-rand-base64-32

BEEHIIV_API_KEY=
BEEHIIV_PUBLICATION_ID=

CLOUDFLARE_R2_ACCESS_KEY=
CLOUDFLARE_R2_SECRET_KEY=
CLOUDFLARE_R2_ENDPOINT=
CLOUDFLARE_R2_BUCKET=prevoto-backups

WIKIMEDIA_USER_AGENT=pre.voto-bot/1.0 (https://pre.voto; contact@pre.voto)

SENTRY_DSN=  # opcional, dejar vacío al inicio

PUBLIC_API_URL=http://localhost  # en frontend; en prod: https://pre.voto
PUBLIC_SITE_URL=http://localhost

RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_SUBSCRIBE_PER_HOUR=5

VEDA_ENABLED_CO=false
VEDA_START_CO=
VEDA_END_CO=
```

---

## Apéndice C — Schemas SQL críticos (resumen)

Para que Claude Code arranque bien la Fase 2, aquí los CREATEs más importantes en pseudocódigo SQL:

```sql
CREATE TABLE countries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code CHAR(2) UNIQUE NOT NULL,         -- ISO 3166-1: co, mx, br, ar...
  name TEXT NOT NULL,
  language TEXT NOT NULL,                -- es, pt-BR
  is_active BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE elections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country_id UUID REFERENCES countries(id),
  type TEXT NOT NULL,                    -- presidential_r1, presidential_r2, midterm, general
  election_date DATE NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE candidates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  election_id UUID REFERENCES elections(id),
  slug TEXT NOT NULL,
  name TEXT NOT NULL,
  party TEXT,
  party_acronym TEXT,
  bio_short TEXT,
  photo_url TEXT,
  photo_author TEXT,
  photo_license TEXT,
  photo_attribution TEXT,
  color HEX,
  is_demo BOOLEAN DEFAULT false,
  sources JSONB DEFAULT '[]',            -- [{title, url, type}]
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(election_id, slug)
);

CREATE TABLE statements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  election_id UUID REFERENCES elections(id),
  text TEXT NOT NULL,
  category TEXT,                          -- economy, security, social, environment...
  weight INT DEFAULT 1 CHECK (weight BETWEEN 1 AND 3),
  display_order INT,
  embedding VECTOR(1536),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE candidate_positions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id UUID REFERENCES candidates(id),
  statement_id UUID REFERENCES statements(id),
  value INT NOT NULL CHECK (value BETWEEN -2 AND 2),
  source_quote TEXT,
  source_url TEXT,
  source_date DATE,
  coded_by TEXT,
  coded_at TIMESTAMPTZ DEFAULT now(),
  notes TEXT,
  UNIQUE(candidate_id, statement_id)
);

CREATE TABLE articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country_id UUID REFERENCES countries(id),
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  dek TEXT,
  body_markdown TEXT NOT NULL,
  hero_image_url TEXT,
  hero_image_attribution TEXT,
  author TEXT,
  tags TEXT[],
  published_at TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ,
  embedding VECTOR(1536),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(country_id, slug)
);

CREATE TABLE sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country_id UUID REFERENCES countries(id),
  name TEXT NOT NULL,
  feed_url TEXT NOT NULL UNIQUE,
  site_url TEXT,
  last_pulled_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE news_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID REFERENCES sources(id),
  country_id UUID REFERENCES countries(id),
  url TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  snippet TEXT,
  published_at TIMESTAMPTZ,
  status TEXT DEFAULT 'raw',              -- raw, curated, published, discarded
  fetched_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE polls (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  election_id UUID REFERENCES elections(id),
  pollster TEXT NOT NULL,
  field_start DATE NOT NULL,
  field_end DATE NOT NULL,
  sample_size INT,
  methodology TEXT,
  results JSONB NOT NULL,                  -- {candidate_id: percentage}
  source_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE poll_averages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  election_id UUID REFERENCES elections(id),
  computed_at TIMESTAMPTZ DEFAULT now(),
  results JSONB NOT NULL,                  -- {candidate_id: {avg, low, high}}
  polls_included INT
);

CREATE TABLE subscribers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  country_code CHAR(2),
  language TEXT DEFAULT 'es',
  beehiiv_id TEXT,
  source TEXT,                              -- quiz, footer, article, other
  status TEXT DEFAULT 'pending',            -- pending, confirmed, unsubscribed
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE quiz_completions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  election_id UUID REFERENCES elections(id),
  session_hash TEXT,
  statements_answered INT,
  top_match_candidate_id UUID REFERENCES candidates(id),
  top_match_pct NUMERIC(4,1),
  completed_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Apéndice D — Guía editorial mínima

**Tono**: periodístico, objetivo, accesible. Lectura de 8° grado.

**Cómo NO escribir**:

- Nada de "los radicales de izquierda" o "la extrema derecha" como descriptores. Usar nombre del partido/coalición y, si necesario, "considerada de izquierda por el espectro político" con cita académica.
- Nada de "obvio que", "claramente", "no es difícil ver", "como sabemos".
- Nada de exclamaciones.
- Nada de emoji en cuerpo de artículo.

**Cómo escribir**:

- Encabezados informativos, no clickbait.
- Cada afirmación factual con fuente enlazada.
- Voz activa.
- Si citas a un candidato, contextualizar fecha + lugar + medio donde lo dijo.
- Después de un párrafo crítico de cualquier candidato, ofrecer la versión opuesta o el contexto que el lector necesita para juzgar.

**Codificación de posiciones** (proceso paso a paso):

1. Leer plan de gobierno oficial completo del candidato.
2. Por cada statement, buscar la frase más cercana en el plan.
3. Si no aparece en el plan, buscar en debates registrados en video con timestamp.
4. Si tampoco, buscar 2 entrevistas en medios serios distintos.
5. Si las dos coinciden, codificar. Si discrepan, marcar como "posición ambigua" (valor 0 con nota).
6. Si no hay fuente clara: NO inventar. Codificar como `null` (el quiz simplemente no usa ese statement para ese candidato).
7. Cada posición codificada debe tener: cita exacta entre comillas (≤20 palabras), URL fuente, fecha de la fuente, tu nombre como codificador.

---

## Resumen ejecutivo

9 fases. Tiempo estimado solo: 4-6 semanas hasta Colombia en vivo. Costo de infra: $10/mes. Trabajo más demandante: codificar posiciones de candidatos (40-60 horas para los 5-7 candidatos colombianos con metodología rigurosa). Lo que va a fallar primero: alguno cuestionará tu neutralidad — tener metodología pública, consejo asesor visible, y código abierto desde día 1 te blinda.

Cuando dudes, vuelve a la regla rectora: **pragmático sobre elegante, neutral sobre vistoso, accionable sobre completo**.

Empieza con la Fase 1. Suerte.
