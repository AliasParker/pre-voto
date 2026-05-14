from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_country_with_election
from app.models.country import Country
from app.models.election import Election
from app.models.poll import Poll
from app.models.poll_average import PollAverage
from app.schemas.poll import PollAverageOut, PollOut

router = APIRouter(prefix="/polls", tags=["polls"])


@router.get("/{country}", response_model=list[PollOut])
async def list_polls(
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    _, election = country_election
    result = await db.execute(
        select(Poll)
        .where(Poll.election_id == election.id, Poll.deleted_at.is_(None))
        .order_by(Poll.field_end.desc())
    )
    return result.scalars().all()


@router.get("/{country}/average", response_model=PollAverageOut)
async def get_poll_average(
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    _, election = country_election
    result = await db.execute(
        select(PollAverage)
        .where(PollAverage.election_id == election.id)
        .order_by(PollAverage.computed_at.desc())
        .limit(1)
    )
    average = result.scalar_one_or_none()
    if not average:
        raise HTTPException(status_code=404, detail="No poll average available")
    return average
