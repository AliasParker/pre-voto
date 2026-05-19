# LAUNCH_BRIEF.md — pre.voto Colombia 2026

> **Este documento es la fuente de verdad sobre las decisiones de producto, contenido y operación del lanzamiento de pre.voto. Si una decisión está acá, está tomada. Si no está acá y es necesaria, preguntá al humano antes de avanzar.**

---

## Changelog

- **v1.1 — 19 mayo 2026**: actualización de porcentajes de confianza por candidato con datos reales del archivo `positions.json` validado. Reemplaza el 80%/13% original por 52%/14% promedio, con rango por candidato. Ajustes asociados en artículos 2, 3 y 5, en hilo de redes, y en pitch a periodistas (los cambios editoriales están documentados aparte, este brief solo refleja los datos correctos).
- **v1.0 — 18 mayo 2026**: versión inicial.

---

## TL;DR para el asistente que abre este archivo

Hola, Claude. Estás abriendo Claude Code para terminar la implementación técnica del lanzamiento de pre.voto en Colombia. Antes de hacer cualquier cosa:

1. **Leé este documento completo.** Tiene todas las decisiones ya tomadas, los datos a importar y las tareas pendientes en orden.
2. **No reescribas el contenido editorial.** Los 5 artículos, los 20 statements, las 240 codificaciones, los 3 emails de Beehiiv y los copys de redes están **validados por el humano**. Cualquier ajuste textual menor lo proponés y esperás confirmación.
3. **El repo es `Work-Space-Pre-Voto`.** No conocés su estructura interna. Explorala con `view` y `bash` antes de tocar archivos. La arquitectura general está descrita más abajo en la sección "Estado del proyecto", pero confirmá contra el código real.
4. **Hay restricciones legales reales (Ley 2494/2025).** No las relajes ni las simplifiques. Si tenés dudas, ver la sección "Restricciones legales".
5. **El humano se mueve entre Claude Code (vos) y el chat web** para decisiones de producto, redacción y planificación. Si te pide algo que parece estratégico más que técnico, sugerí gentilmente que lo discuta en el chat web y volvé acá con la decisión tomada.
6. **Tiempos**: hoy es 19 de mayo de 2026. Lanzamiento soft: 25-26 de mayo. Primera vuelta: 31 de mayo. Cuenta del humano expira el 26 de mayo. Trabajá con esa urgencia en mente.

---

## Contexto del proyecto

**Pre.voto** es una brújula electoral (*Voting Advice Application*) pan-LATAM que compara las posiciones del usuario con las de los candidatos en elecciones presidenciales. Colombia 2026 es el primer país. Después vienen Brasil (oct 2026), México (2027) y Argentina (2027).

- **Dominio**: pre.voto (premium .voto TLD)
- **Producción en vivo**: https://pre.voto (TLS funcionando, deployado en Hetzner CPX22 Falkenstein)
- **Infraestructura**: Cloudflare (DNS + TLS Origin + WAF + cache), backups diarios a R2, UptimeRobot
- **Repo**: `github.com/AliasParker/Work-Space-Pre-Voto` (privado)
- **Stack**: Backend Python + PostgreSQL + Alembic + Docker. Frontend Astro + Svelte + Tailwind, i18n ES + PT.
- **Email**: hola@pre.voto (consultas), errores@pre.voto (correcciones)
- **Firma editorial**: "Equipo pre.voto" (el humano no quiere exponer su nombre individual por ahora)
- **Newsletter**: Beehiiv, publication "pre.voto", plan Launch gratis

**Lo que pre.voto NO es**:
- No es una encuesta (no mide intención de voto)
- No es un medio (no tiene redacción)
- No es un partido (no recomienda voto)
- No es un negocio (no monetiza)

---

## Estado del proyecto

### Fases 1-7: COMPLETADAS

- ✅ Backend Python + Postgres + Alembic + Docker
- ✅ 64+ tests pasando
- ✅ Frontend Astro + Svelte + Tailwind con i18n ES + PT
- ✅ OG cards dinámicas (por resultado de quiz, por artículo)
- ✅ Deploy a producción (Hetzner + Cloudflare + R2 backups)
- ✅ Cuenta Beehiiv creada con publication "pre.voto"
- ✅ PR #9 mergeado

### Fase 8: EN CURSO (lo que falta)

