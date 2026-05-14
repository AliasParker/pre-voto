"""
Newsletter digest service.

Generates a markdown digest from recent articles and polls, and sends
it via Beehiiv API (or logs a dry-run if not configured).
"""

from datetime import datetime, timedelta

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.article import Article
from app.models.newsletter_send import NewsletterSend
from app.models.poll import Poll
from app.models.subscriber import Subscriber

log = structlog.get_logger()


async def generate_digest(
    country_id, db: AsyncSession, *, days: int = 14
) -> str:
    """
    Generate a markdown newsletter digest from recent articles and polls.
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Recent articles
    result = await db.execute(
        select(Article)
        .where(
            Article.country_id == country_id,
            Article.published_at.isnot(None),
            Article.published_at >= cutoff,
            Article.deleted_at.is_(None),
        )
        .order_by(Article.published_at.desc())
        .limit(10)
    )
    articles = result.scalars().all()

    # Recent polls
    result = await db.execute(
        select(Poll)
        .where(Poll.deleted_at.is_(None))
        .order_by(Poll.field_end.desc())
        .limit(5)
    )
    polls = result.scalars().all()

    lines = ["# pre.voto — Resumen quincenal\n"]

    if articles:
        lines.append("## Artículos recientes\n")
        for a in articles:
            lines.append(f"- **{a.title}**")
            if a.dek:
                lines.append(f"  {a.dek}")
        lines.append("")

    if polls:
        lines.append("## Encuestas recientes\n")
        for p in polls:
            lines.append(f"- {p.pollster} ({p.field_start} – {p.field_end})")
        lines.append("")

    if not articles and not polls:
        lines.append("No hay novedades en este período.\n")

    return "\n".join(lines)


async def send_newsletter_digest(
    country_id, db: AsyncSession
) -> NewsletterSend:
    """
    Generate and send newsletter digest.

    Without Beehiiv API key: creates a dry_run record.
    With key: attempts to send via Beehiiv broadcast API.
    """
    digest = await generate_digest(country_id, db)
    subject = "pre.voto — Resumen quincenal"

    # Count subscribers for this country
    result = await db.execute(select(Subscriber))
    subscribers = result.scalars().all()
    recipient_count = len(subscribers)

    if not settings.beehiiv_api_key or not settings.beehiiv_publication_id:
        log.info(
            "newsletter_dry_run",
            country_id=str(country_id),
            content_length=len(digest),
            recipient_count=recipient_count,
        )
        send = NewsletterSend(
            country_id=country_id,
            subject=subject,
            recipient_count=recipient_count,
            status="dry_run",
        )
        db.add(send)
        await db.commit()
        await db.refresh(send)
        return send

    # Attempt Beehiiv send
    url = f"https://api.beehiiv.com/v2/publications/{settings.beehiiv_publication_id}/posts"
    headers = {
        "Authorization": f"Bearer {settings.beehiiv_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "title": subject,
        "subtitle": "Resumen de noticias y encuestas",
        "content": [{"type": "markdown", "markdown": digest}],
        "status": "confirmed",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            broadcast_id = data.get("data", {}).get("id")

        send = NewsletterSend(
            country_id=country_id,
            subject=subject,
            recipient_count=recipient_count,
            beehiiv_broadcast_id=broadcast_id,
            status="sent",
        )
        db.add(send)
        await db.commit()
        await db.refresh(send)

        log.info("newsletter_sent", broadcast_id=broadcast_id)
        return send

    except Exception:
        log.exception("newsletter_send_failed", country_id=str(country_id))
        send = NewsletterSend(
            country_id=country_id,
            subject=subject,
            recipient_count=recipient_count,
            status="failed",
        )
        db.add(send)
        await db.commit()
        await db.refresh(send)
        return send
