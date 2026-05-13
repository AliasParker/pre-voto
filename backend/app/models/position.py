import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CandidatePosition(TimestampMixin, Base):
    __tablename__ = "candidate_positions"
    __table_args__ = (
        UniqueConstraint("candidate_id", "statement_id"),
        CheckConstraint("value BETWEEN -2 AND 2", name="value_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidates.id"), nullable=False
    )
    statement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("statements.id"), nullable=False
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    source_quote: Mapped[str | None] = mapped_column()
    source_url: Mapped[str | None] = mapped_column()
    source_date: Mapped[date | None] = mapped_column(Date)
    coded_by: Mapped[str | None] = mapped_column()
    coded_at: Mapped[datetime | None] = mapped_column(server_default=func.now())
    notes: Mapped[str | None] = mapped_column()

    # relationships
    candidate: Mapped["Candidate"] = relationship(back_populates="positions")  # noqa: F821
    statement: Mapped["Statement"] = relationship(back_populates="positions")  # noqa: F821
