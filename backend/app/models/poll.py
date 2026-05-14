import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id"), nullable=False
    )
    pollster: Mapped[str] = mapped_column(nullable=False)
    field_start: Mapped[date] = mapped_column(Date, nullable=False)
    field_end: Mapped[date] = mapped_column(Date, nullable=False)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    methodology: Mapped[str | None] = mapped_column()
    results: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_url: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # relationships
    election: Mapped["Election"] = relationship(back_populates="polls")  # noqa: F821
