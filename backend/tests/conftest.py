import uuid
from datetime import date, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db import get_db
from app.main import app
from app.models.article import Article
from app.models.base import Base
from app.models.candidate import Candidate
from app.models.country import Country
from app.models.election import Election
from app.models.poll import Poll
from app.models.poll_average import PollAverage
from app.models.position import CandidatePosition
from app.models.statement import Statement

# Fixed UUIDs for test data
COUNTRY_ID = uuid.UUID("a1000000-0000-0000-0000-000000000001")
ELECTION_ID = uuid.UUID("b1000000-0000-0000-0000-000000000001")
CANDIDATE_IDS = [
    uuid.UUID("c1000000-0000-0000-0000-000000000001"),
    uuid.UUID("c1000000-0000-0000-0000-000000000002"),
    uuid.UUID("c1000000-0000-0000-0000-000000000003"),
    uuid.UUID("c1000000-0000-0000-0000-000000000004"),
    uuid.UUID("c1000000-0000-0000-0000-000000000005"),
]
STATEMENT_IDS = [
    uuid.UUID("d1000000-0000-0000-0000-000000000001"),
    uuid.UUID("d1000000-0000-0000-0000-000000000002"),
    uuid.UUID("d1000000-0000-0000-0000-000000000003"),
    uuid.UUID("d1000000-0000-0000-0000-000000000004"),
    uuid.UUID("d1000000-0000-0000-0000-000000000005"),
    uuid.UUID("d1000000-0000-0000-0000-000000000006"),
    uuid.UUID("d1000000-0000-0000-0000-000000000007"),
    uuid.UUID("d1000000-0000-0000-0000-000000000008"),
]

# Position matrix: 5 candidates x 8 statements
POSITION_VALUES = [
    [2, -1, 2, 1, 1, -1, 2, 2],   # María Valencia
    [-1, 2, -1, -1, -2, 2, -1, -1],  # Carlos Restrepo
    [1, -2, 1, 2, 2, -1, 1, 2],   # Laura Castillo
    [0, 0, 0, 1, 1, 0, 0, 1],     # Andrés Molina
    [2, -1, 2, 1, 0, -2, 2, 2],   # Sofía Herrera
]

STATEMENT_WEIGHTS = [2, 2, 1, 2, 3, 1, 2, 1]
STATEMENT_CATEGORIES = [
    "economy", "security", "social", "environment",
    "drugs", "foreign_policy", "health", "education",
]


@pytest.fixture(scope="session")
def engine():
    return create_async_engine(settings.database_url)


@pytest.fixture()
async def db_session(engine):
    """Create a transactional session that rolls back after each test."""
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture()
async def client(db_session):
    """AsyncClient with overridden DB dependency."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
async def seed_data(db_session):
    """Create test data: country, election, 5 candidates, 8 statements, 40 positions."""
    # Country
    country = Country(
        id=COUNTRY_ID, code="co", name="Colombia", language="es", is_active=True
    )
    db_session.add(country)

    # Election
    election = Election(
        id=ELECTION_ID,
        country_id=COUNTRY_ID,
        type="presidential_r1",
        election_date=date(2026, 5, 31),
        description="Test election",
        is_active=True,
    )
    db_session.add(election)

    # Candidates
    candidate_names = [
        ("maria-valencia", "María Valencia", "Alianza Ciudadana", "AC", "#2A9D8F"),
        ("carlos-restrepo", "Carlos Restrepo", "Movimiento Fuerza Nacional", "MFN", "#C17F59"),
        ("laura-castillo", "Laura Castillo", "Partido Verde Esperanza", "PVE", "#4A7CB5"),
        ("andres-molina", "Andrés Molina", "Convergencia Democrática", "CD", "#7B68A5"),
        ("sofia-herrera", "Sofía Herrera", "Movimiento Raíces", "MR", "#A3768A"),
    ]
    candidates = []
    for i, (slug, name, party, acronym, color) in enumerate(candidate_names):
        c = Candidate(
            id=CANDIDATE_IDS[i],
            election_id=ELECTION_ID,
            slug=slug,
            name=name,
            party=party,
            party_acronym=acronym,
            color=color,
            bio_short=f"Bio de {name}",
            is_demo=True,
        )
        db_session.add(c)
        candidates.append(c)

    # Statements
    statements = []
    statement_texts = [
        "El gobierno debe aumentar los impuestos a las grandes fortunas.",
        "Las fuerzas armadas deben tener más autonomía.",
        "El Estado debe garantizar un ingreso básico universal.",
        "Colombia debe prohibir el fracking.",
        "La política de drogas debe priorizar la legalización regulada.",
        "Colombia debe fortalecer su relación comercial con EEUU.",
        "El sistema de salud debe avanzar hacia cobertura pública universal.",
        "La educación universitaria debe ser completamente gratuita.",
    ]
    for i, text in enumerate(statement_texts):
        s = Statement(
            id=STATEMENT_IDS[i],
            election_id=ELECTION_ID,
            text=text,
            category=STATEMENT_CATEGORIES[i],
            weight=STATEMENT_WEIGHTS[i],
            display_order=i + 1,
            is_demo=True,
        )
        db_session.add(s)
        statements.append(s)

    # Positions (5 candidates x 8 statements = 40)
    for ci, candidate in enumerate(candidates):
        for si, statement in enumerate(statements):
            pos = CandidatePosition(
                candidate_id=candidate.id,
                statement_id=statement.id,
                value=POSITION_VALUES[ci][si],
                source_quote=f"Demo quote {ci}-{si}",
                coded_by="test",
            )
            db_session.add(pos)

    await db_session.flush()
    return {
        "country": country,
        "election": election,
        "candidates": candidates,
        "statements": statements,
    }


@pytest.fixture()
async def seed_articles(db_session, seed_data):
    """Create test articles."""
    articles = []
    for i in range(5):
        a = Article(
            country_id=COUNTRY_ID,
            slug=f"test-article-{i}",
            title=f"Test Article {i}",
            dek=f"Test dek {i}",
            body_markdown=f"# Article {i}\n\nBody content.",
            author="Test Author",
            tags=["test"],
            published_at=datetime(2025, 6, 1 + i),
        )
        db_session.add(a)
        articles.append(a)

    # Add unpublished article
    unpublished = Article(
        country_id=COUNTRY_ID,
        slug="unpublished-article",
        title="Unpublished",
        body_markdown="Not published yet.",
    )
    db_session.add(unpublished)

    # Add deleted article
    deleted = Article(
        country_id=COUNTRY_ID,
        slug="deleted-article",
        title="Deleted",
        body_markdown="This is deleted.",
        published_at=datetime(2025, 6, 10),
        deleted_at=datetime(2025, 6, 11),
    )
    db_session.add(deleted)

    await db_session.flush()
    return articles


@pytest.fixture()
async def seed_polls(db_session, seed_data):
    """Create test polls and average."""
    poll = Poll(
        election_id=ELECTION_ID,
        pollster="Test Pollster",
        field_start=date(2025, 5, 1),
        field_end=date(2025, 5, 5),
        sample_size=1000,
        results={"maria-valencia": 30.5, "carlos-restrepo": 25.0},
        source_url="https://example.com/poll",
    )
    db_session.add(poll)

    avg = PollAverage(
        election_id=ELECTION_ID,
        results={"maria-valencia": 28.0, "carlos-restrepo": 24.0},
        polls_included=3,
    )
    db_session.add(avg)

    await db_session.flush()
    return {"poll": poll, "average": avg}


@pytest.fixture()
def admin_headers():
    return {"X-Admin-Key": settings.admin_api_key}
