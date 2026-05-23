# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
"""
Poll average computation service.

Computes a weighted average of recent polls using exponential decay
based on recency. Weight formula: sample_size * exp(-days_since_field_end / 14).
"""

import math
from datetime import date

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.poll import Poll
from app.models.poll_average import PollAverage

log = structlog.get_logger()


async def compute_poll_average(
    election_id, db: AsyncSession, *, max_polls: int = 10
) -> PollAverage | None:
    """
    Compute weighted average of recent polls for an election.

    Weight = sample_size * exp(-days_since_field_end / 14)

    Returns the newly created PollAverage, or None if no polls exist.
    """
    result = await db.execute(
        select(Poll)
        .where(Poll.election_id == election_id, Poll.deleted_at.is_(None))
        .order_by(Poll.field_end.desc())
        .limit(max_polls)
    )
    polls = result.scalars().all()

    if not polls:
        return None

    today = date.today()

    # Collect all candidate slugs across polls
    all_candidates: set[str] = set()
    for poll in polls:
        all_candidates.update(poll.results.keys())

    weighted_sums: dict[str, float] = {c: 0.0 for c in all_candidates}
    total_weights: dict[str, float] = {c: 0.0 for c in all_candidates}

    for poll in polls:
        days_since = (today - poll.field_end).days
        sample = poll.sample_size or 1000  # default if missing
        weight = sample * math.exp(-days_since / 14)

        for candidate, pct in poll.results.items():
            weighted_sums[candidate] += pct * weight
            total_weights[candidate] += weight

    results = {}
    for candidate in all_candidates:
        if total_weights[candidate] > 0:
            results[candidate] = round(
                weighted_sums[candidate] / total_weights[candidate], 1
            )

    avg = PollAverage(
        election_id=election_id,
        results=results,
        polls_included=len(polls),
    )
    db.add(avg)
    await db.commit()
    await db.refresh(avg)

    log.info(
        "poll_average_computed",
        election_id=str(election_id),
        polls_included=len(polls),
    )
    return avg
