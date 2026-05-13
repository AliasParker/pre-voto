import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    country_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("countries.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    feed_url: Mapped[str] = mapped_column(unique=True, nullable=False)
    site_url: Mapped[str | None] = mapped_column()
    last_pulled_at: Mapped[datetime | None] = mapped_column()
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationships
    country: Mapped["Country"] = relationship(back_populates="sources")  # noqa: F821
    news_items: Mapped[list["NewsItem"]] = relationship(back_populates="source")  # noqa: F821
