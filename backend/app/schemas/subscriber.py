# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class SubscriberCreate(BaseModel):
    email: EmailStr
    country_code: str | None = None
    source: str | None = None
    # Quiz result fields (optional — only set when subscribing post-quiz)
    top_match_name: str | None = None
    top_match_pct: int | None = None
    result_url: str | None = None


class SubscriberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    country_code: str | None = None
    status: str
    created_at: datetime
