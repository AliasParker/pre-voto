import pytest

from tests.conftest import STATEMENT_IDS


@pytest.mark.usefixtures("seed_data")
class TestQuizRouter:

    async def test_list_statements(self, client):
        resp = await client.get("/quiz/co/statements")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 8
        # Check ordering by display_order
        orders = [s["display_order"] for s in data]
        assert orders == sorted(orders)

    async def test_submit_quiz(self, client):
        # Build answers: agree with everything
        answers = {str(sid): 2 for sid in STATEMENT_IDS}
        resp = await client.post("/quiz/co/submit", json={"answers": answers})
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert "statements_answered" in data
        assert data["statements_answered"] == 8
        assert len(data["results"]) == 5
        # Results sorted by affinity desc
        affinities = [r["affinity"] for r in data["results"]]
        assert affinities == sorted(affinities, reverse=True)
        # Each result has required fields
        for r in data["results"]:
            assert "candidate_id" in r
            assert "slug" in r
            assert "name" in r
            assert "affinity" in r

    async def test_submit_empty_answers(self, client):
        resp = await client.post("/quiz/co/submit", json={"answers": {}})
        assert resp.status_code == 200
        data = resp.json()
        assert data["statements_answered"] == 0
        # All candidates should have 0.0 affinity
        for r in data["results"]:
            assert r["affinity"] == 0.0

    async def test_submit_with_skips(self, client):
        answers = {
            str(STATEMENT_IDS[0]): 2,
            str(STATEMENT_IDS[1]): None,
            str(STATEMENT_IDS[2]): -1,
        }
        resp = await client.post("/quiz/co/submit", json={"answers": answers})
        assert resp.status_code == 200
        data = resp.json()
        assert data["statements_answered"] == 2  # None doesn't count

    async def test_submit_bad_country(self, client):
        resp = await client.post("/quiz/xx/submit", json={"answers": {}})
        assert resp.status_code == 404
