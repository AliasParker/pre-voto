import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_admin
from app.models.article import Article
from app.models.candidate import Candidate
from app.models.poll import Poll
from app.models.position import CandidatePosition
from app.models.statement import Statement
from app.schemas.article import ArticleCreate, ArticleOut
from app.schemas.candidate import (
    BulkPositionRequest,
    CandidateCreate,
    CandidateDetail,
    CandidateOut,
    CandidateUpdate,
    PositionOut,
)
from app.schemas.poll import PollCreate, PollOut
from app.schemas.statement import StatementCreate
from app.schemas.quiz import StatementOut

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.post("/candidates", response_model=CandidateOut, status_code=201)
async def create_candidate(
    body: CandidateCreate,
    db: AsyncSession = Depends(get_db),
):
    candidate = Candidate(
        election_id=body.election_id,
        slug=body.slug,
        name=body.name,
        party=body.party,
        party_acronym=body.party_acronym,
        bio_short=body.bio_short,
        photo_url=body.photo_url,
        color=body.color,
    )
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate


@router.patch("/candidates/{candidate_id}", response_model=CandidateOut)
async def update_candidate(
    candidate_id: uuid.UUID,
    body: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(candidate, key, value)

    await db.commit()
    await db.refresh(candidate)
    return candidate


@router.post(
    "/candidates/{candidate_id}/positions",
    response_model=list[PositionOut],
    status_code=201,
)
async def bulk_upsert_positions(
    candidate_id: uuid.UUID,
    body: BulkPositionRequest,
    db: AsyncSession = Depends(get_db),
):
    # Verify candidate exists
    result = await db.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Candidate not found")

    for item in body.positions:
        stmt = pg_insert(CandidatePosition).values(
            candidate_id=candidate_id,
            statement_id=item.statement_id,
            value=item.value,
            source_quote=item.source_quote,
            source_url=item.source_url,
            source_date=item.source_date,
            coded_by=item.coded_by,
            notes=item.notes,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_candidate_positions_candidate_id",
            set_={
                "value": stmt.excluded.value,
                "source_quote": stmt.excluded.source_quote,
                "source_url": stmt.excluded.source_url,
                "source_date": stmt.excluded.source_date,
                "coded_by": stmt.excluded.coded_by,
                "notes": stmt.excluded.notes,
            },
        )
        await db.execute(stmt)

    await db.commit()

    # Return all positions for this candidate
    result = await db.execute(
        select(CandidatePosition).where(
            CandidatePosition.candidate_id == candidate_id
        )
    )
    return result.scalars().all()


@router.post("/statements", response_model=StatementOut, status_code=201)
async def create_statement(
    body: StatementCreate,
    db: AsyncSession = Depends(get_db),
):
    statement = Statement(
        election_id=body.election_id,
        text=body.text,
        category=body.category,
        weight=body.weight,
        display_order=body.display_order,
    )
    db.add(statement)
    await db.commit()
    await db.refresh(statement)
    return statement


@router.post("/articles", response_model=ArticleOut, status_code=201)
async def create_article(
    body: ArticleCreate,
    db: AsyncSession = Depends(get_db),
):
    article = Article(
        country_id=body.country_id,
        slug=body.slug,
        title=body.title,
        dek=body.dek,
        body_markdown=body.body_markdown,
        hero_image_url=body.hero_image_url,
        hero_image_attribution=body.hero_image_attribution,
        author=body.author,
        tags=body.tags,
        published_at=body.published_at,
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


@router.post("/polls", response_model=PollOut, status_code=201)
async def create_poll(
    body: PollCreate,
    db: AsyncSession = Depends(get_db),
):
    poll = Poll(
        election_id=body.election_id,
        pollster=body.pollster,
        field_start=body.field_start,
        field_end=body.field_end,
        sample_size=body.sample_size,
        methodology=body.methodology,
        results=body.results,
        source_url=body.source_url,
    )
    db.add(poll)
    await db.commit()
    await db.refresh(poll)
    return poll


@router.post("/jobs/pull-rss", status_code=501)
async def pull_rss():
    return {
        "error": {
            "code": "not_implemented",
            "message": "This endpoint will be activated in Fase 4 (worker)",
        }
    }


@router.post("/jobs/refresh-photos", status_code=501)
async def refresh_photos():
    return {
        "error": {
            "code": "not_implemented",
            "message": "This endpoint will be activated in Fase 4 (worker)",
        }
    }
