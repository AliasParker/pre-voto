import pytest


@pytest.mark.usefixtures("seed_polls")
class TestPollsRouter:

    async def test_list_polls(self, client):
        resp = await client.get("/polls/co")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        poll = data[0]
        assert "pollster" in poll
        assert "results" in poll

    async def test_get_average(self, client):
        resp = await client.get("/polls/co/average")
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert "polls_included" in data


@pytest.mark.usefixtures("seed_data")
class TestPollsRouterNoData:

    async def test_average_not_found(self, client):
        resp = await client.get("/polls/co/average")
        assert resp.status_code == 404
