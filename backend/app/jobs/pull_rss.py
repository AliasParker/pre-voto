import time

import structlog

from app.db import async_session
from app.services.rss_aggregator import pull_all_sources

log = structlog.get_logger()


async def job_pull_rss() -> dict:
    """Pull all active RSS sources and return job result."""
    log.info("job_pull_rss_start")
    start = time.monotonic()

    async with async_session() as db:
        result = await pull_all_sources(db)

    duration_ms = round((time.monotonic() - start) * 1000)
    log.info("job_pull_rss_end", duration_ms=duration_ms, **result)

    return {
        "job": "pull_rss",
        "status": "completed",
        "items_processed": result["items_processed"],
        "errors": result["errors"],
        "duration_ms": duration_ms,
    }
