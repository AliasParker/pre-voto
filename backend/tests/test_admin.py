from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import COUNTRY_ID, ELECTION_ID, STATEMENT_IDS


@pytest.mark.usefixtures("seed_data")
class TestAdminAuth:

    async def test_admin_no_key(self, client):
        resp = await client.post("/admin/candidates", json={})
        assert resp.status_code == 422  # Missing header

    async def test_admin_wrong_key(self, client):
        resp = await client.post(
            "/admin/candidates",
            json={},
            headers={"X-Admin-Key": "wrongkey"},
        )
        assert resp.status_code == 403

    async def test_admin_correct_key(self, client, admin_headers):
        resp = await client.post(
            "/admin/candidates",
            json={
                "election_id": str(ELECTION_ID),
                "slug": "test-admin-candidate",
                "name": "Test Candidate",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201


@pytest.mark.usefixtures("seed_data")
class TestAdminCandidates:

    async def test_create_candidate(self, client, admin_headers):
        resp = await client.post(
            "/admin/candidates",
            json={
                "election_id": str(ELECTION_ID),
                "slug": "new-candidate",
                "name": "New Candidate",
                "party": "New Party",
                "color": "#FF0000",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["slug"] == "new-candidate"
        assert data["name"] == "New Candidate"

    async def test_bulk_positions(self, client, admin_headers, seed_data):
        candidate_id = str(seed_data["candidates"][0].id)
        resp = await client.post(
            f"/admin/candidates/{candidate_id}/positions",
            json={
                "positions": [
                    {
                        "statement_id": str(STATEMENT_IDS[0]),
                        "value": 1,
                        "source_quote": "Updated quote",
                    }
                ]
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert isinstance(data, list)


@pytest.mark.usefixtures("seed_data")
class TestAdminStatements:

    async def test_create_statement(self, client, admin_headers):
        resp = await client.post(
            "/admin/statements",
            json={
                "election_id": str(ELECTION_ID),
                "text": "New test statement",
                "category": "test",
                "weight": 2,
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["text"] == "New test statement"
        assert data["weight"] == 2


@pytest.mark.usefixtures("seed_data")
class TestAdminJobs:

    async def test_pull_rss_endpoint(self, client, admin_headers):
        mock_result = {
            "job": "pull_rss",
            "status": "completed",
            "items_processed": 5,
            "errors": 0,
            "duration_ms": 123,
        }
        with patch(
            "app.jobs.pull_rss.job_pull_rss",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            resp = await client.post("/admin/jobs/pull-rss", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["job"] == "pull_rss"
        assert data["status"] == "completed"
        assert data["items_processed"] == 5

    async def test_refresh_photos_endpoint(self, client, admin_headers):
        resp = await client.post("/admin/jobs/refresh-photos", headers=admin_headers)
        assert resp.status_code == 202
        data = resp.json()
        assert data["job"] == "refresh_photos"
        assert data["status"] == "started"
