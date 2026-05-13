import uuid

from pydantic import BaseModel


class StatementCreate(BaseModel):
    election_id: uuid.UUID
    text: str
    category: str | None = None
    weight: int = 1
    display_order: int | None = None
