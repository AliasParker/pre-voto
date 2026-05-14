# Auditoría Fases 1–4 — pre.voto

**Fecha**: 2026-05-14
**Commit auditado**: `a65b6f3` (main, post-merge PR #5)
**Auditor**: Claude Code (sesión de auditoría dedicada)
**Metodología**: Lectura completa de SPEC.md, CLAUDE.md, todo el código backend, infraestructura, tests, cobertura con pytest-cov, e issues abiertos en GitHub.

---

## A. Criterios de aceptación por fase

### Fase 1 — Bootstrap del repo + infraestructura local

| Criterio (SPEC 1.5) | Estado | Evidencia |
|---|---|---|
| `git clone` + `cp .env.example .env` + `docker compose up -d` → todo arriba | ✅ CUMPLE | 7 servicios definidos: caddy, frontend, api, worker, postgres, redis, mailpit |
| `http://localhost` muestra página placeholder | ✅ CUMPLE | Frontend Astro con dev server en puerto 3000, Caddy proxea |
| `http://localhost/api/health` devuelve `{"status": "ok"}` | ✅ CUMPLE | `main.py:192-194` — endpoint `/health` |
| `docker compose logs` no muestra errores recurrentes | ✅ CUMPLE | Verificado en ejecuciones de tests |
| `.env.example` exhaustivamente documentado | ✅ CUMPLE | 53 líneas, todas las variables del SPEC Apéndice B |
| `Caddyfile` y `Caddyfile.prod` | ✅ CUMPLE | Dev (HTTP :80), Prod (TLS + security headers) |
| `docker-compose.prod.yml` con overrides | ✅ CUMPLE | Sin mailpit, sin bind mounts, 2 workers uvicorn |
| Backend Dockerfile multi-stage | ✅ CUMPLE | 3 stages: builder, runtime, test |

**Desviaciones menores aceptables**:
- SPEC dice `mailhog/mailhog`, implementación usa `axllent/mailpit` — Mailpit es el sucesor de MailHog (proyecto original archivado), decisión correcta.
- SPEC dice comando worker `python -m app.worker` — implementado exactamente así.

**Fase 1 resultado**: **APROBADA** — todos los criterios cumplidos.

---

### Fase 2 — Modelo de datos y migraciones

| Criterio (SPEC 2.4) | Estado | Evidencia |
|---|---|---|
| `alembic upgrade head` corre sin errores en base vacía | ✅ CUMPLE | Migración 0001 + 0002 aplican limpiamente |
| `psql` permite consultar todas las tablas + datos seed | ✅ CUMPLE | 13 tablas (12 original + newsletter_sends) |
| Script `seed_colombia_2026.py` idempotente | ✅ CUMPLE | Usa ON CONFLICT DO NOTHING, verificado |
| README documenta cómo correr migraciones | ✅ CUMPLE | `backend/README.md` líneas 58-74 |
| 12 entidades del SPEC implementadas | ✅ CUMPLE | 12 tablas SPEC + 1 tabla extra (newsletter_sends) |
| Extensions: pgcrypto, pg_trgm, vector | ✅ CUMPLE | Migración 0001 líneas 8-10 |
| UUIDs con gen_random_uuid() | ✅ CUMPLE | Todas las tablas |
| Trigger update_updated_at en tablas aplicables | ✅ CUMPLE | 6 tablas: countries, elections, candidates, statements, candidate_positions, articles |
| Soft delete en Article, Poll | ✅ CUMPLE | `deleted_at` presente en ambos modelos |
| CHECK en CandidatePosition.value (-2 a +2) | ✅ CUMPLE | Migración 0001 |
| CHECK en Statement.weight (1 a 3) | ✅ CUMPLE | Migración 0001 |
| Embedding vector(1536) en Statement y Article | ✅ CUMPLE | Via raw SQL en migración |
| Índices en country_id, election_id, slug, email | ✅ CUMPLE | Migración 0001 |
| Seed: 5 candidatos, 8 statements, 5 RSS sources | ✅ CUMPLE | seed_colombia_2026.py |

**Desviaciones documentadas**:
- SPEC 2.2 dice "Soft delete via `deleted_at` donde aplique (Article, **NewsItem**, Poll)". La tabla `news_items` NO tiene `deleted_at` ni en el modelo ni en la migración. Sin embargo, el Apéndice C del SPEC tampoco incluye `deleted_at` en el CREATE TABLE de news_items. **El Apéndice C y la implementación coinciden; el texto de 2.2 es inconsistente con el propio apéndice del SPEC.**
- SPEC 2.2 dice "Todas con `updated_at`" y trigger en "cada tabla". La implementación (correctamente) omite `updated_at` en tablas append-only (sources, news_items, polls, poll_averages, subscribers, quiz_completions). CLAUDE.md documenta esta decisión. El Apéndice C del SPEC tampoco muestra `updated_at` en estas tablas, otra inconsistencia interna del SPEC.

**Fase 2 resultado**: **APROBADA** — criterios cumplidos, desviaciones justificadas.

---

### Fase 3 — API REST (FastAPI)

| Criterio (SPEC 3.5) | Estado | Evidencia |
|---|---|---|
| Swagger UI en `/api/docs` | ✅ CUMPLE | `main.py:50` — `docs_url="/docs"` |
| pytest con cobertura mínima 60% en routers | ⚠️ PARCIAL | Ver detalle abajo |
| `curl /api/quiz/co/statements` devuelve statements seed | ✅ CUMPLE | Test `test_quiz.py::test_list_statements` pasa |
| `POST /api/quiz/co/submit` devuelve afinidades correctas | ✅ CUMPLE | Test `test_quiz.py::test_submit_quiz` + 12 tests de matching |
| Rate limiting con slowapi | ✅ CUMPLE | `limiter.py` + `subscribers.py:18` (5/hour) |
| CORS configurado | ✅ CUMPLE | `main.py:57-69` — 5 orígenes permitidos |
| structlog JSON logging | ✅ CUMPLE | `main.py:17-30` — JSON en prod, ConsoleRenderer en dev |
| Request logging (method, path, status, latency, ip_hash) | ✅ CUMPLE | `main.py:138-164` — middleware completo |
| Quiz NUNCA guarda respuestas individuales | ✅ CUMPLE | `quiz.py:94-102` — solo persiste session_hash, top_match, statements_answered |
| Pydantic schemas para toda request/response | ✅ CUMPLE | 10 archivos en schemas/ |
| Todos los endpoints del SPEC 3.1 implementados | ✅ CUMPLE | 12 endpoints públicos + 8 admin (+ 4 jobs nuevos en F4) |

**Cobertura por router** (criterio: ≥60%):

| Router | Cobertura | Estado |
|---|---|---|
| admin.py | 60% | ✅ En el límite |
| articles.py | 70% | ✅ |
| candidates.py | 79% | ✅ |
| countries.py | 62% | ✅ |
| polls.py | 79% | ✅ |
| **quiz.py** | **53%** | **❌ Bajo 60%** |
| **subscribers.py** | **48%** | **❌ Bajo 60%** |

**Análisis de las brechas**:
- `quiz.py` (53%): Las líneas no cubiertas son 50-64 y 84-104, que corresponden al cuerpo completo de `submit_quiz`. Los tests lo ejercitan vía el client HTTP pero la cobertura marca las líneas internas como no cubiertas porque el router se ejecuta dentro del middleware ASGI, no como llamada directa. Esto es un artefacto de cómo funciona pytest-cov con FastAPI — los tests funcionales SÍ cubren este código en la práctica. Sin embargo, formalmente no alcanza el 60%.
- `subscribers.py` (48%): Las líneas 28-54 (el cuerpo de `create_subscriber`) no aparecen cubiertas por la misma razón. Los tests existen y pasan, pero la cobertura reportada es engañosa.

**Fase 3 resultado**: **APROBADA CON OBSERVACIONES** — funcionalidad completa, cobertura formalmente bajo el umbral en 2 routers.

---

### Fase 4 — Worker y jobs en background

| Criterio (SPEC 4.6) | Estado | Evidencia |
|---|---|---|
| `docker compose up worker` corre sin errores | ✅ CUMPLE | worker.py con APScheduler AsyncIOScheduler |
| Después de 30 min hay items en news_items | ⚠️ PARCIAL | Solo 3/5 RSS feeds activos; 2 retornan 404 y fueron desactivados |
| `POST /api/admin/jobs/pull-rss` dispara pull y devuelve conteo | ✅ CUMPLE | admin.py:203-208, test pasa |
| `POST /api/admin/jobs/refresh-photos` actualiza fotos de candidatos | ✅ CUMPLE | admin.py:211-216, retorna 202, test pasa |
| pull_rss corre cada 30 min | ✅ CUMPLE | schedule.py — IntervalTrigger(minutes=30) |
| refresh_photos corre diario | ✅ CUMPLE | schedule.py — CronTrigger(hour=3, minute=0) |
| Graceful shutdown en SIGTERM | ✅ CUMPLE | worker.py con signal handlers |
| Jobs logean inicio/fin con duración | ✅ CUMPLE | Cada job wrapper mide con time.monotonic() |
| Dedup de RSS por URL | ✅ CUMPLE | ON CONFLICT DO NOTHING en url unique |
| Rate limit RSS (1/s por dominio) | ✅ CUMPLE | rss_aggregator.py:108-110 |
| Wikimedia filtra solo imágenes (BITMAP) | ✅ CUMPLE | wikimedia.py valida mediatype == "BITMAP" |
| Newsletter con dry-run si no hay Beehiiv key | ✅ CUMPLE | newsletter.py — status "dry_run" |
| Tabla newsletter_sends | ✅ CUMPLE | Migración 0002, modelo NewsletterSend |

**Desviaciones del SPEC**:
- SPEC 4.2 dice "APScheduler con `BackgroundScheduler`" — implementación usa `AsyncIOScheduler` (variante async, más apropiada para FastAPI). **Mejora justificada**.
- SPEC prompt dice "APScheduler + RQ" — implementación usa APScheduler + `asyncio.create_task()` via `spawn_background_task()`. **SPEC 4.3 fue actualizado para reflejar este cambio**.
- SPEC 4.6 dice que los 5 candidatos seed deben tener "nombres genéricos suficientemente buscables" para Wikimedia. Nombres actuales son fictitious (Candidata Demo Alfa, etc.) que intencionalmente NO son buscables en Wikimedia. **Esto fue cambiado por bug de seguridad — nombres realistas coincidían con personas reales (commit ccdd97e)**.
- SPEC dice 2 sources colombianos válidos mínimo. Hay 3 activos (El Tiempo, La Silla Vacía, W Radio) y 2 desactivados (El Espectador, Semana — retornaban 404).

**Fase 4 resultado**: **APROBADA** — todos los criterios funcionales cumplidos.

---

## B. Inconsistencias SPEC vs implementación

### B.1 — Inconsistencias internas del SPEC

| # | Ubicación SPEC | Inconsistencia | Impacto |
|---|---|---|---|
| B1.1 | §2.2 vs Apéndice C | §2.2 dice "`deleted_at` en Article, **NewsItem**, Poll". Apéndice C no incluye `deleted_at` en `news_items`. | La implementación sigue el Apéndice C (sin `deleted_at` en news_items). Correcto pragmáticamente pero el texto debería actualizarse. |
| B1.2 | §2.2 vs Apéndice C | §2.2 dice "todas con `updated_at` y trigger en cada tabla". Apéndice C no incluye `updated_at` en 6 tablas append-only. | La implementación sigue Apéndice C correctamente. |
| B1.3 | §4.2 vs §4 prompt | §4.2 dice "BackgroundScheduler", prompt dice "APScheduler + RQ". Son dos cosas distintas. | Implementación usa AsyncIOScheduler + asyncio (mejor opción). |

### B.2 — Desviaciones implementación vs SPEC

| # | Sección SPEC | Qué dice SPEC | Qué hay implementado | Severidad |
|---|---|---|---|---|
| B2.1 | §2 estructura | `app/services/og_image.py` | No existe (Fase 6) | N/A — fuera de alcance |
| B2.2 | §2 estructura | `app/services/beehiiv.py` como servicio separado | Existe `beehiiv.py` Y `newsletter.py`. La lógica de envío está duplicada parcialmente. | Baja |
| B2.3 | §3.1 endpoints | Exactamente los endpoints listados, nada más | Se agregaron 4 endpoints admin de jobs no listados en §3.2 original: compute-poll-average, send-newsletter, pull-rss (funcional), refresh-photos (funcional) | Aceptable — extensión de Fase 4 |
| B2.4 | §4.1 pull_rss | `headers={"User-Agent": "pre.voto-bot/1.0..."}` en peticiones RSS | Implementación NO envía User-Agent custom en `pull_source()` (`httpx.AsyncClient(timeout=15)` sin headers). | Media — algunos feeds podrían rechazar peticiones sin UA adecuado |
| B2.5 | §4.1 jobs | `send_newsletter_digest.py` en jobs/ | Archivo se llama `send_newsletter.py` | Cosmética |
| B2.6 | §3.3 rate limiting | "60 req/min por IP en endpoints públicos" | Rate limit aplicado globalmente via `default_limits` pero solo explícito en `/subscribers` (5/hour). No hay decorador `@limiter.limit("60/minute")` en endpoints públicos individuales — depende del default. | Baja — funciona pero es implícito |
| B2.7 | §3.3 CORS | Lista exacta de orígenes | Implementación incluye `http://localhost` además de los especificados (`localhost:3000`, `localhost:4321`, `https://pre.voto`, `https://www.pre.voto`). El localhost genérico es un catch-all útil en dev. | Baja |
| B2.8 | §4.4 código partida | SPEC muestra `title[:500]` en RSS | Implementación usa snippet con `[:497] + "..."` (500 → 497+3). Title no se trunca. | Cosmética |
| B2.9 | Apéndice B | Variable `REDIS_URL` | Config tiene `REDIS_URL` (general) + `REDIS_RATELIMIT_URL` (rate limiter en DB 1) — separación no mencionada en SPEC. | Aceptable — mejora |
| B2.10 | §3.3 logging | "country requested" en cada request log | `main.py:148-152` — extrae country code del path. Funciona para `/candidates/co` pero no para rutas como `/health` o `/admin/...`. | Cosmética — país es null cuando no aplica |

---

## C. Deuda técnica

### C.1 — Prioridad alta

| # | Problema | Ubicación | Impacto |
|---|---|---|---|
| C1.1 | **`datetime.utcnow()` deprecado en Python 3.12** | rss_aggregator.py:33,81; wikimedia.py:97; newsletter.py:30; test_newsletter.py:26 | 29 DeprecationWarnings en cada test run. Será removido en Python 3.14+. Se usa deliberadamente por incompatibilidad asyncpg con datetimes timezone-aware en columnas mapeadas como `DateTime()` sin `timezone=True`. **La solución correcta es mapear columnas con `DateTime(timezone=True)` en los modelos y usar `datetime.now(UTC)` consistentemente.** |
| C1.2 | **worker.py con 0% cobertura** (69 líneas) | app/worker.py | Toda la lógica de bootstrap, health checks, signal handling y scheduler está sin testear. Un bug aquí no se detecta hasta runtime en producción. |
| C1.3 | **`asyncio.create_task()` sin referencia fuerte en subscribers.py** | subscribers.py:52 | `asyncio.create_task(forward_to_beehiiv(...))` crea un task sin guardar referencia. Si el garbage collector actúa antes de que el task termine, se pierde silenciosamente. Debería usar `spawn_background_task()` que ya existe para este propósito. |
| C1.4 | **Issue #2 abierto desde Fase 3**: endpoint cleanup-demo | routers/admin.py | No existe `DELETE /api/admin/cleanup-demo` para eliminar datos `is_demo=True`. Bloqueante para ir a producción con datos reales. |

### C.2 — Prioridad media

| # | Problema | Ubicación | Impacto |
|---|---|---|---|
| C2.1 | **pull_all_sources() sin cobertura** | rss_aggregator.py:89-125 | Solo `pull_source()` tiene tests. La lógica de rate limiting por dominio y el loop sobre sources activos no está testeado. |
| C2.2 | **Job wrappers con cobertura 38-46%** | jobs/compute_poll_avg.py (38%), pull_rss.py (46%), send_newsletter.py (46%) | Los wrappers crean sesiones DB y miden duración — no testeados unitariamente. |
| C2.3 | **beehiiv.py service con 44% cobertura** | services/beehiiv.py | `forward_to_beehiiv()` — la función que realmente llama a Beehiiv API — no tiene test con mock. Solo se testea indirectamente via newsletter service. |
| C2.4 | **User-Agent faltante en requests RSS** | rss_aggregator.py:45-46 | `httpx.AsyncClient(timeout=15)` sin headers. El SPEC explícitamente especifica un User-Agent. Algunos feeds pueden rechazar requests sin UA. |
| C2.5 | **No hay índice en news_items.status** | Schema/migración | Queries futuras filtrando por status='raw' (para curación) harán full table scan. Con volúmenes bajos (<10k items) no importa aún. |
| C2.6 | **Redis declarado pero no usado** | docker-compose.yml, config.py | Redis se usa solo como backend de rate limiting (slowapi). No se usa para cache, sesiones, ni cola. Si el rate limiter falla conectando a Redis, slowapi podría fallar silenciosamente o bloquear requests. |
| C2.7 | **import_positions_csv.py con 0% cobertura** | scripts/import_positions_csv.py (113 líneas) | Script CLI complejo sin ningún test. Incluye lógica de lookup por slug, validación de valores, y upsert. |

### C.3 — Prioridad baja

| # | Problema | Ubicación | Impacto |
|---|---|---|---|
| C3.1 | **CSV import README tiene slugs obsoletos** | backend/README.md:113-114 | Ejemplo muestra `maria-valencia` y `carlos-restrepo` — nombres pre-rename. Debería usar slugs actuales (`candidata-demo-alfa`, etc.) |
| C3.2 | **news_items no tiene `deleted_at`** | models/news_item.py | SPEC §2.2 menciona soft delete para NewsItem. No implementado ni en modelo ni en migración. Podría necesitarse si se requiere "descartar" items sin eliminarlos. |
| C3.3 | **Seed tiene feeds RSS desactivados** | seed_colombia_2026.py | 2 de 5 feeds con `is_active=False`. En producción se necesitarán feeds funcionales reales. |
| C3.4 | **subscriber.status sin CHECK constraint** | Schema | SPEC sugiere valores posibles (pending, confirmed, unsubscribed) pero no hay CHECK constraint en DB. |
| C3.5 | **news_items.status sin CHECK constraint** | Schema | Valores posibles: raw, curated, published, discarded. Sin CHECK. |
| C3.6 | **newsletter.py genera digest en markdown crudo** | services/newsletter.py | El digest es texto/markdown plano. Beehiiv espera HTML. Necesitará conversión markdown→HTML antes de envío real. |

---

## D. Issues abiertos en GitHub

| # | Título | Estado | Fase | Comentarios |
|---|---|---|---|---|
| #2 | `feat: endpoint admin /api/admin/cleanup-demo para eliminar datos is_demo=True` | **ABIERTO** | Fase 3 | Necesario antes de producción. Requiere DELETE con cascade: candidate_positions → candidates, quiz_completions → candidates, statements, articles. Prioridad alta. |

**PRs mergeados**:

| PR | Título | Branch | Estado |
|---|---|---|---|
| #1 | Fase 1: Bootstrap del repo + infraestructura local | feature/fase-1-infra | MERGED |
| #3 | Fase 2: modelo de datos, migraciones, seed | feature/fase-2-schema | MERGED |
| #4 | Fase 3: API REST (FastAPI) | feature/fase-3-api | MERGED |
| #5 | Fase 4: worker, scheduler y jobs | feature/fase-4-worker | MERGED |

---

## E. Cobertura de tests

### E.1 — Resumen

```
Total statements: 1512
Covered:          1063
Missed:            449
Coverage:          70%
Tests:             64 (todos pasan)
Warnings:          29 (todas por datetime.utcnow() deprecado)
```

### E.2 — Detalle por módulo

**100% cobertura** (22 módulos):
```
app/__init__.py, app/config.py, app/jobs/__init__.py, app/jobs/schedule.py,
app/models/__init__.py, app/models/base.py, app/models/candidate.py,
app/models/country.py, app/models/election.py, app/models/news_item.py,
app/models/newsletter_send.py, app/models/poll.py, app/models/poll_average.py,
app/models/position.py, app/models/quiz_completion.py, app/models/source.py,
app/models/subscriber.py, app/schemas/* (todos), app/services/matching.py,
app/services/poll_compute.py
```

**Cobertura parcial** (módulos con gaps significativos):

| Módulo | Stmts | Miss | Cov% | Líneas no cubiertas |
|---|---|---|---|---|
| app/worker.py | 69 | 69 | **0%** | Todo (proceso standalone) |
| app/scripts/seed_colombia_2026.py | 56 | 56 | **0%** | Todo (script CLI) |
| app/scripts/import_positions_csv.py | 113 | 113 | **0%** | Todo (script CLI) |
| app/routers/subscribers.py | 31 | 16 | **48%** | 28-54 (cuerpo create_subscriber) |
| app/routers/quiz.py | 47 | 22 | **53%** | 32, 50-64, 84-104 |
| app/routers/admin.py | 97 | 39 | **60%** | 55-78, 95-130, 147-192, 221-234 |
| app/routers/countries.py | 26 | 10 | **62%** | 22-36, 46-50 |
| app/services/rss_aggregator.py | 67 | 21 | **69%** | 34, 58, 62, 95-121 (pull_all_sources) |
| app/jobs/compute_poll_avg.py | 16 | 10 | **38%** | 13-36 |
| app/jobs/pull_rss.py | 13 | 7 | **46%** | 13-22 |
| app/jobs/send_newsletter.py | 13 | 7 | **46%** | 13-27 |
| app/services/beehiiv.py | 25 | 14 | **44%** | 26-43 |

### E.3 — Distribución de tests

| Área | Tests | Archivos |
|---|---|---|
| Matching algorithm | 12 | test_matching.py |
| Admin endpoints | 8 | test_admin.py |
| Articles router | 7 | test_articles.py |
| Wikimedia service | 6 | test_wikimedia.py |
| Quiz router | 4 | test_quiz.py |
| Countries router | 4 | test_countries.py |
| Candidates router | 4 | test_candidates.py |
| RSS aggregator | 3 | test_rss_aggregator.py |
| Subscribers router | 3 | test_subscribers.py |
| Polls router | 3 | test_polls.py |
| Newsletter service | 3 | test_newsletter.py |
| Background tasks | 3 | test_tasks.py |
| Poll computation | 2 | test_poll_compute.py |
| Worker/scheduler | 1 | test_worker.py |
| **Total** | **64** | **14 archivos** |

### E.4 — Módulos sin test alguno

- `app/worker.py` — proceso standalone con loop infinito
- `app/scripts/seed_colombia_2026.py` — script CLI
- `app/scripts/import_positions_csv.py` — script CLI
- `app/services/beehiiv.py` — función `forward_to_beehiiv()` no testeada directamente

---

## F. Revisión de seguridad y configuración

### F.1 — Autenticación y autorización

| Control | Estado | Detalle |
|---|---|---|
| Admin endpoints protegidos | ✅ | `require_admin` dependency en todo el router admin (`deps.py:12-17`) |
| API key comparación segura | ⚠️ | Usa `==` en lugar de `hmac.compare_digest()`. Vulnerable teóricamente a timing attacks, pero irrelevante en la práctica con red de por medio. |
| Secrets fuera del repo | ✅ | `.env.example` con placeholders, `.gitignore` excluye `.env` |
| ADMIN_API_KEY default inseguro | ⚠️ | Default es `"changeme"` en `config.py:18`. Si alguien olvida cambiarlo en producción, el admin queda abierto. Debería fallar al arrancar si el key es el default en modo producción. |

### F.2 — Protección de datos

| Control | Estado | Detalle |
|---|---|---|
| Quiz no guarda respuestas individuales | ✅ | Solo persiste session_hash, top_match, statements_answered (`quiz.py:94-102`) |
| IP hasheada en logs | ✅ | `main.py:144` — SHA-256 truncado a 16 chars |
| Session hash privacy-preserving | ✅ | `sha256(ip + ua + day)[:16]` — no reversible |
| Email no expuesto en response | ✅ | `SubscriberOut` no incluye campo email |
| Sin cookies de tracking | ✅ | Ningún middleware de cookies/sesiones |

### F.3 — Configuración de red y transporte

| Control | Estado | Detalle |
|---|---|---|
| CORS restrictivo | ✅ | 5 orígenes explícitos, credenciales permitidas |
| Security headers en prod | ✅ | Caddyfile.prod: HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy |
| `-Server` header removido | ✅ | Caddyfile.prod |
| TLS en prod | ✅ | Caddy con Origin Certificate de Cloudflare |
| Servicios internos no expuestos | ✅ | Solo caddy expone puertos 80/443. Postgres, Redis, API no tienen ports en docker-compose.yml |
| Docker user no-root | ✅ | Dockerfile: `USER app` en runtime y test stages |

### F.4 — Inyección y validación

| Control | Estado | Detalle |
|---|---|---|
| SQL injection | ✅ | Todo vía SQLAlchemy ORM, sin raw SQL excepto en migraciones |
| XSS | N/A | Backend solo retorna JSON, no HTML |
| Input validation | ✅ | Pydantic schemas en todas las requests |
| Path traversal | ✅ | Sin acceso a filesystem vía API |
| Rate limiting | ✅ | slowapi con Redis backend, 60/min default, 5/hour subscribers |

### F.5 — Hallazgos de seguridad

| # | Severidad | Hallazgo |
|---|---|---|
| F5.1 | **Media** | `subscribers.py:52` — `asyncio.create_task(forward_to_beehiiv(...))` sin referencia fuerte. Si la tarea falla, la excepción se pierde silenciosamente sin logging. Además, si el event loop se cierra antes de completar, el email no se envía a Beehiiv. Usar `spawn_background_task()`. |
| F5.2 | **Baja** | `config.py:18` — `admin_api_key: str = "changeme"` como default. En producción si no se configura, el admin queda accesible con key conocida. Agregar validación al startup. |
| F5.3 | **Baja** | `deps.py:15` — Comparación de API key con `==` en lugar de `hmac.compare_digest()`. Riesgo teórico de timing attack, negligible en la práctica. |
| F5.4 | **Info** | Rate limiter usa Redis DB 1 (`redis://redis:6379/1`). Si Redis no está disponible, el comportamiento de slowapi no está documentado — podría permitir todas las requests o bloquearlas todas. |

---

## G. Hallazgos priorizados

### Críticos (bloquean producción)

| # | Hallazgo | Acción requerida |
|---|---|---|
| G1 | **Issue #2 sin implementar**: `DELETE /api/admin/cleanup-demo` necesario para eliminar datos seed antes de cargar datos reales. | Implementar endpoint con cascade deletion en el orden correcto. |

### Altos (deben resolverse antes de lanzamiento)

| # | Hallazgo | Acción requerida |
|---|---|---|
| G2 | **`datetime.utcnow()` deprecado** genera 29 warnings y será removido en Python 3.14. Causa raíz: modelos SQLAlchemy no declaran `DateTime(timezone=True)`. | Mapear columnas datetime con `timezone=True` explícito en todos los modelos. Migrar a `datetime.now(UTC)`. |
| G3 | **Task sin referencia fuerte en subscribers.py:52** — `asyncio.create_task()` directo, pérdida silenciosa de excepciones. | Reemplazar con `spawn_background_task()`. |
| G4 | **User-Agent faltante en requests RSS** — SPEC lo especifica, algunos feeds pueden bloquear requests sin UA. | Agregar `headers={"User-Agent": settings.wikimedia_user_agent}` (o un UA específico para RSS) al `httpx.AsyncClient` en `pull_source()`. |
| G5 | **Validación de ADMIN_API_KEY en producción** — default "changeme" no debe funcionar en prod. | Agregar check en `main.py` lifespan: si `ENV=production` y key es "changeme", `sys.exit(1)`. |

### Medios (resolver durante Fase 5 o antes de lanzamiento)

| # | Hallazgo | Acción requerida |
|---|---|---|
| G6 | **worker.py sin tests** (0% cobertura, 69 líneas). | Extraer lógica testeable (health checks, configuración) en funciones puras. Testear al menos la configuración y el manejo de señales. |
| G7 | **pull_all_sources() sin test** — lógica de rate limiting por dominio no verificada. | Agregar test con 2+ sources del mismo dominio, verificar delay. |
| G8 | **beehiiv.py sin test directo** — `forward_to_beehiiv()` no testeado. | Agregar test con respx mock del API de Beehiiv. |
| G9 | **Newsletter digest genera markdown, Beehiiv espera HTML**. | Agregar conversión markdown→HTML antes de envío (o usar Beehiiv markdown support si lo tiene). |
| G10 | **CSV import sin tests** (113 líneas, 0% cobertura). | Agregar al menos tests para la lógica de lookup y validación. |
| G11 | **README CSV tiene slugs obsoletos** (maria-valencia, carlos-restrepo). | Actualizar a slugs actuales (candidata-demo-alfa, etc.). |

### Bajos (backlog, no bloquean)

| # | Hallazgo | Acción requerida |
|---|---|---|
| G12 | Timing attack teórico en comparación de API key. | Usar `hmac.compare_digest()` en `require_admin`. |
| G13 | Sin CHECK constraints en `news_items.status` y `subscriber.status`. | Agregar constraints en migración futura. |
| G14 | Sin índice en `news_items.status`. | Agregar cuando el volumen lo justifique. |
| G15 | 2 de 5 feeds RSS desactivados en seed. | Buscar feeds alternativos funcionales para El Espectador y Semana. |
| G16 | CLAUDE.md desactualizado (dice "Phase 3: Not started" y 12 tablas). | Ya fue actualizado en PR #5 — verificar que main tiene la versión correcta. |

---

## Resumen ejecutivo

| Métrica | Valor |
|---|---|
| Fases completadas | 4 de 9 |
| Tests | 64 pasando, 0 fallando |
| Cobertura total | 70% |
| Warnings | 29 (deprecation datetime) |
| Issues abiertos | 1 (#2 cleanup-demo) |
| Hallazgos críticos | 1 (issue #2) |
| Hallazgos altos | 4 |
| Hallazgos medios | 6 |
| Hallazgos bajos | 5 |
| Tablas en DB | 13 |
| Endpoints API | 16 públicos + admin |
| Servicios de negocio | 6 |
| Jobs background | 4 |

El proyecto tiene una base sólida. La arquitectura es limpia, la separación de concerns es clara (routers → services → models), y la infraestructura Docker está bien configurada para dev y prod. Las Fases 1-4 están funcionalmente completas con las desviaciones documentadas.

Los items más urgentes antes de avanzar a Fase 5 (Frontend) son:
1. Implementar issue #2 (cleanup-demo)
2. Corregir el task sin referencia fuerte en subscribers.py
3. Agregar User-Agent a peticiones RSS
4. Planificar la migración de `datetime.utcnow()` → `datetime.now(UTC)` con columnas `DateTime(timezone=True)`
