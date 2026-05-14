import hashlib

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.deps import get_country_with_election
from app.models.candidate import Candidate
from app.models.country import Country
from app.models.election import Election
from app.models.quiz_completion import QuizCompletion
from app.models.statement import Statement
from app.schemas.quiz import CandidateAffinity, QuizResult, QuizSubmitRequest, StatementOut
from app.services.matching import compute_affinity

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/{country}/statements", response_model=list[StatementOut])
async def list_statements(
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    _, election = country_election
    result = await db.execute(
        select(Statement)
        .where(Statement.election_id == election.id)
        .order_by(Statement.display_order)
    )
    return result.scalars().all()


@router.post("/{country}/submit", response_model=QuizResult)
async def submit_quiz(
    body: QuizSubmitRequest,
    request: Request,
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    _, election = country_election

    # Fetch candidates with their positions
    result = await db.execute(
        select(Candidate)
        .options(selectinload(Candidate.positions))
        .where(Candidate.election_id == election.id)
    )
    candidates = result.scalars().all()

    # Fetch statement weights
    stmt_result = await db.execute(
        select(Statement).where(Statement.election_id == election.id)
    )
    statements = stmt_result.scalars().all()
    statement_weights = {s.id: s.weight for s in statements}

    # Compute affinity per candidate
    affinities: list[CandidateAffinity] = []
    for candidate in candidates:
        cand_positions = {p.statement_id: p.value for p in candidate.positions}
        affinity = compute_affinity(body.answers, cand_positions, statement_weights)
        affinities.append(
            CandidateAffinity(
                candidate_id=candidate.id,
                slug=candidate.slug,
                name=candidate.name,
                party=candidate.party,
                party_acronym=candidate.party_acronym,
                photo_url=candidate.photo_url,
                color=candidate.color,
                affinity=affinity,
            )
        )

    # Sort by affinity descending
    affinities.sort(key=lambda a: a.affinity, reverse=True)

    # Count answered statements
    statements_answered = sum(1 for v in body.answers.values() if v is not None)

    # Persist quiz completion
    ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if not ip and request.client:
        ip = request.client.host
    ua = request.headers.get("user-agent", "")
    from datetime import date

    day_str = date.today().isoformat()
    session_hash = hashlib.sha256(f"{ip}{ua}{day_str}".encode()).hexdigest()[:16]

    top_match = affinities[0] if affinities else None
    completion = QuizCompletion(
        election_id=election.id,
        session_hash=session_hash,
        statements_answered=statements_answered,
        top_match_candidate_id=top_match.candidate_id if top_match else None,
        top_match_pct=top_match.affinity if top_match else None,
    )
    db.add(completion)
    await db.commit()

    return QuizResult(results=affinities, statements_answered=statements_answered)
