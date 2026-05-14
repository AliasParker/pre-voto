import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class NewsletterSend(Base):
    __tablename__ = "newsletter_sends"
    __table_args__ = (
        CheckConstraint(
            "status IN ('sent', 'dry_run', 'failed')",
            name="status_valid",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    country_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("countries.id"), nullable=False
    )
    subject: Mapped[str] = mapped_column(nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    recipient_count: Mapped[int] = mapped_column(Integer, nullable=False)
    beehiiv_broadcast_id: Mapped[str | None] = mapped_column()
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # relationships
    country: Mapped["Country"] = relationship()  # noqa: F821
