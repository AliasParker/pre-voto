import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Donation(TimestampMixin, Base):
    __tablename__ = "donations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    email: Mapped[str] = mapped_column(nullable=False)
    amount_cents: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), server_default="usd")
    stripe_session_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column()
    status: Mapped[str] = mapped_column(
        String(20), server_default="pending"
    )  # pending, succeeded, failed, cancelled
    newsletter_opt_in: Mapped[bool] = mapped_column(
        Boolean, server_default="false"
    )
    country_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("countries.id"), nullable=True
    )
