# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid
from pathlib import Path

import httpx
import pytest
import respx
from sqlalchemy import select

from app.models.news_item import NewsItem
from app.models.source import Source
from tests.conftest import COUNTRY_ID

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SOURCE_ID = uuid.UUID("ee000000-0000-0000-0000-000000000099")
FEED_URL = "https://example.com/rss/test.xml"


@pytest.fixture()
def sample_rss_xml():
    return (FIXTURES_DIR / "sample_rss.xml").read_text()


@pytest.fixture()
async def seed_source(db_session, seed_data):
    """Create a test RSS source."""
    source = Source(
        id=SOURCE_ID,
        country_id=COUNTRY_ID,
        name="Test Feed",
        feed_url=FEED_URL,
        is_active=True,
    )
    db_session.add(source)
    await db_session.flush()
    return source


class TestPullSource:

    @respx.mock
    async def test_pull_source_parses_and_inserts(
        self, db_session, seed_source, sample_rss_xml
    ):
        from app.services.rss_aggregator import pull_source

        respx.get(FEED_URL).mock(
            return_value=httpx.Response(200, text=sample_rss_xml)
        )

        count = await pull_source(seed_source, db_session)
        assert count == 3

        result = await db_session.execute(
            select(NewsItem).where(NewsItem.source_id == SOURCE_ID)
        )
        items = result.scalars().all()
        assert len(items) == 3

        urls = {item.url for item in items}
        assert "https://example.com/news/valencia-plan-economico" in urls
        assert "https://example.com/news/debate-bogota" in urls
        assert "https://example.com/news/encuesta-empate" in urls

        # Verify published_at was parsed
        for item in items:
            assert item.published_at is not None

    @respx.mock
    async def test_pull_source_dedup_by_url(
        self, db_session, seed_source, sample_rss_xml
    ):
        from app.services.rss_aggregator import pull_source

        respx.get(FEED_URL).mock(
            return_value=httpx.Response(200, text=sample_rss_xml)
        )

        count1 = await pull_source(seed_source, db_session)
        assert count1 == 3

        count2 = await pull_source(seed_source, db_session)
        assert count2 == 0

    @respx.mock
    async def test_pull_source_handles_feed_error(self, db_session, seed_source):
        from app.services.rss_aggregator import pull_source

        respx.get(FEED_URL).mock(side_effect=httpx.ConnectError("connection refused"))

        count = await pull_source(seed_source, db_session)
        assert count == 0
