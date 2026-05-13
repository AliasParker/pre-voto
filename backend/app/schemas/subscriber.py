import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class SubscriberCreate(BaseModel):
    email: EmailStr
    country_code: str | None = None
    source: str | None = None


class SubscriberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    country_code: str | None = None
    status: str
    created_at: datetime
