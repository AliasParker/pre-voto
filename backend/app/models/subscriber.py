# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Subscriber(Base):
    __tablename__ = "subscribers"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(2))
    language: Mapped[str] = mapped_column(String, server_default=text("'es'"))
    beehiiv_id: Mapped[str | None] = mapped_column()
    source: Mapped[str | None] = mapped_column()
    status: Mapped[str] = mapped_column(String, server_default=text("'pending'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
