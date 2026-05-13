import asyncio

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.db import get_db
from app.limiter import limiter
from app.models.subscriber import Subscriber
from app.schemas.subscriber import SubscriberCreate, SubscriberOut
from app.services.beehiiv import forward_to_beehiiv

router = APIRouter(prefix="/subscribers", tags=["subscribers"])


@router.post("", response_model=SubscriberOut, status_code=201)
@limiter.limit("5/hour")
async def create_subscriber(
    body: SubscriberCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Check if subscriber already exists
    result = await db.execute(
        select(Subscriber).where(Subscriber.email == body.email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update country_code if provided
        if body.country_code:
            existing.country_code = body.country_code
        if body.source:
            existing.source = body.source
        existing.status = "pending"
        await db.commit()
        await db.refresh(existing)
        subscriber = existing
    else:
        subscriber = Subscriber(
            email=body.email,
            country_code=body.country_code,
            source=body.source,
            status="pending",
        )
        db.add(subscriber)
        await db.commit()
        await db.refresh(subscriber)

    # Forward to Beehiiv in background (don't block response)
    asyncio.create_task(forward_to_beehiiv(body.email, body.country_code))

    return subscriber
