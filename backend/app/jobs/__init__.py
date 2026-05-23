# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
from app.jobs.compute_poll_avg import job_compute_poll_average
from app.jobs.pull_rss import job_pull_rss
from app.jobs.refresh_photos import job_refresh_photos
from app.jobs.send_newsletter import job_send_newsletter

__all__ = [
    "job_pull_rss",
    "job_refresh_photos",
    "job_compute_poll_average",
    "job_send_newsletter",
]
