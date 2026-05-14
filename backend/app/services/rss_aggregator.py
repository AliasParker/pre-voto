"""
RSS feed aggregator service.

Fetches RSS feeds, parses entries with feedparser, and inserts new items
into the news_items table with deduplication via ON CONFLICT DO NOTHING
on the unique url constraint.
"""

import asyncio
import time
from calendar import timegm
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse

import feedparser
import httpx
import structlog
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.news_item import NewsItem
from app.models.source import Source

log = structlog.get_logger()


def _parse_published(entry) -> datetime | None:
    """Convert feedparser's published_parsed (time.struct_time) to naive UTC datetime."""
    pp = entry.get("published_parsed")
    if pp is not None:
        return datetime.utcfromtimestamp(timegm(pp))
    return None


async def pull_source(source: Source, db: AsyncSession) -> int:
    """
    Fetch a single RSS feed and insert new items.

    Returns the number of new items inserted.
    """
    new_count = 0
    try:
        headers = {"User-Agent": settings.wikimedia_user_agent}
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            resp = await client.get(source.feed_url)
            resp.raise_for_status()
    except Exception:
        log.warning("rss_fetch_failed", source=source.name, url=source.feed_url)
        return 0

    feed = feedparser.parse(resp.text)

    for entry in feed.entries:
        url = entry.get("link")
        title = entry.get("title")
        if not url or not title:
            continue

        snippet = entry.get("summary") or entry.get("description")
        if snippet and len(snippet) > 500:
            snippet = snippet[:497] + "..."

        published_at = _parse_published(entry)

        stmt = pg_insert(NewsItem).values(
            source_id=source.id,
            country_id=source.country_id,
            url=url,
            title=title,
            snippet=snippet,
            published_at=published_at,
        )
        stmt = stmt.on_conflict_do_nothing(constraint="uq_news_items_url")
        result = await db.execute(stmt)
        if result.rowcount > 0:
            new_count += 1

    # Update last_pulled_at
    await db.execute(
        update(Source).where(Source.id == source.id).values(last_pulled_at=datetime.utcnow())
    )
    await db.commit()

    log.info("rss_source_pulled", source=source.name, new_items=new_count)
    return new_count


async def pull_all_sources(db: AsyncSession) -> dict:
    """
    Pull all active RSS sources with rate limiting (1s between calls to same domain).

    Returns dict with keys: items_processed, errors, sources_fetched.
    """
    result_obj = await db.execute(
        select(Source).where(Source.is_active.is_(True))
    )
    sources = result_obj.scalars().all()

    total_items = 0
    errors = 0
    domain_last_call: dict[str, float] = defaultdict(float)

    for source in sources:
        domain = urlparse(source.feed_url).netloc

        # Rate limit: 1 second between calls to the same domain
        elapsed = time.monotonic() - domain_last_call[domain]
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)

        try:
            count = await pull_source(source, db)
            total_items += count
        except Exception:
            log.exception("rss_pull_source_error", source=source.name)
            errors += 1

        domain_last_call[domain] = time.monotonic()

    return {
        "items_processed": total_items,
        "errors": errors,
        "sources_fetched": len(sources),
    }
