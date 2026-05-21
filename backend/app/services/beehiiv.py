import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_beehiiv_warning_logged = False

_BEEHIIV_URL_TPL = (
    "https://api.beehiiv.com/v2/publications/{pub_id}/subscriptions"
)


def _beehiiv_ready() -> bool:
    global _beehiiv_warning_logged
    if not settings.beehiiv_api_key or not settings.beehiiv_publication_id:
        if not _beehiiv_warning_logged:
            logger.warning("Beehiiv not configured — skipping newsletter forwarding")
            _beehiiv_warning_logged = True
        return False
    return True


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.beehiiv_api_key}",
        "Content-Type": "application/json",
    }


async def _post_subscription(payload: dict) -> str | None:
    url = _BEEHIIV_URL_TPL.format(pub_id=settings.beehiiv_publication_id)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=_headers(), timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("id")
    except Exception:
        logger.exception("Failed to forward subscriber to Beehiiv")
        return None


async def subscribe_from_home(email: str, country_code: str | None) -> str | None:
    """Subscribe from the newsletter form (home/article pages). Sends country_code only."""
    if not _beehiiv_ready():
        return None

    payload: dict = {"email": email}
    if country_code:
        payload["custom_fields"] = [
            {"name": "country_code", "value": country_code},
        ]
    return await _post_subscription(payload)


async def subscribe_from_quiz(
    email: str,
    country_code: str | None,
    top_match_name: str | None = None,
    top_match_pct: int | None = None,
    result_url: str | None = None,
) -> str | None:
    """Subscribe from quiz results. Sends country_code + quiz result fields."""
    if not _beehiiv_ready():
        return None

    fields = []
    if country_code:
        fields.append({"name": "country_code", "value": country_code})
    if top_match_name:
        fields.append({"name": "top_match_name", "value": top_match_name})
    if top_match_pct is not None:
        fields.append({"name": "top_match_pct", "value": top_match_pct})
    if result_url:
        fields.append({"name": "result_url", "value": result_url})

    payload: dict = {"email": email}
    if fields:
        payload["custom_fields"] = fields
    return await _post_subscription(payload)


# Backward-compatible alias
async def forward_to_beehiiv(email: str, country_code: str | None) -> str | None:
    return await subscribe_from_home(email, country_code)