- ❌ Import a DB de producción de los 12 candidatos + 20 statements + 240 codificaciones + 5 artículos
- ❌ Disclaimers Ley 2494 en `/co/quiz`, `/co/resultados/*`, y footer global
- ❌ Feature flag `quiz_disabled_during_veda` (backend + frontend)
- ❌ Integración Beehiiv: trigger desde backend post-quiz → API Beehiiv con custom fields y automation_id
- ❌ Visualización en frontend del % de citas directas vs inferidas por candidato (`high_confidence_pct`)
- ❌ Doble métrica de afinidad: con todas las posiciones / solo con confianza alta
- ❌ QA end-to-end del flujo completo
- ❌ Deploy final + smoke test post-deploy

---

## Decisiones de producto vigentes

Estas decisiones están tomadas. No las cuestiones, implementálas.

### Sobre los candidatos

- **12 candidatos en contienda activa** (no 13). Clara López (casilla 2) y Luis Gilberto Murillo (casilla 14) renunciaron para sumarse a Cepeda. Sus casillas quedan en el tarjetón pero pre.voto no las incluye en el quiz.
- En la página del quiz, una nota visible al inicio aclara: "Dos candidatos del tarjetón (Clara López y Luis Gilberto Murillo) renunciaron y sus votos no se cuentan a su nombre. Pre.voto no los incluye en el quiz."

### Sobre el nivel de evidencia documental por candidato

**Esta es información actualizada de v1.1. Los porcentajes reflejan el archivo `positions.json` validado.**

Los porcentajes de codificaciones con **cita directa** (confianza alta) varían mucho por candidato:

| Candidato | % codificaciones high | Notas |
|-----------|----------------------|-------|
| Cepeda | 85% | Plan oficial extenso + trayectoria documentada |
| De la Espriella | 80% | Plan oficial + cuenta oficial activa |
| Valencia | 70% | Plan 10 + entrevistas verificables |
| López Hernández | 45% | Trayectoria documentada, plan más general |
| Fajardo | 30% | Posiciones mayormente inferidas de entrevistas, plan menos específico tema por tema |
| Botero | 30% | Plan oficial corto pero específico en banderas |
| Lizcano | 20% | Plan oficial técnico, poca información sobre ejes social/exterior |
| Uribe Londoño | 15% | Recién relanzó candidatura, plan parcial |
| Caicedo | 15% | Plataforma regional, poca info sobre ejes nacionales |
| Matamoros | 10% | Eje seguridad documentado, resto inferido |
| Barreras | 10% | Plan oficial pero con foco en propuestas tech, poca claridad en ejes sociales |
| Macollins | 0% | Campaña centrada en una bandera (reestructuración territorial); sin posiciones públicas sobre los demás temas |

- **Promedio del top 5**: **52%** de codificaciones con cita directa.
- **Promedio del bottom 7**: **14%** de codificaciones con cita directa.
- **Promedio general (12 candidatos)**: 34% high, 25% medium, 41% low.

Estos porcentajes son visibles para el usuario en cada ficha individual y en cada tarjeta de resultado del ranking. El campo `high_confidence_pct` de `candidates.json` contiene el valor exacto por candidato.

### Sobre el cálculo de afinidad

- **Promedio ponderado simple**: cada uno de los 20 statements pesa lo mismo (1/20).
- **Comparación posición a posición**:
  - Coincidencia exacta (mismo valor): 100%
  - Diferencia de 1 nivel (ej. ++ vs +): 75%
  - Diferencia de 2 niveles (ej. ++ vs 0): 50%
  - Diferencia de 3 niveles (ej. ++ vs -): 25%
  - Diferencia de 4 niveles (ej. ++ vs --): 0%
- **Doble métrica visible al usuario**:
  - Afinidad con TODAS las posiciones del candidato
  - Afinidad SOLO con las posiciones de confianza alta (cita directa)
- Las posiciones marcadas como "Neutral" del USUARIO se excluyen del cálculo (no contribuyen). Las "Neutral" del CANDIDATO sí se incluyen.

### Sobre la presentación de resultados

- **Ranking de 12 candidatos** ordenado por afinidad descendente.
- Cada tarjeta de resultado muestra:
  - Foto del candidato
  - Nombre + fórmula vicepresidencial
  - % de afinidad (con todas las posiciones)
  - % de afinidad (solo con confianza alta) en menor tamaño
  - Indicador de "% de codificaciones con cita directa" (badge) que sale del campo `high_confidence_pct`
  - Link a la ficha completa del candidato
