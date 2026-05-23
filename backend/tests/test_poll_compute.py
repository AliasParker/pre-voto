# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import math
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import select

from app.models.poll import Poll
from app.models.poll_average import PollAverage
from app.services.poll_compute import compute_poll_average
from tests.conftest import ELECTION_ID


class TestComputePollAverage:

    async def test_compute_weighted_average(self, db_session, seed_data):
        """Three polls with different dates and sample sizes verify decay."""
        today = date.today()

        polls_data = [
            {
                "pollster": "Pollster A",
                "field_start": today - timedelta(days=3),
                "field_end": today - timedelta(days=1),
                "sample_size": 1500,
                "results": {"valencia": 35.0, "restrepo": 25.0},
            },
            {
                "pollster": "Pollster B",
                "field_start": today - timedelta(days=10),
                "field_end": today - timedelta(days=7),
                "sample_size": 1000,
                "results": {"valencia": 30.0, "restrepo": 30.0},
            },
            {
                "pollster": "Pollster C",
                "field_start": today - timedelta(days=20),
                "field_end": today - timedelta(days=14),
                "sample_size": 800,
                "results": {"valencia": 25.0, "restrepo": 35.0},
            },
        ]

        for pd in polls_data:
            poll = Poll(election_id=ELECTION_ID, **pd)
            db_session.add(poll)
        await db_session.flush()

        avg = await compute_poll_average(ELECTION_ID, db_session)
        assert avg is not None
        assert avg.polls_included == 3

        # More recent polls with larger samples should dominate
        # Poll A (1 day old, 1500 sample) should have highest weight
        # Poll C (14 days old, 800 sample) should have lowest weight
        # Valencia: A=35 (high weight), B=30 (mid), C=25 (low) → >30
        # Restrepo: A=25 (high weight), B=30 (mid), C=35 (low) → <30
        assert avg.results["valencia"] > 30
        assert avg.results["restrepo"] < 30

        # Verify manually
        weights = []
        for pd in polls_data:
            days = (today - pd["field_end"]).days
            w = pd["sample_size"] * math.exp(-days / 14)
            weights.append(w)

        expected_v = sum(
            pd["results"]["valencia"] * w
            for pd, w in zip(polls_data, weights)
        ) / sum(weights)
        assert abs(avg.results["valencia"] - round(expected_v, 1)) < 0.2

    async def test_compute_no_polls_returns_none(self, db_session, seed_data):
        # Delete any existing polls for this election first
        result = await db_session.execute(
            select(Poll).where(Poll.election_id == ELECTION_ID)
        )
        for poll in result.scalars().all():
            await db_session.delete(poll)
        await db_session.flush()

        avg = await compute_poll_average(ELECTION_ID, db_session)
        assert avg is None
