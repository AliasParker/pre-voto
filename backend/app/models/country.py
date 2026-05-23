# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Country(TimestampMixin, Base):
    __tablename__ = "countries"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    language: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # relationships
    elections: Mapped[list["Election"]] = relationship(back_populates="country")  # noqa: F821
    articles: Mapped[list["Article"]] = relationship(back_populates="country")  # noqa: F821
    sources: Mapped[list["Source"]] = relationship(back_populates="country")  # noqa: F821
    news_items: Mapped[list["NewsItem"]] = relationship(back_populates="country")  # noqa: F821