- **Las posiciones donde diferís** se muestran en una segunda sección, no en la primera. La primera sección es el ranking.

### Sobre las fichas de candidatos

Cada ficha individual (`/co/candidatos/:slug`) muestra:
- Bio corta + foto + fórmula VP
- Coalición/partido
- Posicionamiento (etiqueta descriptiva, no evaluativa — ver glosario)
- Encabezado con: "20 posiciones codificadas. X con cita directa (X% del total), Y con inferencia coherente, Z con inferencia sin cita." Usar `high_confidence_pct` para el cálculo de X.
- Tabla de las 20 posiciones con: statement, posición codificada, nivel de confianza (alta/media/baja con código de color), fuente (cita textual cuando hay, link cuando hay)
- Para candidatos con **menos del 30% de codificaciones high** (Fajardo, Botero, Lizcano, Uribe Londoño, Macollins, Barreras, Caicedo, Matamoros): aviso destacado al inicio de la ficha:
  > Este candidato ha tomado posición pública sobre menos de un tercio de los temas del quiz. La mayoría de las codificaciones son inferencias basadas en su trayectoria y coalición. Para una decisión informada, consulte directamente su plan de gobierno y sus declaraciones públicas.
- Para Macollins específicamente (0% high), el aviso es más fuerte:
  > Sondra Macollins no tiene posiciones públicas registradas sobre 18 de los 20 temas del quiz. Las codificaciones que ves abajo son inferencias coherentes con su línea declarada, pero no constituyen declaraciones directas de la candidata. Su campaña se ha centrado en su propuesta de reestructuración territorial. Para conocer su posición específica sobre cualquier tema del quiz, te recomendamos consultar fuentes oficiales.
- Para Clara López y Murillo (retirados): la ficha existe pero muestra solo el aviso de retiro, no tiene posiciones codificadas.

### Sobre el footer global

Texto fijo del footer:
> Pre.voto es una iniciativa independiente, sin afiliación partidaria, sin pauta comercial y sin contenido patrocinado. Para consultas: hola@pre.voto. Para corregir errores: errores@pre.voto.

Adicional en el footer de páginas del quiz:
> Pre.voto NO es una encuesta de opinión electoral en el sentido de la Ley 2494 de 2025. Es una herramienta pedagógica individual.

### Sobre las URLs

- `/` → landing pan-LATAM
- `/co` → landing Colombia (selector de país)
- `/co/quiz` → quiz
- `/co/resultados/:token` → página de resultados (token único por usuario)
- `/co/candidatos/:slug` → ficha individual de candidato
- `/co/blog/:slug` → artículos
- `/metodologia` → metodología general (no por país)
- `/equipo` → "Equipo pre.voto" + valores + qué NO somos

### Sobre la firma de los artículos

Todos firmados por **"Equipo pre.voto"**. Nunca por nombre individual.

---

## Datos a importar

Los 3 archivos JSON validados están en mano del humano y se entregan a Claude Code en el momento del import:

- `statements.json` — 20 statements con eje, slug, texto y label corto
- `candidates.json` — 12 candidatos activos + 2 retirados con metadata (incluye `high_confidence_pct` por candidato)
- `positions.json` — 240 codificaciones con posición, confianza, fuente y cita textual

### Validaciones que se aplicaron al JSON antes de pasarlo

- 240 codificaciones exactas (12 candidatos × 20 statements)
- Sin duplicados (cada par candidato+statement aparece una sola vez)
- Todos los statement_ids van del 1 al 20
- Cada candidato activo tiene exactamente 20 posiciones
- Los 2 retirados (Clara López, Murillo) no tienen posiciones codificadas

### Estructura del schema de DB (referencia)

- Tabla `statements`: id, slug, axis, text, short_label
- Tabla `candidates`: id, ballot_position, slug, full_name, running_mate, coalition, age, positioning, bio_short, withdrawn (bool), withdrawn_date, endorses (FK opcional a otro candidato), plan_url, high_confidence_pct
- Tabla `candidate_positions`: candidate_id (FK), statement_id (FK), position (enum), confidence (enum), source_quote (text nullable), source_url (text nullable), source_type (enum: plan_oficial, entrevista, cuenta_oficial, trayectoria, inferencia), notes (text nullable)

### Los 5 artículos

Todos firmados por "Equipo pre.voto". Slugs y fechas de publicación:

