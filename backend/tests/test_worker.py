# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.jobs.schedule import configure_scheduler


class TestSchedulerConfiguration:

    def test_scheduler_has_expected_jobs(self):
        scheduler = AsyncIOScheduler()
        configure_scheduler(scheduler)

        jobs = {j.id: j for j in scheduler.get_jobs()}

        assert "pull_rss" in jobs
        assert "refresh_photos" in jobs

        # Verify trigger types
        assert isinstance(jobs["pull_rss"].trigger, IntervalTrigger)
        assert isinstance(jobs["refresh_photos"].trigger, CronTrigger)

        # Verify interval is 30 minutes
        pull_trigger = jobs["pull_rss"].trigger
        assert pull_trigger.interval.total_seconds() == 30 * 60

        # Verify cron is at 3:00 AM
        photo_trigger = jobs["refresh_photos"].trigger
        cron_fields = {f.name: str(f) for f in photo_trigger.fields}
        assert cron_fields["hour"] == "3"
        assert cron_fields["minute"] == "0"
