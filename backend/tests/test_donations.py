"""Tests for donations router and Stripe webhook."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.donation import Donation


@pytest_asyncio.fixture()
async def seed_donation(db_session: AsyncSession):
    """Create a test donation record."""
    donation = Donation(
        email="donor@example.com",
        amount_cents=1000,
        currency="usd",
        stripe_session_id="cs_test_abc123",
        status="pending",
        newsletter_opt_in=True,
    )
    db_session.add(donation)
    await db_session.flush()
    return donation


class TestCreateSession:

    async def test_create_session_returns_503_without_stripe_key(self, client, monkeypatch):
        """Without STRIPE_SECRET_KEY configured, returns 503."""
        monkeypatch.setattr("app.config.settings.stripe_secret_key", "")
        resp = await client.post(
            "/donations/create-session",
            json={"amount_usd": 10, "email": "test@example.com"},
        )
        assert resp.status_code == 503
        data = resp.json()
        assert data["error"]["code"] == "stripe_not_configured"

    async def test_create_session_invalid_amount_below_minimum(self, client):
        """Amount below $1 should fail validation."""
        resp = await client.post(
            "/donations/create-session",
            json={"amount_usd": 0.50, "email": "test@example.com"},
        )
        assert resp.status_code == 422

    async def test_create_session_invalid_amount_above_maximum(self, client):
        """Amount above $10,000 should fail validation."""
        resp = await client.post(
            "/donations/create-session",
            json={"amount_usd": 50000, "email": "test@example.com"},
        )
        assert resp.status_code == 422

    async def test_create_session_invalid_email(self, client):
        """Invalid email should fail validation."""
        resp = await client.post(
            "/donations/create-session",
            json={"amount_usd": 10, "email": "not-an-email"},
        )
        assert resp.status_code == 422

    async def test_create_session_valid_request(self, client, monkeypatch, db_session):
        """Valid request with mocked Stripe creates session and DB record."""
        monkeypatch.setattr("app.config.settings.stripe_secret_key", "sk_test_fake")

        mock_session = MagicMock()
        mock_session.id = "cs_test_new_session"
        mock_session.url = "https://checkout.stripe.com/test"

        with patch("app.routers.donations.stripe") as mock_stripe:
            mock_stripe.checkout.Session.create.return_value = mock_session
            mock_stripe.StripeError = Exception

            resp = await client.post(
                "/donations/create-session",
                json={
                    "amount_usd": 25,
                    "email": "donor@example.com",
                    "newsletter_opt_in": True,
                },
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["checkout_url"] == "https://checkout.stripe.com/test"
        assert data["session_id"] == "cs_test_new_session"


class TestDonationStatus:

    async def test_session_status_found(self, client, seed_donation):
        """Returns donation status for existing session."""
        resp = await client.get(f"/donations/session/{seed_donation.stripe_session_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["amount_cents"] == 1000
        assert data["currency"] == "usd"
        assert data["status"] == "pending"
        assert "created_at" in data

    async def test_session_status_not_found(self, client):
        """Returns 404 for unknown session."""
        resp = await client.get("/donations/session/cs_nonexistent")
        assert resp.status_code == 404


class TestStripeWebhook:

    async def test_webhook_not_configured(self, client, monkeypatch):
        """Returns 400 if webhook secret not configured."""
        monkeypatch.setattr("app.config.settings.stripe_webhook_secret", "")
        resp = await client.post(
            "/stripe/webhook",
            content=b"{}",
            headers={"stripe-signature": "t=1,v1=sig"},
        )
        assert resp.status_code == 400

    async def test_webhook_invalid_signature(self, client, monkeypatch):
        """Invalid signature is rejected."""
        monkeypatch.setattr("app.config.settings.stripe_webhook_secret", "whsec_test123")

        with patch("app.routers.stripe_webhook.stripe") as mock_stripe:
            # Set the exception class first, then use it as side_effect
            mock_stripe.SignatureVerificationError = type(
                "SignatureVerificationError", (Exception,), {}
            )
            mock_stripe.Webhook.construct_event.side_effect = (
                mock_stripe.SignatureVerificationError("bad sig")
            )

            resp = await client.post(
                "/stripe/webhook",
                content=b'{"type":"test"}',
                headers={"stripe-signature": "t=123,v1=invalidsig"},
            )
        assert resp.status_code == 400

    async def test_webhook_completed_updates_status(
        self, client, seed_donation, db_session, monkeypatch
    ):
        """checkout.session.completed updates donation to succeeded."""
        monkeypatch.setattr("app.config.settings.stripe_webhook_secret", "whsec_test123")

        event_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": seed_donation.stripe_session_id,
                    "payment_intent": "pi_test_xyz",
                }
            },
        }

        with patch("app.routers.stripe_webhook.stripe") as mock_stripe:
            mock_stripe.Webhook.construct_event.return_value = event_data
            mock_stripe.SignatureVerificationError = Exception

            resp = await client.post(
                "/stripe/webhook",
                content=json.dumps(event_data).encode(),
                headers={"stripe-signature": "t=123,v1=validsig"},
            )

        assert resp.status_code == 200
        await db_session.refresh(seed_donation)
        assert seed_donation.status == "succeeded"
        assert seed_donation.stripe_payment_intent_id == "pi_test_xyz"

    async def test_webhook_expired_updates_status(
        self, client, seed_donation, db_session, monkeypatch
    ):
        """checkout.session.expired updates donation to cancelled."""
        monkeypatch.setattr("app.config.settings.stripe_webhook_secret", "whsec_test123")

        event_data = {
            "type": "checkout.session.expired",
            "data": {
                "object": {
                    "id": seed_donation.stripe_session_id,
                }
            },
        }

        with patch("app.routers.stripe_webhook.stripe") as mock_stripe:
            mock_stripe.Webhook.construct_event.return_value = event_data
            mock_stripe.SignatureVerificationError = Exception

            resp = await client.post(
                "/stripe/webhook",
                content=json.dumps(event_data).encode(),
                headers={"stripe-signature": "t=123,v1=validsig"},
            )

        assert resp.status_code == 200
        await db_session.refresh(seed_donation)
        assert seed_donation.status == "cancelled"
