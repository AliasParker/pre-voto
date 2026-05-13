import pytest


@pytest.mark.usefixtures("seed_articles")
class TestArticlesRouter:

    async def test_list_articles(self, client):
        resp = await client.get("/articles/xt")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # Should have 5 published articles (not unpublished, not deleted)
        assert len(data) == 5

    async def test_list_articles_total_count_header(self, client):
        resp = await client.get("/articles/xt")
        assert "x-total-count" in resp.headers
        assert resp.headers["x-total-count"] == "5"

    async def test_list_articles_pagination(self, client):
        resp = await client.get("/articles/xt?offset=0&limit=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert resp.headers["x-total-count"] == "5"

    async def test_list_articles_limit_max_100(self, client):
        resp = await client.get("/articles/xt?limit=200")
        assert resp.status_code == 422  # validation error

    async def test_get_article_by_slug(self, client):
        resp = await client.get("/articles/xt/test-article-0")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "test-article-0"
        assert "body_markdown" in data

    async def test_get_article_not_found(self, client):
        resp = await client.get("/articles/xt/nonexistent")
        assert resp.status_code == 404

    async def test_deleted_article_not_accessible(self, client):
        resp = await client.get("/articles/xt/deleted-article")
        assert resp.status_code == 404
