"""Public open-data API — statements, candidates, and positions.

All endpoints are public (no auth), read-only, and add open-data headers.
CORS is handled per-endpoint (not via global middleware) to avoid conflicts
with the app-wide allow_credentials=True setting.
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.deps import get_country_with_election
from app.models.candidate import Candidate
from app.models.country import Country
from app.models.election import Election
from app.models.position import CandidatePosition
from app.models.statement import Statement
from app.schemas.opendata import (
    OpenDataCandidate,
    OpenDataPosition,
    OpenDataStatement,
)

router = APIRouter(prefix="/opendata", tags=["opendata"])

VALUE_LABELS = {
    -2: "Totalmente en desacuerdo",
    -1: "En desacuerdo",
    0: "Neutral",
    1: "De acuerdo",
    2: "Totalmente de acuerdo",
}


def _set_opendata_headers(response: Response) -> None:
    response.headers["X-License"] = "CC-BY-4.0"
    response.headers["Access-Control-Allow-Origin"] = "*"


@router.get("/{country}/statements", response_model=list[OpenDataStatement])
async def list_statements(
    response: Response,
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    """All quiz statements for the active election in a country."""
    _set_opendata_headers(response)
    _, election = country_election
    result = await db.execute(
        select(Statement)
        .where(Statement.election_id == election.id)
        .order_by(Statement.display_order)
    )
    return result.scalars().all()


@router.get("/{country}/candidates", response_model=list[OpenDataCandidate])
async def list_candidates(
    response: Response,
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    """All candidates for the active election in a country."""
    _set_opendata_headers(response)
    _, election = country_election
    result = await db.execute(
        select(Candidate)
        .where(Candidate.election_id == election.id)
        .order_by(Candidate.ballot_position, Candidate.name)
    )
    return result.scalars().all()


@router.get("/{country}/positions", response_model=list[OpenDataPosition])
async def list_positions(
    response: Response,
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    """All candidate-statement positions (flat join) for the active election."""
    _set_opendata_headers(response)
    _, election = country_election

    result = await db.execute(
        select(CandidatePosition)
        .join(Candidate, CandidatePosition.candidate_id == Candidate.id)
        .join(Statement, CandidatePosition.statement_id == Statement.id)
        .where(Candidate.election_id == election.id)
        .options(
            selectinload(CandidatePosition.candidate),
            selectinload(CandidatePosition.statement),
        )
        .order_by(Candidate.ballot_position, Statement.display_order)
    )
    positions = result.scalars().all()

    return [
        OpenDataPosition(
            candidate_slug=pos.candidate.slug,
            candidate_name=pos.candidate.name,
            statement_slug=pos.statement.slug,
            statement_text=pos.statement.text,
            statement_category=pos.statement.category,
            value=pos.value,
            value_label=VALUE_LABELS.get(pos.value, "Desconocido"),
            confidence=pos.confidence,
            source_type=pos.source_type,
            source_quote=pos.source_quote,
            source_url=pos.source_url,
            source_date=pos.source_date,
        )
        for pos in positions
    ]
