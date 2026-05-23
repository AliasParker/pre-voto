# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    party: str | None = None
    party_acronym: str | None = None
    coalition: str | None = None
    bio_short: str | None = None
    photo_url: str | None = None
    color: str | None = None
    ballot_position: int | None = None
    running_mate: str | None = None
    positioning: str | None = None
    high_confidence_pct: int | None = None
    withdrawn: bool = False


class PositionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    statement_id: uuid.UUID
    value: int
    source_quote: str | None = None
    source_url: str | None = None
    source_date: date | None = None
    confidence: str | None = None
    source_type: str | None = None
    notes: str | None = None


class CandidateDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    party: str | None = None
    party_acronym: str | None = None
    coalition: str | None = None
    bio_short: str | None = None
    photo_url: str | None = None
    photo_author: str | None = None
    photo_license: str | None = None
    photo_attribution: str | None = None
    color: str | None = None
    sources: dict | list = []
    positions: list[PositionOut] = []
    ballot_position: int | None = None
    running_mate: str | None = None
    positioning: str | None = None
    age: int | None = None
    plan_url: str | None = None
    high_confidence_pct: int | None = None
    withdrawn: bool = False
    withdrawn_date: date | None = None
    endorses: str | None = None


class CandidateCreate(BaseModel):
    election_id: uuid.UUID
    slug: str
    name: str
    party: str | None = None
    party_acronym: str | None = None
    coalition: str | None = None
    bio_short: str | None = None
    photo_url: str | None = None
    color: str | None = None


class CandidateUpdate(BaseModel):
    name: str | None = None
    party: str | None = None
    party_acronym: str | None = None
    coalition: str | None = None
    bio_short: str | None = None
    photo_url: str | None = None
    photo_author: str | None = None
    photo_license: str | None = None
    photo_attribution: str | None = None
    color: str | None = None


class BulkPositionItem(BaseModel):
    statement_id: uuid.UUID
    value: int
    source_quote: str | None = None
    source_url: str | None = None
    source_date: date | None = None
    coded_by: str | None = None
    notes: str | None = None


class BulkPositionRequest(BaseModel):
    positions: list[BulkPositionItem]
