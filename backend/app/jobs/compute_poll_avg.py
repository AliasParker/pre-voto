import time

import structlog

from app.db import async_session
from app.services.poll_compute import compute_poll_average

log = structlog.get_logger()


async def job_compute_poll_average(election_id) -> dict:
    """Compute weighted poll average for an election."""
    log.info("job_compute_poll_average_start", election_id=str(election_id))
    start = time.monotonic()

    async with async_session() as db:
        avg = await compute_poll_average(election_id, db)

    duration_ms = round((time.monotonic() - start) * 1000)

    if avg is None:
        log.info("job_compute_poll_average_end", status="no_polls", duration_ms=duration_ms)
        return {
            "job": "compute_poll_average",
            "status": "completed",
            "items_processed": 0,
            "errors": 0,
            "duration_ms": duration_ms,
        }

    log.info(
        "job_compute_poll_average_end",
        polls_included=avg.polls_included,
        duration_ms=duration_ms,
    )
    return {
        "job": "compute_poll_average",
        "status": "completed",
        "items_processed": avg.polls_included or 0,
        "errors": 0,
        "duration_ms": duration_ms,
    }
