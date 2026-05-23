# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

# PostgreSQL enum types — must match migration 0004
ConfidenceLevel = Enum("high", "medium", "low", name="confidence_level", create_type=False)
SourceType = Enum(
    "plan_oficial", "entrevista", "cuenta_oficial", "trayectoria", "inferencia",
    name="source_type", create_type=False,
)


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
    coded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[str | None] = mapped_column()

    # Fase 8 additions
    confidence: Mapped[str | None] = mapped_column(ConfidenceLevel)
    source_type: Mapped[str | None] = mapped_column(SourceType)

    # relationships
    candidate: Mapped["Candidate"] = relationship(back_populates="positions")  # noqa: F821
    statement: Mapped["Statement"] = relationship(back_populates="positions")  # noqa: F821
