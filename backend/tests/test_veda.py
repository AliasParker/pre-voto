# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
"""Tests for veda electoral — quiz disabled during election day voting hours."""

from datetime import datetime, timezone, timedelta

import pytest

from app.config import settings
from app.services.veda import is_quiz_disabled, _parse_iso
from tests.conftest import STATEMENT_IDS


class TestParseIso:
    def test_valid_with_tz(self):
        dt = _parse_iso("2026-05-31T00:00:00-05:00")
        assert dt is not None
        assert dt.tzinfo is not None

    def test_valid_utc(self):
        dt = _parse_iso("2026-05-31T05:00:00+00:00")
        assert dt is not None

    def test_naive_gets_utc(self):
        dt = _parse_iso("2026-05-31T00:00:00")
        assert dt is not None
        assert dt.tzinfo == timezone.utc

    def test_empty_string(self):
        assert _parse_iso("") is None

    def test_invalid(self):
        assert _parse_iso("not-a-date") is None


class TestIsQuizDisabled:
    def test_disabled_during_1ra_vuelta(self, monkeypatch):
        monkeypatch.setattr(settings, "quiz_veda_start_co", "2026-05-31T00:00:00-05:00")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "2026-05-31T16:00:00-05:00")
        # 2026-05-31T10:00:00 Bogotá = 2026-05-31T15:00:00 UTC
        now = datetime(2026, 5, 31, 15, 0, 0, tzinfo=timezone.utc)
        assert is_quiz_disabled("co", now) is True

    def test_not_disabled_before_1ra_vuelta(self, monkeypatch):
        monkeypatch.setattr(settings, "quiz_veda_start_co", "2026-05-31T00:00:00-05:00")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "2026-05-31T16:00:00-05:00")
        # Day before
        now = datetime(2026, 5, 30, 12, 0, 0, tzinfo=timezone.utc)
        assert is_quiz_disabled("co", now) is False

    def test_not_disabled_after_1ra_vuelta(self, monkeypatch):
        monkeypatch.setattr(settings, "quiz_veda_start_co", "2026-05-31T00:00:00-05:00")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "2026-05-31T16:00:00-05:00")
        # 2026-05-31T16:00 Bogotá = 2026-05-31T21:00 UTC — exactly at end (exclusive)
        now = datetime(2026, 5, 31, 21, 0, 0, tzinfo=timezone.utc)
        assert is_quiz_disabled("co", now) is False

    def test_disabled_during_2da_vuelta(self, monkeypatch):
        monkeypatch.setattr(settings, "quiz_veda_start_co", "2026-05-31T00:00:00-05:00")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "2026-05-31T16:00:00-05:00")
        monkeypatch.setattr(settings, "quiz_veda_start_co_2da", "2026-06-21T00:00:00-05:00")
        monkeypatch.setattr(settings, "quiz_veda_end_co_2da", "2026-06-21T16:00:00-05:00")
        # During 2da vuelta
        now = datetime(2026, 6, 21, 10, 0, 0, tzinfo=timezone.utc)
        assert is_quiz_disabled("co", now) is True

    def test_not_disabled_for_other_country(self, monkeypatch):
        monkeypatch.setattr(settings, "quiz_veda_start_co", "2026-05-31T00:00:00-05:00")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "2026-05-31T16:00:00-05:00")
        now = datetime(2026, 5, 31, 15, 0, 0, tzinfo=timezone.utc)
        assert is_quiz_disabled("br", now) is False

    def test_not_disabled_when_empty_config(self, monkeypatch):
        monkeypatch.setattr(settings, "quiz_veda_start_co", "")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "")
        now = datetime(2026, 5, 31, 15, 0, 0, tzinfo=timezone.utc)
        assert is_quiz_disabled("co", now) is False

    def test_at_start_boundary_inclusive(self, monkeypatch):
        monkeypatch.setattr(settings, "quiz_veda_start_co", "2026-05-31T00:00:00-05:00")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "2026-05-31T16:00:00-05:00")
        # Exactly at start: 2026-05-31T00:00:00-05:00 = 2026-05-31T05:00:00 UTC
        now = datetime(2026, 5, 31, 5, 0, 0, tzinfo=timezone.utc)
        assert is_quiz_disabled("co", now) is True


@pytest.mark.usefixtures("seed_data")
class TestQuizStatusEndpoint:

    async def test_quiz_status_not_disabled(self, client, monkeypatch):
        monkeypatch.setattr(settings, "quiz_veda_start_co", "")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "")
        resp = await client.get("/feature-flags/quiz-status?country=xt")
        assert resp.status_code == 200
        assert resp.json()["quiz_disabled"] is False

    async def test_quiz_status_requires_country(self, client):
        resp = await client.get("/feature-flags/quiz-status")
        assert resp.status_code == 422


@pytest.mark.usefixtures("seed_data")
class TestQuizSubmitVeda:

    async def test_submit_returns_423_during_veda(self, client, monkeypatch):
        # Set veda window to include "now"
        now = datetime.now(timezone.utc)
        start = (now - timedelta(hours=1)).isoformat()
        end = (now + timedelta(hours=1)).isoformat()
        monkeypatch.setattr(settings, "quiz_veda_start_co", "")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "")
        # Test country is "xt", not "co" — should NOT be blocked
        answers = {str(sid): 2 for sid in STATEMENT_IDS}
        resp = await client.post("/quiz/xt/submit", json={"answers": answers})
        assert resp.status_code == 200

    async def test_submit_normal_when_no_veda(self, client, monkeypatch):
        monkeypatch.setattr(settings, "quiz_veda_start_co", "")
        monkeypatch.setattr(settings, "quiz_veda_end_co", "")
        answers = {str(sid): 2 for sid in STATEMENT_IDS}
        resp = await client.post("/quiz/xt/submit", json={"answers": answers})
        assert resp.status_code == 200
