# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
"""Integration tests for usage tracking endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.usefixtures("seed_data")
class TestUsageEventEndpoint:
    """POST /usage/event — ingest quiz usage events."""

    async def test_quiz_started(self, client: AsyncClient):
        resp = await client.post(
            "/usage/event",
            json={"event_type": "quiz_started", "country": "xt"},
        )
        assert resp.status_code == 204

    async def test_question_answered(self, client: AsyncClient):
        resp = await client.post(
            "/usage/event",
            json={
                "event_type": "question_answered",
                "statement_id": "dd000000-0000-0000-0000-000000000001",
                "position_value": 2,
                "country": "xt",
            },
        )
        assert resp.status_code == 204

    async def test_quiz_completed(self, client: AsyncClient):
        resp = await client.post(
            "/usage/event",
            json={
                "event_type": "quiz_completed",
                "top_match_slug": "candidata-demo-alfa",
                "top_match_pct": 82.5,
                "duration_seconds": 180,
                "country": "xt",
            },
        )
        assert resp.status_code == 204

    async def test_share_clicked(self, client: AsyncClient):
        resp = await client.post(
            "/usage/event",
            json={
                "event_type": "share_clicked",
                "share_channel": "whatsapp",
                "country": "xt",
            },
        )
        assert resp.status_code == 204

    async def test_question_viewed(self, client: AsyncClient):
        resp = await client.post(
            "/usage/event",
            json={
                "event_type": "question_viewed",
                "statement_id": "dd000000-0000-0000-0000-000000000003",
                "country": "xt",
            },
        )
        assert resp.status_code == 204

    async def test_invalid_event_type(self, client: AsyncClient):
        resp = await client.post(
            "/usage/event",
            json={"event_type": "invalid_type", "country": "xt"},
        )
        assert resp.status_code == 422

    async def test_invalid_position_value(self, client: AsyncClient):
        resp = await client.post(
            "/usage/event",
            json={
                "event_type": "question_answered",
                "statement_id": "dd000000-0000-0000-0000-000000000001",
                "position_value": 5,
                "country": "xt",
            },
        )
        assert resp.status_code == 422

    async def test_invalid_share_channel(self, client: AsyncClient):
        resp = await client.post(
            "/usage/event",
            json={
                "event_type": "share_clicked",
                "share_channel": "facebook",
                "country": "xt",
            },
        )
        assert resp.status_code == 422


class TestUsageSummaryEndpoint:
    """GET /admin/usage/summary — aggregated stats with Basic Auth."""

    async def test_summary_requires_auth(self, client: AsyncClient):
        resp = await client.get("/admin/usage/summary")
        assert resp.status_code == 401

    async def test_summary_wrong_credentials(self, client: AsyncClient):
        resp = await client.get(
            "/admin/usage/summary",
            auth=("wrong", "creds"),
        )
        assert resp.status_code == 401

    async def test_summary_valid_auth(self, client: AsyncClient):
        from app.config import settings

        resp = await client.get(
            "/admin/usage/summary",
            auth=(settings.admin_user, settings.admin_pass),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "total_quiz_started" in data
        assert "total_quiz_completed" in data
        assert "completion_rate" in data
        assert "abandonment_by_question" in data
        assert "response_distribution" in data
        assert "top_matches" in data
        assert "average_duration_seconds" in data
        assert "shares_by_channel" in data

    async def test_summary_with_data(self, client: AsyncClient):
        """Ingest events then verify summary reflects them."""
        from app.config import settings

        # Ingest a few events
        await client.post(
            "/usage/event",
            json={"event_type": "quiz_started", "country": "xt"},
        )
        await client.post(
            "/usage/event",
            json={
                "event_type": "question_answered",
                "statement_id": "dd000000-0000-0000-0000-000000000001",
                "position_value": 1,
                "country": "xt",
            },
        )
        await client.post(
            "/usage/event",
            json={
                "event_type": "quiz_completed",
                "top_match_slug": "candidata-demo-alfa",
                "top_match_pct": 75.0,
                "duration_seconds": 120,
                "country": "xt",
            },
        )
        await client.post(
            "/usage/event",
            json={
                "event_type": "share_clicked",
                "share_channel": "whatsapp",
                "country": "xt",
            },
        )

        resp = await client.get(
            "/admin/usage/summary",
            auth=(settings.admin_user, settings.admin_pass),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_quiz_started"] >= 1
        assert data["total_quiz_completed"] >= 1
        assert data["completion_rate"] > 0
        assert data["shares_by_channel"]["whatsapp"] >= 1
