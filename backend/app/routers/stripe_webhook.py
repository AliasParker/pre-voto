import stripe
import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models.donation import Donation
from app.services.email import send_donation_email
from app.tasks import spawn_background_task

log = structlog.get_logger()

router = APIRouter(prefix="/donations/stripe", tags=["stripe"])


def _field(obj, key, default=None):
    """Get field from dict or StripeObject (SDK v15+ returns StripeObjects)."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


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

    event_type = _field(event, "type")
    event_data = _field(event, "data")
    data_object = _field(event_data, "object")

    if event_type == "checkout.session.completed":
        session_id = _field(data_object, "id")
        payment_intent_id = _field(data_object, "payment_intent")
        customer_details = _field(data_object, "customer_details")
        customer_email = _field(customer_details, "email") if customer_details else None
        if not customer_email:
            customer_email = _field(data_object, "customer_email")

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

            # TX2: send thank-you email
            if customer_email:
                amount_display = f"US${donation.amount_cents / 100:.2f}"
                spawn_background_task(
                    send_donation_email(customer_email, amount_display),
                    name="send_donation_email",
                )

    elif event_type == "checkout.session.expired":
        session_id = _field(data_object, "id")
        result = await db.execute(
            select(Donation).where(Donation.stripe_session_id == session_id)
        )
        donation = result.scalar_one_or_none()
        if donation:
            donation.status = "cancelled"
            await db.commit()
            log.info("donation_session_expired", session_id=session_id)

    elif event_type == "payment_intent.payment_failed":
        payment_intent_id = _field(data_object, "id")
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
