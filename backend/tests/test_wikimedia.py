import json
from pathlib import Path

import httpx
import pytest
import respx
from sqlalchemy import select

from app.models.candidate import Candidate
from app.services.wikimedia import COMMONS_API, search_candidate_photo, refresh_candidate_photos
from tests.conftest import CANDIDATE_IDS

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def wikimedia_found():
    return json.loads((FIXTURES_DIR / "wikimedia_response.json").read_text())


@pytest.fixture()
def wikimedia_empty():
    return json.loads((FIXTURES_DIR / "wikimedia_empty.json").read_text())


@pytest.fixture()
def wikimedia_pdf():
    return json.loads((FIXTURES_DIR / "wikimedia_pdf.json").read_text())


class TestSearchCandidatePhoto:

    @respx.mock
    async def test_search_candidate_photo_found(self, wikimedia_found):
        respx.get(COMMONS_API).mock(
            return_value=httpx.Response(200, json=wikimedia_found)
        )

        result = await search_candidate_photo("María Valencia", "Colombia")
        assert result is not None
        assert result["url"] == "https://upload.wikimedia.org/wikipedia/commons/a/ab/María_Valencia_2025.jpg"
        assert result["author"] == "Juan Pérez"
        assert result["license"] == "CC BY-SA 4.0"
        assert "Wikimedia Commons" in result["attribution"]

    @respx.mock
    async def test_search_candidate_photo_not_found(self, wikimedia_empty):
        respx.get(COMMONS_API).mock(
            return_value=httpx.Response(200, json=wikimedia_empty)
        )

        result = await search_candidate_photo("Unknown Person", "Colombia")
        assert result is None

    @respx.mock
    async def test_search_candidate_photo_rejects_pdf(self, wikimedia_pdf):
        respx.get(COMMONS_API).mock(
            return_value=httpx.Response(200, json=wikimedia_pdf)
        )

        result = await search_candidate_photo("Laura Castillo", "Colombia")
        assert result is None


class TestRefreshCandidatePhotos:

    @respx.mock
    async def test_refresh_candidate_photos_updates_fields(
        self, db_session, seed_data, wikimedia_found
    ):
        respx.get(COMMONS_API).mock(
            return_value=httpx.Response(200, json=wikimedia_found)
        )

        result = await refresh_candidate_photos(db_session)
        assert result["updated"] > 0

        # Verify first candidate got photo
        row = await db_session.execute(
            select(Candidate).where(Candidate.id == CANDIDATE_IDS[0])
        )
        candidate = row.scalar_one()
        assert candidate.photo_url is not None
        assert "wikimedia" in candidate.photo_url
        assert candidate.photo_author == "Juan Pérez"
        assert candidate.photo_license == "CC BY-SA 4.0"

    @respx.mock
    async def test_refresh_candidate_not_found_leaves_null(
        self, db_session, seed_data, wikimedia_empty
    ):
        respx.get(COMMONS_API).mock(
            return_value=httpx.Response(200, json=wikimedia_empty)
        )

        result = await refresh_candidate_photos(db_session)
        assert result["not_found"] > 0

        row = await db_session.execute(
            select(Candidate).where(Candidate.id == CANDIDATE_IDS[0])
        )
        candidate = row.scalar_one()
        assert candidate.photo_url is None

    @respx.mock
    async def test_refresh_candidate_pdf_result_leaves_null(
        self, db_session, seed_data, wikimedia_pdf
    ):
        respx.get(COMMONS_API).mock(
            return_value=httpx.Response(200, json=wikimedia_pdf)
        )

        result = await refresh_candidate_photos(db_session)
        # PDF results are treated as not found
        assert result["not_found"] > 0
        assert result["updated"] == 0

        row = await db_session.execute(
            select(Candidate).where(Candidate.id == CANDIDATE_IDS[0])
        )
        candidate = row.scalar_one()
        assert candidate.photo_url is None
