import time

import structlog

from app.db import async_session
from app.services.newsletter import send_newsletter_digest

log = structlog.get_logger()


async def job_send_newsletter(country_id) -> dict:
    """Generate and send newsletter digest for a country."""
    log.info("job_send_newsletter_start", country_id=str(country_id))
    start = time.monotonic()

    async with async_session() as db:
        send = await send_newsletter_digest(country_id, db)

    duration_ms = round((time.monotonic() - start) * 1000)
    log.info(
        "job_send_newsletter_end",
        status=send.status,
        recipient_count=send.recipient_count,
        duration_ms=duration_ms,
    )

    return {
        "job": "send_newsletter",
        "status": "completed",
        "items_processed": send.recipient_count,
        "errors": 1 if send.status == "failed" else 0,
        "duration_ms": duration_ms,
    }
