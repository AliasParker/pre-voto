import pytest


@pytest.mark.usefixtures("seed_data")
class TestCandidatesRouter:

    async def test_list_candidates(self, client):
        resp = await client.get("/candidates/co")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 5
        slugs = {c["slug"] for c in data}
        assert "maria-valencia" in slugs

    async def test_get_candidate_by_slug(self, client):
        resp = await client.get("/candidates/co/maria-valencia")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "maria-valencia"
        assert data["name"] == "María Valencia"
        assert "positions" in data
        assert len(data["positions"]) == 8

    async def test_get_candidate_not_found(self, client):
        resp = await client.get("/candidates/co/nonexistent")
        assert resp.status_code == 404
        assert "error" in resp.json()

    async def test_candidates_bad_country(self, client):
        resp = await client.get("/candidates/xx")
        assert resp.status_code == 404