| Slug | Título | Fecha publicación |
|------|--------|-------------------|
| `metodologia` | Cómo construimos pre.voto: la metodología detrás del quiz | 23 mayo 2026 |
| `comparativo-cinco-candidatos` | Cepeda, De la Espriella, Valencia, Fajardo y López: los cinco candidatos que se reparten el 90% del voto | 24 mayo 2026 |
| `otros-siete-candidatos` | Más allá del top-5: los siete candidatos que también están en el tarjetón del 31 de mayo | 25 mayo 2026 |
| `como-se-vota` | Cómo se vota el 31 de mayo: guía rápida del sistema electoral colombiano | 26 mayo 2026 |
| `lanzamiento` | Por qué construimos pre.voto: una brújula electoral pan-LATAM, sin medio detrás | 27 mayo 2026 |

Los textos completos los tiene el humano en el chat web. **Importante para Claude Code**: en v1.1 hubo ajustes editoriales en los artículos 3 y 5 (y en notas internas del 2) para reflejar los porcentajes reales de confianza. El humano va a pasar las versiones definitivas como archivos `.md` o `.mdx` para que las importes a `src/content/blog/`. No re-redactes los artículos vos.

---

## Tareas pendientes (en orden de prioridad)

### Tarea 1 — Import a DB de candidatos, statements y codificaciones (CRÍTICO)

**Criterios de aceptación**:
- Tabla `candidates` con los 12 candidatos en contienda + 2 retirados (flag `withdrawn=true`)
- Tabla `statements` con los 20 statements
- Tabla `candidate_positions` con 240 codificaciones (12 candidatos × 20 statements)
- Los retirados NO tienen registros en `candidate_positions`
- Tests del backend (que ya existen, 64+) siguen pasando después del import
- Migración Alembic reversible

**Pasos sugeridos**:
1. Verificar el schema actual con `bash` (psql, ver tablas existentes)
2. Pedir al humano los 3 archivos JSON (`statements.json`, `candidates.json`, `positions.json`)
3. Generar migration Alembic con seed data (o script `scripts/seed_co_2026.py` que ejecute el seed por separado de las migrations)
4. Aplicar a staging primero, después a producción
5. Validar con queries SQL que el import fue completo: contar registros, verificar que cada candidato activo tenga 20 posiciones, verificar que ningún `candidate_position` apunte a un retirado

### Tarea 2 — Import a CMS/blog de los 5 artículos (CRÍTICO)

**Criterios de aceptación**:
- Cada artículo en MDX o markdown según la convención del proyecto (Astro suele usar `.md` o `.mdx` en `src/content/blog/`)
- Frontmatter con: title, slug, publication_date, author ("Equipo pre.voto"), description (preview de 160 chars), country (CO)
- Renderizan en `/co/blog/:slug`
- OG cards funcionan (ya implementadas en Fase 7, solo verificar que toman el frontmatter correcto)

**Importante**: pedir los textos al humano en el chat web. No inventes el contenido. Los textos definitivos incorporan los ajustes editoriales de v1.1.

### Tarea 3 — Disclaimers Ley 2494 (CRÍTICO LEGAL)

**Criterios de aceptación**:
- **Footer global** (todas las páginas): texto fijo de pre.voto (ver "Decisiones de producto")
- **Footer de `/co/quiz`, `/co/resultados/*`, `/co/candidatos/*`**: adicional sobre Ley 2494
- **Aviso destacado** al inicio de `/co/quiz` antes del primer statement:
  > Pre.voto es una herramienta pedagógica individual. No es una encuesta de opinión electoral. Tu resultado es para tu uso personal y no se agrega ni se publica como estadística colectiva.
- Aviso destacado en `/co/resultados/:token`:
  > Este resultado representa tu coincidencia con las posiciones declaradas o inferidas de cada candidato. No es una recomendación de voto. La decisión final es tuya.

### Tarea 4 — Feature flag `quiz_disabled_during_veda`

**Criterios de aceptación**:
- Backend: feature flag controlable por variable de entorno o tabla `feature_flags`
- Activación programada automática:
  - **Inicio**: 31 mayo 2026 00:00 hora Bogotá (UTC-5)
  - **Fin**: 31 mayo 2026 16:00 hora Bogotá
  - Si hay 2da vuelta: **Inicio**: 21 junio 2026 00:00 — **Fin**: 21 junio 2026 16:00
