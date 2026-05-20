import stripe
import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models.donation import Donation

log = structlog.get_logger()

router = APIRouter(prefix="/stripe", tags=["stripe"])


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not settings.stripe_webhook_secret:
        log.warning("stripe_webhook_secret_not_configured")
        return JSONResponse(status_code=400, content={"error": "Webhook secret not configured"})

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        log.warning("stripe_webhook_invalid_payload")
        return JSONResponse(status_code=400, content={"error": "Invalid payload"})
    except stripe.SignatureVerificationError:
        log.warning("stripe_webhook_invalid_signature")
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})

    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        session_id = data_object["id"]
        payment_intent_id = data_object.get("payment_intent")
        customer_email = data_object.get("customer_details", {}).get("email") or data_object.get("customer_email")

        result = await db.execute(
            select(Donation).where(Donation.stripe_session_id == session_id)
        )
        donation = result.scalar_one_or_none()
        if donation:
            donation.status = "succeeded"
            donation.stripe_payment_intent_id = payment_intent_id
            if customer_email:
                donation.email = customer_email
            await db.commit()
            log.info("donation_succeeded", session_id=session_id, amount_cents=donation.amount_cents, email=customer_email)

    elif event_type == "checkout.session.expired":
        session_id = data_object["id"]
        result = await db.execute(
            select(Donation).where(Donation.stripe_session_id == session_id)
        )
        donation = result.scalar_one_or_none()
        if donation:
            donation.status = "cancelled"
            await db.commit()
            log.info("donation_session_expired", session_id=session_id)

    elif event_type == "payment_intent.payment_failed":
        payment_intent_id = data_object["id"]
        result = await db.execute(
            select(Donation).where(
                Donation.stripe_payment_intent_id == payment_intent_id
            )
        )
        donation = result.scalar_one_or_none()
        if donation:
            donation.status = "failed"
            await db.commit()
            log.info("donation_payment_failed", payment_intent_id=payment_intent_id)

    return JSONResponse(status_code=200, content={"received": True})
