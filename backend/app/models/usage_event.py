import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    event_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    session_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    statement_id: Mapped[uuid.UUID | None] = mapped_column()
    position_value: Mapped[int | None] = mapped_column(SmallInteger)
    top_match_slug: Mapped[str | None] = mapped_column(String(100))
    top_match_pct: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    share_channel: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(2), server_default="co", nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB)