- Cuando está activa:
  - `GET /co/quiz` redirige a `/co/veda` (página estática con mensaje)
  - `POST /api/quiz/submit` retorna 423 (Locked) con mensaje JSON
- Página `/co/veda`:
  > Hoy es día de elección en Colombia. El quiz de pre.voto está pausado por respeto a la veda electoral. Volvé después de las 4 PM hora Bogotá, cuando cierren las mesas. Andá a votar.
- Tests: agregar test que verifique que el flag funciona

### Tarea 5 — Visualización de doble métrica de afinidad y badges de confianza

**Criterios de aceptación**:
- En cada tarjeta de resultado en `/co/resultados/:token`:
  - Número grande: afinidad con TODAS las posiciones (ej: "78%")
  - Número pequeño debajo: "afinidad con posiciones de cita directa: 82%"
  - Badge con tooltip: "85% de las codificaciones de este candidato tiene cita directa" (usar `high_confidence_pct`)
- En la ficha del candidato `/co/candidatos/:slug`:
  - Encabezado declara: "20 posiciones codificadas. X con cita directa (X% del total)."
- Aviso destacado para candidatos con `high_confidence_pct < 30` (Fajardo, Botero, Lizcano, Uribe Londoño, Macollins, Barreras, Caicedo, Matamoros)
- Aviso especialmente fuerte para Macollins (`high_confidence_pct == 0`)

### Tarea 6 — Integración Beehiiv (post-quiz)

**Criterios de aceptación**:
- Endpoint POST `https://api.beehiiv.com/v2/publications/{pub_id}/subscriptions`
- Body:
  ```json
  {
    "email": "user@example.com",
    "reactivate_existing": true,
    "send_welcome_email": false,
    "utm_source": "prevoto_quiz",
    "utm_medium": "post_quiz_subscription",
    "utm_campaign": "co_2026_first_round",
    "custom_fields": [
      {"name": "top_match_name", "value": "Iván Cepeda"},
      {"name": "top_match_pct", "value": 78},
      {"name": "result_url", "value": "https://pre.voto/co/resultados/abc123"},
      {"name": "country", "value": "CO"}
    ],
    "automation_ids": ["${BEEHIIV_AUTOMATION_ID_CO}"]
  }
  ```
- Variables de entorno requeridas:
  - `BEEHIIV_API_KEY` (secret)
  - `BEEHIIV_PUBLICATION_ID` (el humano lo va a pasar, formato `pub_xxx`)
  - `BEEHIIV_AUTOMATION_ID_CO` (se obtiene después de crear la automation en Beehiiv UI)
- Trigger: cuando el usuario completa el quiz Y opta por suscribirse (checkbox post-resultados).
- Manejo de errores: si Beehiiv falla, log a stderr/Sentry pero NO bloquear el flujo del quiz. El usuario debe ver sus resultados aunque la suscripción falle.
- Idempotencia: usar `reactivate_existing: true` y los custom fields se sobreescriben en cada submit (Beehiiv lo maneja nativamente).
- **No subscribir automáticamente**. El usuario debe tildar explícitamente el checkbox "Quiero recibir el contexto y el recordatorio de votación por email".
- Tests: mockear el endpoint de Beehiiv y verificar el body correcto.

**Importante sobre el automation en Beehiiv**: el humano todavía no creó la automation en Beehiiv UI. Necesita:
1. Crear los 4 custom fields (`top_match_name`, `top_match_pct`, `result_url`, `country`)
2. Crear la automation con trigger "Subscriber added by API" y filter `country = "CO"`
3. Subir los 3 textos de email (los tiene del chat web)
4. Activar la automation y copiar el `automation_id`
5. Setear `BEEHIIV_AUTOMATION_ID_CO` en producción

Hasta que la automation esté creada, no se puede testear end-to-end. Pero el código puede estar listo apuntando a placeholder.

### Tarea 7 — QA end-to-end

