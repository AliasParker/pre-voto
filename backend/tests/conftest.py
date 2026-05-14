import uuid
from datetime import UTC, date, datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.db import get_db
from app.main import app
from app.models.article import Article
from app.models.candidate import Candidate
from app.models.country import Country
from app.models.election import Election
from app.models.poll import Poll
from app.models.poll_average import PollAverage
from app.models.position import CandidatePosition
from app.models.statement import Statement

# Use DIFFERENT UUIDs from seed data to avoid conflicts
COUNTRY_ID = uuid.UUID("aa000000-0000-0000-0000-000000000001")
ELECTION_ID = uuid.UUID("bb000000-0000-0000-0000-000000000001")
CANDIDATE_IDS = [
    uuid.UUID("cc000000-0000-0000-0000-000000000001"),
    uuid.UUID("cc000000-0000-0000-0000-000000000002"),
    uuid.UUID("cc000000-0000-0000-0000-000000000003"),
    uuid.UUID("cc000000-0000-0000-0000-000000000004"),
    uuid.UUID("cc000000-0000-0000-0000-000000000005"),
]
STATEMENT_IDS = [
    uuid.UUID("dd000000-0000-0000-0000-000000000001"),
    uuid.UUID("dd000000-0000-0000-0000-000000000002"),
    uuid.UUID("dd000000-0000-0000-0000-000000000003"),
    uuid.UUID("dd000000-0000-0000-0000-000000000004"),
    uuid.UUID("dd000000-0000-0000-0000-000000000005"),
    uuid.UUID("dd000000-0000-0000-0000-000000000006"),
    uuid.UUID("dd000000-0000-0000-0000-000000000007"),
    uuid.UUID("dd000000-0000-0000-0000-000000000008"),
]

POSITION_VALUES = [
    [2, -1, 2, 1, 1, -1, 2, 2],
    [-1, 2, -1, -1, -2, 2, -1, -1],
    [1, -2, 1, 2, 2, -1, 1, 2],
    [0, 0, 0, 1, 1, 0, 0, 1],
    [2, -1, 2, 1, 0, -2, 2, 2],
]

STATEMENT_WEIGHTS = [2, 2, 1, 2, 3, 1, 2, 1]
STATEMENT_CATEGORIES = [
    "economy", "security", "social", "environment",
    "drugs", "foreign_policy", "health", "education",
]


test_engine = create_async_engine(settings.database_url, poolclass=NullPool)


@pytest_asyncio.fixture()
async def db_session():
    """Create a session with SAVEPOINT-based test isolation."""
    async with test_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()

        session = AsyncSession(bind=conn, expire_on_commit=False)

        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(session_sync, transaction):
            if transaction.nested and not transaction._parent.nested:
                session_sync.begin_nested()

        yield session

        await session.close()
        await conn.rollback()


@pytest_asyncio.fixture()
async def client(db_session):
    """AsyncClient with overridden DB dependency and rate limiting disabled."""
    from app.limiter import limiter

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    limiter.enabled = False
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    limiter.enabled = True
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def seed_data(db_session):
    """Create test data: country, election, 5 candidates, 8 statements, 40 positions."""
    # Use test-only country code to avoid conflict with seeded "co"
    country = Country(
        id=COUNTRY_ID, code="xt", name="Testlandia", language="es", is_active=True
    )
    db_session.add(country)
    await db_session.flush()

    election = Election(
        id=ELECTION_ID,
        country_id=COUNTRY_ID,
        type="presidential_r1",
        election_date=date(2026, 5, 31),
        description="Test election",
        is_active=True,
    )
    db_session.add(election)
    await db_session.flush()

    candidate_names = [
        ("candidata-demo-alfa", "Candidata Demo Alfa", "Alianza Ciudadana", "AC", "#2A9D8F"),
        ("candidato-demo-beta", "Candidato Demo Beta", "Movimiento Fuerza Nacional", "MFN", "#C17F59"),
        ("candidata-demo-gamma", "Candidata Demo Gamma", "Partido Verde Esperanza", "PVE", "#4A7CB5"),
        ("candidato-demo-delta", "Candidato Demo Delta", "Convergencia Democrática", "CD", "#7B68A5"),
        ("candidata-demo-epsilon", "Candidata Demo Epsilon", "Movimiento Raíces", "MR", "#A3768A"),
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
    await db_session.flush()

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
    for i, txt in enumerate(statement_texts):
        s = Statement(
            id=STATEMENT_IDS[i],
            election_id=ELECTION_ID,
            text=txt,
            category=STATEMENT_CATEGORIES[i],
            weight=STATEMENT_WEIGHTS[i],
            display_order=i + 1,
            is_demo=True,
        )
        db_session.add(s)
        statements.append(s)
    await db_session.flush()

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


@pytest_asyncio.fixture()
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
            published_at=datetime(2025, 6, 1 + i, tzinfo=UTC),
        )
        db_session.add(a)
        articles.append(a)

    unpublished = Article(
        country_id=COUNTRY_ID,
        slug="unpublished-article",
        title="Unpublished",
        body_markdown="Not published yet.",
    )
    db_session.add(unpublished)

    deleted = Article(
        country_id=COUNTRY_ID,
        slug="deleted-article",
        title="Deleted",
        body_markdown="This is deleted.",
        published_at=datetime(2025, 6, 10, tzinfo=UTC),
        deleted_at=datetime(2025, 6, 11, tzinfo=UTC),
    )
    db_session.add(deleted)

    await db_session.flush()
    return articles


@pytest_asyncio.fixture()
async def seed_polls(db_session, seed_data):
    """Create test polls and average."""
    poll = Poll(
        election_id=ELECTION_ID,
        pollster="Test Pollster",
        field_start=date(2025, 5, 1),
        field_end=date(2025, 5, 5),
        sample_size=1000,
        results={"candidata-demo-alfa": 30.5, "candidato-demo-beta": 25.0},
        source_url="https://example.com/poll",
    )
    db_session.add(poll)

    avg = PollAverage(
        election_id=ELECTION_ID,
        results={"candidata-demo-alfa": 28.0, "candidato-demo-beta": 24.0},
        polls_included=3,
    )
    db_session.add(avg)

    await db_session.flush()
    return {"poll": poll, "average": avg}


@pytest.fixture()
def admin_headers():
    return {"X-Admin-Key": settings.admin_api_key}
