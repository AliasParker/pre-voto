import pytest

from app.config import settings


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

    async def test_future_article_not_in_list(self, client):
        resp = await client.get("/articles/xt")
        assert resp.status_code == 200
        slugs = [a["slug"] for a in resp.json()]
        assert "future-article" not in slugs

    async def test_future_article_not_accessible_by_slug(self, client):
        resp = await client.get("/articles/xt/future-article")
        assert resp.status_code == 404

    async def test_demo_article_not_in_list(self, client):
        resp = await client.get("/articles/xt")
        assert resp.status_code == 200
        slugs = [a["slug"] for a in resp.json()]
        assert "demo-article" not in slugs

    async def test_demo_article_not_accessible_by_slug(self, client):
        resp = await client.get("/articles/xt/demo-article")
        assert resp.status_code == 404


@pytest.mark.usefixtures("seed_articles")
class TestArticlesPreview:

    async def test_preview_list_requires_token(self, client):
        resp = await client.get("/articles/xt/preview")
        assert resp.status_code == 401

    async def test_preview_list_rejects_wrong_token(self, client):
        resp = await client.get("/articles/xt/preview?token=wrong")
        assert resp.status_code == 401

    async def test_preview_list_includes_future_articles(self, client, monkeypatch):
        monkeypatch.setattr(settings, "admin_preview_token", "test-secret")
        resp = await client.get("/articles/xt/preview?token=test-secret")
        assert resp.status_code == 200
        slugs = [a["slug"] for a in resp.json()]
        assert "future-article" in slugs
        # Excludes demo and deleted
        assert "demo-article" not in slugs
        assert "deleted-article" not in slugs

    async def test_preview_detail_returns_future_article(self, client, monkeypatch):
        monkeypatch.setattr(settings, "admin_preview_token", "test-secret")
        resp = await client.get("/articles/xt/preview/future-article?token=test-secret")
        assert resp.status_code == 200
        assert resp.json()["slug"] == "future-article"

    async def test_preview_detail_rejects_wrong_token(self, client):
        resp = await client.get("/articles/xt/preview/future-article?token=wrong")
        assert resp.status_code == 401