**Criterios de aceptación**:
- Hacer el quiz desde cero como usuario nuevo. Validar:
  - [ ] Los 20 statements aparecen en orden y se pueden responder
  - [ ] El resultado se genera correctamente
  - [ ] El ranking de 12 candidatos está completo
  - [ ] Los 2 retirados NO aparecen en el ranking
  - [ ] Las dos métricas de afinidad se muestran correctamente
  - [ ] Los badges de "% citas directas" se muestran y coinciden con `high_confidence_pct` por candidato
  - [ ] El aviso especial para Macollins se muestra en su ficha
  - [ ] El aviso para candidatos con <30% high se muestra correctamente
  - [ ] El link a cada ficha funciona
  - [ ] Los 5 artículos renderean
  - [ ] OG cards de cada artículo y de cada resultado pasan Twitter Card Validator
  - [ ] Disclaimers Ley 2494 visibles en footer y página de quiz
  - [ ] Aviso de candidatos retirados visible en el quiz
  - [ ] Si subscribe checkbox tildado, el suscriptor llega a Beehiiv con custom fields correctos
  - [ ] Si subscribe checkbox no tildado, no llega nada
- Probar el feature flag de veda manualmente:
  - Activar flag → ver `/co/veda`, no poder hacer quiz
  - Desactivar flag → todo vuelve a funcionar
- Probar en móvil (responsive)
- Verificar performance (Lighthouse): >80 en mobile

### Tarea 8 — Deploy final + smoke test

**Criterios de aceptación**:
- Backup pre-deploy de la DB de producción
- Push a `main` → CI/CD a producción Hetzner
- Smoke test post-deploy:
  - [ ] Homepage carga
  - [ ] `/co` carga
  - [ ] `/co/quiz` funciona
  - [ ] Crear un quiz completo desde un browser real
  - [ ] Recibir el email de Beehiiv (a una cuenta de test)
- Notificar al humano cuando esté listo para anuncio público

---

## Configuración crítica

### Variables de entorno (`.env` en producción)

Las que ya existen (no tocar):
- `DATABASE_URL`
- `SECRET_KEY`
- `CORS_ALLOWED_ORIGINS`
- `R2_*` (backups)

Nuevas que hay que agregar:
- `BEEHIIV_API_KEY` (secret, el humano la va a pasar)
- `BEEHIIV_PUBLICATION_ID` (formato `pub_xxx`)
- `BEEHIIV_AUTOMATION_ID_CO` (se obtiene después de crear automation)
- `QUIZ_VEDA_START_CO` (ISO datetime, default `2026-05-31T00:00:00-05:00`)
- `QUIZ_VEDA_END_CO` (ISO datetime, default `2026-05-31T16:00:00-05:00`)
- `QUIZ_VEDA_START_CO_2DA` (ISO datetime, default `2026-06-21T00:00:00-05:00`, solo si aplica)
- `QUIZ_VEDA_END_CO_2DA` (ISO datetime, default `2026-06-21T16:00:00-05:00`, solo si aplica)

### Feature flags

Hay (o debería haber) una tabla `feature_flags` con `key`, `value`, `enabled`, `country_scope`. Si no existe, crearla.

Flags a usar:
- `quiz_disabled_during_veda` (boolean, country-scoped `CO`)
- `show_dual_affinity_metric` (boolean, global) — para el feature de doble afinidad
- `beehiiv_subscriptions_enabled` (boolean, country-scoped `CO`) — kill switch si Beehiiv falla

---

## Restricciones legales

### Ley 2494 de 2025 (Colombia)

Esta ley regula encuestas, sondeos y herramientas digitales que pretenden medir opinión electoral.

**Lo que pre.voto puede hacer**:
- Mostrar al usuario individual su propio resultado (afinidad con cada candidato)
- Publicar las codificaciones de los candidatos con fuente citada
- Enviar al usuario por email su propio resultado

**Lo que pre.voto NO puede hacer**:
- Publicar **agregados estadísticos** de afinidad (ej: "el 47% de nuestros usuarios coincide más con Cepeda")
- Difundir estimaciones de intención de voto
- Comportarse como encuestadora sin estar inscrita como tal

**Implicaciones técnicas**:
- El backend puede contar quiz completados (métrica interna) pero NO debe exponer agregados públicamente
- El dashboard interno con métricas (si existe) debe estar protegido y nunca renderear públicamente
- Los emails de Beehiiv contienen solo el dato individual del usuario, nunca agregados

### Veda electoral

- Veda de publicación de encuestas: desde el 24 de mayo 2026 hasta cierre de mesas el 31 de mayo
- Veda de propaganda: día de elección (31 de mayo)
- Pre.voto **no es propaganda** ni **es encuesta**, por lo tanto técnicamente puede seguir activo
- Pero por **prudencia y reputación**, el quiz se pausa entre 00:00 y 16:00 del día de elección (feature flag de veda)

### Protección de datos (Ley 1581/2012)

