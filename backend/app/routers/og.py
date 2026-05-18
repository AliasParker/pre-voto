"""
OG image generation and share-page endpoints.

Two routers are exposed:
- og_router (prefix="/og"): serves the generated PNG image.
- share_router (no prefix): serves a minimal HTML page with OG meta tags
  for social-media crawlers, plus a client-side redirect for real users.

Caddy rewrites /{country}/quiz?top=...&pct=... to /share/{country}/quiz?...
and proxies to the backend, which is handled by share_router.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.candidate import Candidate
from app.models.country import Country
from app.models.election import Election
from app.services.og_image import generate_og_image

og_router = APIRouter(prefix="/og", tags=["og"])
share_router = APIRouter(tags=["og"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_country_election(
    country_code: str, db: AsyncSession
) -> tuple[Country, Election]:
    """Look up active country + election by 2-letter code."""
    result = await db.execute(
        select(Country)
        .options(selectinload(Country.elections))
        .where(Country.code == country_code.lower(), Country.is_active.is_(True))
    )
    country = result.scalar_one_or_none()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    election = next((e for e in country.elections if e.is_active), None)
    if not election:
        raise HTTPException(status_code=404, detail="No active election")

    return country, election


async def _get_candidate_by_slug(
    slug: str, election_id, db: AsyncSession
) -> Candidate | None:
    result = await db.execute(
        select(Candidate).where(
            Candidate.election_id == election_id,
            Candidate.slug == slug,
        )
    )
    return result.scalar_one_or_none()


def _build_election_label(country: Country, election: Election) -> str:
    return f"pre.voto \u00b7 {country.name} {election.election_date.year}"


def _slug_to_display_name(slug: str) -> str:
    """Fallback: convert slug to title-cased name."""
    return slug.replace("-", " ").title()


# ---------------------------------------------------------------------------
# GET /og/quiz — PNG image
# ---------------------------------------------------------------------------

@og_router.get("/quiz")
async def og_quiz_image(
    country: str = Query(..., min_length=2, max_length=2),
    top: str = Query(..., min_length=1),
    pct: int = Query(..., ge=0, le=100),
    # Reserved for future visual comparison — not rendered yet.
    second: str | None = Query(None),
    second_pct: int | None = Query(None, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
) -> Response:
    country_obj, election = await _get_country_election(country, db)
    candidate = await _get_candidate_by_slug(top, election.id, db)

    candidate_name = candidate.name if candidate else _slug_to_display_name(top)
    party = candidate.party if candidate else None
    election_label = _build_election_label(country_obj, election)

    png_bytes = generate_og_image(
        candidate_name=candidate_name,
        party=party,
        pct=pct,
        election_label=election_label,
    )

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )


# ---------------------------------------------------------------------------
# GET /share/quiz/{country} — HTML with OG meta tags (Caddy proxies here)
# ---------------------------------------------------------------------------

_SHARE_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{og_title} — pre.voto</title>
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_description}">
<meta property="og:image" content="{og_image_url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="pre.voto">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{og_description}">
<meta name="twitter:image" content="{og_image_url}">
<script>window.location.replace('/{country}/quiz#top={top}&pct={pct}');</script>
</head>
<body>
<p>Redirigiendo a <a href="/{country}/quiz">pre.voto</a>...</p>
</body>
</html>
"""


@share_router.get("/share/{country}/quiz")
async def quiz_share_html(
    country: str,
    top: str = Query(..., min_length=1),
    pct: int = Query(..., ge=0, le=100),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    country_obj, election = await _get_country_election(country, db)
    candidate = await _get_candidate_by_slug(top, election.id, db)

    candidate_name = candidate.name if candidate else _slug_to_display_name(top)
    election_label = _build_election_label(country_obj, election)

    og_title = f"Mi afinidad: {pct}% con {candidate_name}"
    og_description = f"Resultado en pre.voto \u2014 {election_label}"
    og_image_url = f"/api/og/quiz?country={country}&top={top}&pct={pct}"

    html = _SHARE_HTML_TEMPLATE.format(
        og_title=og_title,
        og_description=og_description,
        og_image_url=og_image_url,
        country=country,
        top=top,
        pct=pct,
    )

    return HTMLResponse(content=html, status_code=200)
