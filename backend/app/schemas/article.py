import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    dek: str | None = None
    hero_image_url: str | None = None
    author: str | None = None
    tags: list[str] | None = None
    published_at: datetime | None = None


class ArticleDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    dek: str | None = None
    body_markdown: str
    hero_image_url: str | None = None
    hero_image_attribution: str | None = None
    author: str | None = None
    tags: list[str] | None = None
    published_at: datetime | None = None


class ArticleCreate(BaseModel):
    country_id: uuid.UUID
    slug: str
    title: str
    dek: str | None = None
    body_markdown: str
    hero_image_url: str | None = None
    hero_image_attribution: str | None = None
    author: str | None = None
    tags: list[str] | None = None
    published_at: datetime | None = None
