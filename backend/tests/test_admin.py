import pytest

from tests.conftest import ELECTION_ID, STATEMENT_IDS


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
class TestAdminStubs:

    async def test_pull_rss_stub(self, client, admin_headers):
        resp = await client.post("/admin/jobs/pull-rss", headers=admin_headers)
        assert resp.status_code == 501

    async def test_refresh_photos_stub(self, client, admin_headers):
        resp = await client.post("/admin/jobs/refresh-photos", headers=admin_headers)
        assert resp.status_code == 501