- El email del usuario solo se almacena si opta por suscribirse a Beehiiv
- Las respuestas del quiz NO se almacenan en la DB asociadas a un usuario identificable (solo agregados anónimos para mejorar la metodología)
- Política de privacidad en `/privacidad` (verificar que exista)

---

## No-hacer

Cosas que **no** debe hacer Claude Code, aunque parezcan razonables:

- **No reescribir el contenido editorial** (artículos, statements, codificaciones, emails). Está validado por el humano.
- **No agregar candidatos retirados al quiz** "para que estén completos". Quedaron fuera por decisión.
- **No exponer agregados públicos** de respuestas del quiz (riesgo legal).
- **No habilitar Beehiiv subscription automáticamente sin checkbox del usuario** (riesgo legal de protección de datos).
- **No incluir el plan de gobierno completo de cada candidato como adjunto/embed**. Solo links a las fuentes originales.
- **No prometer fechas exactas para Brasil/México/Argentina**. El calendario es aspiracional ("octubre 2026", "2027") pero no rígido.
- **No mencionar a competidores negativamente** en ningún copy del sitio. Si surge la cuestión, "son aportes valiosos; pre.voto entra en una línea complementaria".
- **No abrir cuenta de Instagram automatizada** ni "auto-generar" contenido para redes. Las redes las maneja el humano.
- **No habilitar donaciones** todavía. Es una decisión que el humano va a tomar después de julio.
- **No "ajustar hacia arriba" los niveles de confianza** de las codificaciones para que cuadren con porcentajes promedio mejores. La distribución actual es honesta y refleja la materia prima disponible. Si una codificación parece subestimada, hay un proceso: el humano propone la revisión en el chat web con la fuente nueva, y se actualiza.

---

## Glosario

- **Brújula electoral / VAA (Voting Advice Application)**: herramienta que compara las posiciones del usuario con las de los candidatos en una elección.
- **Pacto Histórico**: coalición de izquierda que llevó a Petro al poder en 2022. Cepeda es su candidato para 2026.
- **Centro Democrático**: partido fundado por Álvaro Uribe. Paloma Valencia es su candidata para 2026.
- **Paz Total**: política del gobierno Petro de negociación simultánea con todos los grupos armados ilegales (Ley 2272/2022).
- **C-055/2022**: sentencia de la Corte Constitucional que despenalizó el aborto hasta la semana 24.
- **Ley 2381/2024**: reforma pensional del gobierno Petro.
- **Confianza alta/media/baja**: en el contexto de codificaciones, mide qué tan respaldada está una posición. Alta = cita directa al candidato. Media = inferida de línea explícita. Baja = inferida sin cita específica.
- **`high_confidence_pct`**: campo en `candidates.json` con el porcentaje de codificaciones del candidato que están marcadas con confianza alta. Es el dato que se muestra al usuario como "% de respaldo documental".
- **Posicionamiento**: etiqueta descriptiva (no evaluativa) que pre.voto le asigna a cada candidato. Ejemplos: "el outsider de la mano dura", "el matemático del centro". **Importante**: no son juicios, son descripciones funcionales.

---

## Cuándo escalar al humano

Esto va a Claude Code (vos), no al humano:
- Implementación de tareas listadas arriba
- Ajustes técnicos menores (renombre de variables, refactor, tests)
- Resolución de bugs encontrados durante QA
- Configuración de CI/CD
- Optimización de queries SQL
- Estilos CSS y mejoras de UX menores

Esto va al humano (chat web o WhatsApp si está habilitado):
- Cualquier decisión sobre **contenido editorial** (texto, codificaciones, posiciones)
- Cambios al diseño de cálculo de afinidad
- Decisiones sobre Brasil/México/Argentina
- Respuestas a periodistas
- Quejas de candidatos o sus campañas
- Errores reportados a errores@pre.voto que parecen sustanciales
- Decisiones de presupuesto (compra de herramientas, contratación)

---

## Contacto

- Humano: en el chat web de Claude.ai (la cuenta del usuario)
- Repo: `github.com/AliasParker/Work-Space-Pre-Voto`
- Producción: https://pre.voto
- Email proyecto: hola@pre.voto

---

## Última actualización

- **Fecha**: 19 de mayo de 2026
- **Versión**: 1.1
- **Por**: Equipo pre.voto (asistencia editorial Claude vía chat web)
- **Próxima revisión**: post-lanzamiento (31 de mayo de 2026)
