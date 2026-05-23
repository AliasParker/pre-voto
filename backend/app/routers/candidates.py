# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.deps import get_country_with_election
from app.models.candidate import Candidate
from app.models.country import Country
from app.models.election import Election
from app.schemas.candidate import CandidateDetail, CandidateOut

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/{country}", response_model=list[CandidateOut])
async def list_candidates(
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    _, election = country_election
    result = await db.execute(
        select(Candidate)
        .where(Candidate.election_id == election.id)
        .order_by(Candidate.ballot_position, Candidate.name)
    )
    return result.scalars().all()


@router.get("/{country}/{slug}", response_model=CandidateDetail)
async def get_candidate(
    slug: str,
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    _, election = country_election
    result = await db.execute(
        select(Candidate)
        .options(selectinload(Candidate.positions))
        .where(Candidate.election_id == election.id, Candidate.slug == slug)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
