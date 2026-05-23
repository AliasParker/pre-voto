# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
"""
Scheduler configuration for background jobs.

Registers jobs with APScheduler triggers. Import and call
configure_scheduler() to set up the cron schedule.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


def configure_scheduler(scheduler: AsyncIOScheduler) -> None:
    """Register all background jobs with their triggers."""
    from app.jobs.pull_rss import job_pull_rss
    from app.jobs.refresh_photos import job_refresh_photos

    scheduler.add_job(
        job_pull_rss,
        trigger=IntervalTrigger(minutes=30),
        id="pull_rss",
        name="Pull RSS feeds",
        replace_existing=True,
    )

    scheduler.add_job(
        job_refresh_photos,
        trigger=CronTrigger(hour=3, minute=0),
        id="refresh_photos",
        name="Refresh candidate photos",
        replace_existing=True,
    )
