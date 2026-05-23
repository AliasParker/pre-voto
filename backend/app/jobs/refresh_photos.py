# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import time

import structlog

from app.db import async_session
from app.services.wikimedia import refresh_candidate_photos

log = structlog.get_logger()


async def job_refresh_photos() -> dict:
    """Refresh candidate photos from Wikimedia Commons."""
    log.info("job_refresh_photos_start")
    start = time.monotonic()

    async with async_session() as db:
        result = await refresh_candidate_photos(db)

    duration_ms = round((time.monotonic() - start) * 1000)
    log.info("job_refresh_photos_end", duration_ms=duration_ms, **result)

    return {
        "job": "refresh_photos",
        "status": "completed",
        "items_processed": result["updated"],
        "errors": result["errors"],
        "duration_ms": duration_ms,
    }
