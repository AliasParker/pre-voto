import math

import stripe
import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.limiter import limiter
from app.models.donation import Donation
from app.schemas.donation import (
    DonationCreateRequest,
    DonationCreateResponse,
    DonationStatusOut,
)

log = structlog.get_logger()

router = APIRouter(prefix="/donations", tags=["donations"])


@router.post("/create-session", response_model=DonationCreateResponse)
@limiter.limit("10/hour")
async def create_donation_session(
    body: DonationCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    if not settings.stripe_secret_key:
        return JSONResponse(
            status_code=503,
            content={"error": {"code": "stripe_not_configured", "message": "Donations are not available yet."}},
        )

    stripe.api_key = settings.stripe_secret_key

    amount_cents = math.ceil(body.amount_usd * 100)

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": amount_cents,
                        "product_data": {
                            "name": "Donación a pre.voto",
                            "description": "Contribución voluntaria al proyecto pre.voto",
                        },
                    },
                    "quantity": 1,
                }
            ],
            customer_email=body.email,
            success_url=f"{settings.frontend_url}/apoyar/gracias?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/apoyar/cancelar",
            metadata={
                "newsletter_opt_in": str(body.newsletter_opt_in).lower(),
            },
        )
    except stripe.StripeError as e:
        log.error("stripe_session_create_failed", error=str(e))
        return JSONResponse(
            status_code=502,
            content={"error": {"code": "stripe_error", "message": "Could not create payment session."}},
        )

    donation = Donation(
        email=body.email,
        amount_cents=amount_cents,
        currency="usd",
        stripe_session_id=session.id,
        status="pending",
        newsletter_opt_in=body.newsletter_opt_in,
    )
    db.add(donation)
    await db.commit()

    return DonationCreateResponse(
        checkout_url=session.url,
        session_id=session.id,
    )


@router.get("/session/{session_id}", response_model=DonationStatusOut)
async def get_donation_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Donation).where(Donation.stripe_session_id == session_id)
    )
    donation = result.scalar_one_or_none()
    if not donation:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": "Donation session not found."}},
        )
    return DonationStatusOut.model_validate(donation)
