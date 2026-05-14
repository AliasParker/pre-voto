import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PollOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pollster: str
    field_start: date
    field_end: date
    sample_size: int | None = None
    methodology: str | None = None
    results: dict
    source_url: str | None = None
    created_at: datetime


class PollAverageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    computed_at: datetime
    results: dict
    polls_included: int | None = None


class PollCreate(BaseModel):
    election_id: uuid.UUID
    pollster: str
    field_start: date
    field_end: date
    sample_size: int | None = None
    methodology: str | None = None
    results: dict
    source_url: str | None = None
