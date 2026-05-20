from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_country_with_election
from app.models.article import Article
from app.models.country import Country
from app.models.election import Election
from app.schemas.article import ArticleDetail, ArticleOut

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/{country}", response_model=list[ArticleOut])
async def list_articles(
    response: Response,
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    country_obj, _ = country_election

    base_filter = (
        Article.country_id == country_obj.id,
        Article.deleted_at.is_(None),
        Article.published_at.is_not(None),
        Article.published_at <= func.now(),
        Article.is_demo.is_(False),
    )

    # Total count
    count_result = await db.execute(
        select(func.count(Article.id)).where(*base_filter)
    )
    total = count_result.scalar_one()
    response.headers["X-Total-Count"] = str(total)

    # Paginated results
    result = await db.execute(
        select(Article)
        .where(*base_filter)
        .order_by(Article.published_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{country}/{slug}", response_model=ArticleDetail)
async def get_article(
    slug: str,
    country_election: tuple[Country, Election] = Depends(get_country_with_election),
    db: AsyncSession = Depends(get_db),
):
    country_obj, _ = country_election
    result = await db.execute(
        select(Article).where(
            Article.country_id == country_obj.id,
            Article.slug == slug,
            Article.deleted_at.is_(None),
            Article.published_at.is_not(None),
            Article.published_at <= func.now(),
            Article.is_demo.is_(False),
        )
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
