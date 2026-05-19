import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Candidate(TimestampMixin, Base):
    __tablename__ = "candidates"
    __table_args__ = (
        UniqueConstraint("election_id", "slug"),
        CheckConstraint(
            r"color ~ '^#[0-9A-Fa-f]{6}$'",
            name="color_hex_format",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id"), nullable=False
    )
    slug: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    party: Mapped[str | None] = mapped_column()
    party_acronym: Mapped[str | None] = mapped_column()
    bio_short: Mapped[str | None] = mapped_column()
    photo_url: Mapped[str | None] = mapped_column()
    photo_author: Mapped[str | None] = mapped_column()
    photo_license: Mapped[str | None] = mapped_column()
    photo_attribution: Mapped[str | None] = mapped_column()
    color: Mapped[str | None] = mapped_column(String(7))
    is_demo: Mapped[bool] = mapped_column(Boolean, server_default="false")
    sources: Mapped[dict | list] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))

    # Fase 8 additions
    ballot_position: Mapped[int | None] = mapped_column(Integer)
    running_mate: Mapped[str | None] = mapped_column()
    coalition: Mapped[str | None] = mapped_column()
    positioning: Mapped[str | None] = mapped_column()
    age: Mapped[int | None] = mapped_column(Integer)
    plan_url: Mapped[str | None] = mapped_column()
    high_confidence_pct: Mapped[int | None] = mapped_column(Integer)
    withdrawn: Mapped[bool] = mapped_column(Boolean, server_default="false")
    withdrawn_date: Mapped[date | None] = mapped_column(Date)
    endorses: Mapped[str | None] = mapped_column()

    # relationships
    election: Mapped["Election"] = relationship(back_populates="candidates")  # noqa: F821
    positions: Mapped[list["CandidatePosition"]] = relationship(back_populates="candidate")  # noqa: F821
    quiz_completions: Mapped[list["QuizCompletion"]] = relationship(back_populates="top_match_candidate")  # noqa: F821
