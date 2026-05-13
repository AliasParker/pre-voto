import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_beehiiv_warning_logged = False


async def forward_to_beehiiv(email: str, country_code: str | None) -> str | None:
    """
    Forward a subscriber to Beehiiv newsletter platform.

    Returns beehiiv_id if successful, None otherwise.
    """
    global _beehiiv_warning_logged

    if not settings.beehiiv_api_key or not settings.beehiiv_publication_id:
        if not _beehiiv_warning_logged:
            logger.warning("Beehiiv not configured — skipping newsletter forwarding")
            _beehiiv_warning_logged = True
        return None

    url = f"https://api.beehiiv.com/v2/publications/{settings.beehiiv_publication_id}/subscriptions"
    headers = {
        "Authorization": f"Bearer {settings.beehiiv_api_key}",
        "Content-Type": "application/json",
    }
    payload: dict = {"email": email}
    if country_code:
        payload["custom_fields"] = [{"name": "country", "value": country_code}]

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("id")
    except Exception:
        logger.exception("Failed to forward subscriber to Beehiiv")
        return None
