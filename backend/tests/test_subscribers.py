import pytest


@pytest.mark.usefixtures("seed_data")
class TestSubscribersRouter:

    async def test_create_subscriber(self, client):
        resp = await client.post(
            "/subscribers",
            json={"email": "test@example.com", "country_code": "co"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["country_code"] == "co"
        # Email should NOT be in response
        assert "email" not in data

    async def test_duplicate_email(self, client):
        # First subscription
        await client.post(
            "/subscribers",
            json={"email": "dup@example.com", "country_code": "co"},
        )
        # Second subscription (upsert)
        resp = await client.post(
            "/subscribers",
            json={"email": "dup@example.com", "country_code": "br"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["country_code"] == "br"

    async def test_invalid_email(self, client):
        resp = await client.post(
            "/subscribers",
            json={"email": "not-an-email"},
        )
        assert resp.status_code == 422
