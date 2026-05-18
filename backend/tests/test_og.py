import pytest
from PIL import Image
import io


@pytest.mark.usefixtures("seed_data")
class TestOgQuizImage:

    async def test_og_quiz_image_valid(self, client):
        resp = await client.get(
            "/og/quiz",
            params={"country": "xt", "top": "candidata-demo-alfa", "pct": 82},
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"
        assert "max-age=86400" in resp.headers["cache-control"]

    async def test_og_quiz_image_missing_params(self, client):
        resp = await client.get("/og/quiz")
        assert resp.status_code == 422

    async def test_og_quiz_image_invalid_country(self, client):
        resp = await client.get(
            "/og/quiz",
            params={"country": "zz", "top": "slug", "pct": 82},
        )
        assert resp.status_code == 404

    async def test_og_quiz_image_dimensions(self, client):
        resp = await client.get(
            "/og/quiz",
            params={"country": "xt", "top": "candidata-demo-alfa", "pct": 82},
        )
        assert resp.status_code == 200
        img = Image.open(io.BytesIO(resp.content))
        assert img.size == (1200, 630)


@pytest.mark.usefixtures("seed_data")
class TestShareHtml:

    async def test_share_html_contains_og_meta(self, client):
        resp = await client.get(
            "/share/xt/quiz",
            params={"top": "candidata-demo-alfa", "pct": 82},
        )
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        body = resp.text
        assert '<meta property="og:image"' in body
        assert "/api/og/quiz?country=xt&top=candidata-demo-alfa&pct=82" in body

    async def test_share_html_redirect_script(self, client):
        resp = await client.get(
            "/share/xt/quiz",
            params={"top": "candidata-demo-alfa", "pct": 82},
        )
        assert resp.status_code == 200
        body = resp.text
        assert "window.location.replace(" in body
        assert "/xt/quiz#top=candidata-demo-alfa&pct=82" in body
