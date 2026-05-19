import uuid

from sqlalchemy import Boolean, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class FeatureFlag(TimestampMixin, Base):
    __tablename__ = "feature_flags"
    __table_args__ = (
        UniqueConstraint("key", "country_scope", name="uq_feature_flags_key_country"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    key: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[str | None] = mapped_column()
    enabled: Mapped[bool] = mapped_column(Boolean, server_default="false")
    country_scope: Mapped[str | None] = mapped_column(String(2))
