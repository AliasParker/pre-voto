import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id"), nullable=False
    )
    country_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("countries.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(unique=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    snippet: Mapped[str | None] = mapped_column()
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String, server_default=text("'raw'"))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # relationships
    source: Mapped["Source"] = relationship(back_populates="news_items")  # noqa: F821
    country: Mapped["Country"] = relationship(back_populates="news_items")  # noqa: F821
