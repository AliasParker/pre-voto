# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PollAverage(Base):
    __tablename__ = "poll_averages"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id"), nullable=False
    )
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    results: Mapped[dict] = mapped_column(JSONB, nullable=False)
    polls_included: Mapped[int | None] = mapped_column(Integer)

    # relationships
    election: Mapped["Election"] = relationship(back_populates="poll_averages")  # noqa: F821
