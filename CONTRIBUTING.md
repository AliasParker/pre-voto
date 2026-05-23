# Contribuir a pre.voto

Gracias por tu interés en contribuir. pre.voto es una brújula electoral de código abierto para Latinoamérica.

## Tipos de contribución

### Correcciones editoriales

Si encontraste un error en una codificación de candidato (posición incorrecta, fuente rota, cita mal atribuida):

1. Escribe a [errores@pre.voto](mailto:errores@pre.voto) o abre un issue en GitHub.
2. Incluye: candidato, statement, posición que consideras correcta, y fuente verificable.
3. El protocolo completo está en [pre.voto/correcciones](https://pre.voto/correcciones).

### Código

1. Abre un issue describiendo el cambio antes de escribir código.
2. Fork el repo y crea una rama desde `main`.
3. Asegúrate de que `docker compose run --rm api-test` pasa.
4. Abre un pull request con descripción clara del cambio y su motivación.

### Codificaciones para un nuevo país

Si quieres ayudar a codificar posiciones de candidatos para una elección en Brasil, México, Argentina u otro país:

1. Escribe a [hola@pre.voto](mailto:hola@pre.voto) con el país y la elección.
2. El equipo editorial coordina la investigación, las fuentes y la metodología.

## Setup local

```bash
git clone https://github.com/AliasParker/pre-voto.git
cd pre-voto
cp .env.example .env
docker compose up -d
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.seed_colombia_2026
```

Abre `http://localhost` para ver el frontend. La API responde en `http://localhost/api/health`.

## Reglas

- No commitear archivos `.env` ni credenciales.
- No pushear directamente a `main`. Siempre via PR.
- Dependencias del frontend: nunca `npm install` en el host. Usar `docker compose exec frontend npm install <pkg>` o editar `package.json` y rebuild.
- Los SPDX headers (`SPDX-License-Identifier: AGPL-3.0-or-later`) deben mantenerse en archivos nuevos.

## Licencia

Al contribuir, aceptas que tu contribución se licencia bajo:

- **AGPL-3.0-or-later** para código.
- **CC-BY 4.0** para contenido editorial.

## Código de conducta

Este proyecto sigue el [Contributor Covenant](CODE_OF_CONDUCT.md). Al participar, te comprometes a mantener un ambiente respetuoso.

## Contacto

- Consultas generales: [hola@pre.voto](mailto:hola@pre.voto)
- Errores editoriales: [errores@pre.voto](mailto:errores@pre.voto)
