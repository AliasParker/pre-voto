import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


class Article(TimestampMixin, Base):
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("country_id", "slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    country_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("countries.id"), nullable=False
    )
    slug: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    dek: Mapped[str | None] = mapped_column()
    body_markdown: Mapped[str] = mapped_column(nullable=False)
    hero_image_url: Mapped[str | None] = mapped_column()
    hero_image_attribution: Mapped[str | None] = mapped_column()
    author: Mapped[str | None] = mapped_column()
    tags = mapped_column(ARRAY(TEXT), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column()
    deleted_at: Mapped[datetime | None] = mapped_column()
    embedding = mapped_column(Vector(1536), nullable=True) if Vector else None
    is_demo: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # relationships
    country: Mapped["Country"] = relationship(back_populates="articles")  # noqa: F821
