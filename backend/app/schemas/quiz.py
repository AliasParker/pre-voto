import uuid

from pydantic import BaseModel, ConfigDict


class StatementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    text: str
    category: str | None = None
    slug: str | None = None
    short_label: str | None = None
    weight: int
    display_order: int | None = None


class QuizSubmitRequest(BaseModel):
    answers: dict[uuid.UUID, int | None]


class CandidateAffinity(BaseModel):
    candidate_id: uuid.UUID
    slug: str
    name: str
    party: str | None = None
    party_acronym: str | None = None
    coalition: str | None = None
    photo_url: str | None = None
    color: str | None = None
    affinity: float
    affinity_high_confidence: float | None = None
    high_confidence_pct: int | None = None
    running_mate: str | None = None
    ballot_position: int | None = None


class QuizResult(BaseModel):
    results: list[CandidateAffinity]
    statements_answered: int
