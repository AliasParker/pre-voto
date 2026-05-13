import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Election(TimestampMixin, Base):
    __tablename__ = "elections"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    country_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("countries.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(nullable=False)
    election_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column()
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # relationships
    country: Mapped["Country"] = relationship(back_populates="elections")  # noqa: F821
    candidates: Mapped[list["Candidate"]] = relationship(back_populates="election")  # noqa: F821
    statements: Mapped[list["Statement"]] = relationship(back_populates="election")  # noqa: F821
    polls: Mapped[list["Poll"]] = relationship(back_populates="election")  # noqa: F821
    poll_averages: Mapped[list["PollAverage"]] = relationship(back_populates="election")  # noqa: F821
    quiz_completions: Mapped[list["QuizCompletion"]] = relationship(back_populates="election")  # noqa: F821
