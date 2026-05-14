"""
Wikimedia Commons photo service.

Searches for candidate photos on Wikimedia Commons API and updates
candidate records with photo URL, author, and license information.
"""

from datetime import datetime, timedelta

import httpx
import structlog
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.candidate import Candidate

log = structlog.get_logger()

COMMONS_API = "https://commons.wikimedia.org/w/api.php"


async def search_candidate_photo(
    name: str, country: str = "Colombia"
) -> dict | None:
    """
    Search Wikimedia Commons for a candidate photo.

    Returns dict with {url, author, license, attribution} or None if not found.
    """
    params = {
        "action": "query",
        "generator": "search",
        "gsrnamespace": "6",
        "gsrsearch": f"{name} {country}",
        "gsrlimit": "1",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "format": "json",
    }
    headers = {"User-Agent": settings.wikimedia_user_agent}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(COMMONS_API, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        log.warning("wikimedia_search_failed", name=name)
        return None

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None

    # Take the first result
    page = next(iter(pages.values()))
    imageinfo = page.get("imageinfo", [])
    if not imageinfo:
        return None

    info = imageinfo[0]
    url = info.get("url")
    if not url:
        return None

    extmetadata = info.get("extmetadata", {})
    author = extmetadata.get("Artist", {}).get("value", "Unknown")
    license_name = extmetadata.get("LicenseShortName", {}).get("value", "Unknown")
    attribution = f"{author}, {license_name}, via Wikimedia Commons"

    return {
        "url": url,
        "author": author,
        "license": license_name,
        "attribution": attribution,
    }


async def refresh_candidate_photos(db: AsyncSession) -> dict:
    """
    Update photos for candidates missing photo_url or not updated in 30+ days.

    Returns dict with {updated, not_found, errors}.
    """
    cutoff = datetime.utcnow() - timedelta(days=30)

    result = await db.execute(
        select(Candidate).where(
            or_(
                Candidate.photo_url.is_(None),
                Candidate.updated_at < cutoff,
            )
        )
    )
    candidates = result.scalars().all()

    updated = 0
    not_found = 0
    errors = 0

    for candidate in candidates:
        try:
            photo = await search_candidate_photo(candidate.name)
        except Exception:
            log.exception("wikimedia_refresh_error", candidate=candidate.name)
            errors += 1
            continue

        if photo:
            candidate.photo_url = photo["url"]
            candidate.photo_author = photo["author"]
            candidate.photo_license = photo["license"]
            candidate.photo_attribution = photo["attribution"]
            updated += 1
            log.info("wikimedia_photo_updated", candidate=candidate.name)
        else:
            not_found += 1
            log.info("wikimedia_photo_not_found", candidate=candidate.name)

    await db.commit()

    return {"updated": updated, "not_found": not_found, "errors": errors}
