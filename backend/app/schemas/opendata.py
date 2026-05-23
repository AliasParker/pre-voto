"""Schemas for public open-data API endpoints."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class OpenDataStatement(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str | None = None
    text: str
    category: str | None = None
    short_label: str | None = None
    weight: int = 1
    display_order: int | None = None


class OpenDataCandidate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name: str
    party: str | None = None
    party_acronym: str | None = None
    coalition: str | None = None
    bio_short: str | None = None
    photo_url: str | None = None
    color: str | None = None
    ballot_position: int | None = None
    positioning: str | None = None
    high_confidence_pct: int | None = None
    withdrawn: bool = False
    withdrawn_date: date | None = None
    endorses: str | None = None


class OpenDataPosition(BaseModel):
    candidate_slug: str
    candidate_name: str
    statement_slug: str | None
    statement_text: str
    statement_category: str | None
    value: int
    value_label: str
    confidence: str | None
    source_type: str | None
    source_quote: str | None
    source_url: str | None
    source_date: date | None
