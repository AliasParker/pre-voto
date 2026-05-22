from datetime import UTC, datetime
from unittest.mock import patch

import httpx
import pytest
import respx

from app.models.article import Article
from app.models.newsletter_send import NewsletterSend
from app.services.newsletter import generate_digest, send_newsletter_digest
from tests.conftest import COUNTRY_ID, ELECTION_ID


@pytest.fixture()
async def seed_newsletter_data(db_session, seed_data):
    """Create articles for newsletter digest testing."""
    articles = []
    for i in range(3):
        a = Article(
            country_id=COUNTRY_ID,
            slug=f"newsletter-article-{i}",
            title=f"Artículo de prueba {i}",
            dek=f"Resumen del artículo {i}",
            body_markdown=f"Contenido del artículo {i}.",
            author="Test Author",
            published_at=datetime.now(UTC),
        )
        db_session.add(a)
        articles.append(a)
    await db_session.flush()
    return articles


class TestGenerateDigest:

    async def test_generate_digest_content(self, db_session, seed_newsletter_data):
        digest = await generate_digest(COUNTRY_ID, db_session)

        assert "pre.voto" in digest
        assert "Artículo de prueba 0" in digest
        assert "Artículo de prueba 1" in digest
        assert "Artículo de prueba 2" in digest


class TestSendNewsletter:

    async def test_send_dry_run_without_key(self, db_session, seed_newsletter_data):
        """Without Beehiiv key, should create a dry_run record."""
        with patch("app.services.newsletter.settings") as mock_settings:
            mock_settings.beehiiv_api_key = ""
            mock_settings.beehiiv_publication_id = ""
            send = await send_newsletter_digest(COUNTRY_ID, db_session)

        assert isinstance(send, NewsletterSend)
        assert send.status == "dry_run"
        assert send.country_id == COUNTRY_ID
        assert send.beehiiv_broadcast_id is None

    @respx.mock
    async def test_send_with_beehiiv_mock(self, db_session, seed_newsletter_data):
        """With mocked Beehiiv API, should create a sent record."""
        with patch("app.services.newsletter.settings") as mock_settings:
            mock_settings.beehiiv_api_key = "test-key"
            mock_settings.beehiiv_publication_id = "pub-123"

            respx.post("https://api.beehiiv.com/v2/publications/pub-123/posts").mock(
                return_value=httpx.Response(
                    200, json={"data": {"id": "broadcast-456"}}
                )
            )

            send = await send_newsletter_digest(COUNTRY_ID, db_session)

            assert send.status == "sent"
            assert send.beehiiv_broadcast_id == "broadcast-456"
