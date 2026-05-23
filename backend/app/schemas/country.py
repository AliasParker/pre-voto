# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ElectionBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    election_date: date
    description: str | None = None
    is_active: bool


class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    language: str
    is_active: bool
    next_election: ElectionBrief | None = None


class CountryDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    language: str
    is_active: bool
    elections: list[ElectionBrief] = []
