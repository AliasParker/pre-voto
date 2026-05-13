import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class QuizCompletion(Base):
    __tablename__ = "quiz_completions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id"), nullable=False
    )
    session_hash: Mapped[str | None] = mapped_column()
    statements_answered: Mapped[int | None] = mapped_column(Integer)
    top_match_candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("candidates.id")
    )
    top_match_pct: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    completed_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationships
    election: Mapped["Election"] = relationship(back_populates="quiz_completions")  # noqa: F821
    top_match_candidate: Mapped["Candidate | None"] = relationship(back_populates="quiz_completions")  # noqa: F821
