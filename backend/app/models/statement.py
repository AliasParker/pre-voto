import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


class Statement(TimestampMixin, Base):
    __tablename__ = "statements"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id"), nullable=False
    )
    slug: Mapped[str | None] = mapped_column()
    text: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str | None] = mapped_column()
    short_label: Mapped[str | None] = mapped_column()
    weight: Mapped[int] = mapped_column(
        Integer, server_default="1"
    )
    display_order: Mapped[int | None] = mapped_column(Integer)
    embedding = mapped_column(Vector(1536), nullable=True) if Vector else None
    is_demo: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # constraints
    __table_args__ = (
        CheckConstraint("weight BETWEEN 1 AND 3", name="weight_range"),
    )

    # relationships
    election: Mapped["Election"] = relationship(back_populates="statements")  # noqa: F821
    positions: Mapped[list["CandidatePosition"]] = relationship(back_populates="statement")  # noqa: F821
