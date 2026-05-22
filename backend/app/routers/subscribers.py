from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.db import get_db
from app.limiter import limiter
from app.models.subscriber import Subscriber
from app.schemas.subscriber import SubscriberCreate, SubscriberOut
# PAUSED: from app.services.beehiiv import subscribe_from_home, subscribe_from_quiz
from app.services.email import send_welcome_email
from app.tasks import spawn_background_task

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

    is_new = existing is None

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

    # PAUSED: Beehiiv dispatch (subscribe_from_home / subscribe_from_quiz)
    # Subscribers are saved to DB only. Beehiiv sync can be re-enabled later.

    # TX1: send welcome email to new non-quiz subscribers
    if is_new and not body.top_match_name:
        spawn_background_task(
            send_welcome_email(body.email),
            name="send_welcome_email",
        )

    return subscriber
