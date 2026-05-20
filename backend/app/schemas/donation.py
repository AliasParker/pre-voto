from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class DonationCreateRequest(BaseModel):
    amount_usd: float

    @field_validator("amount_usd")
    @classmethod
    def amount_must_be_at_least_one(cls, v: float) -> float:
        if v < 1:
            raise ValueError("Amount must be at least $1 USD")
        if v > 10000:
            raise ValueError("Amount cannot exceed $10,000 USD")
        return v


class DonationCreateResponse(BaseModel):
    checkout_url: str
    session_id: str


class DonationStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amount_cents: int
    currency: str
    status: str
    newsletter_opt_in: bool
    created_at: datetime


class NewsletterOptInRequest(BaseModel):
    opt_in: bool = True
