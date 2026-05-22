"""Create usage_events table for custom quiz tracking.

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usage_events",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("session_hash", sa.String(64), nullable=False),
        sa.Column("statement_id", sa.Uuid(), nullable=True),
        sa.Column("position_value", sa.SmallInteger(), nullable=True),
        sa.Column("top_match_slug", sa.String(100), nullable=True),
        sa.Column("top_match_pct", sa.Numeric(4, 1), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("share_channel", sa.String(20), nullable=True),
        sa.Column("country", sa.String(2), server_default="co", nullable=False),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usage_events")),
    )
    op.create_index(op.f("ix_usage_events_event_type"), "usage_events", ["event_type"])
    op.create_index(op.f("ix_usage_events_session_hash"), "usage_events", ["session_hash"])
    op.create_index(op.f("ix_usage_events_timestamp"), "usage_events", ["timestamp"])


def downgrade() -> None:
    op.drop_index(op.f("ix_usage_events_timestamp"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_session_hash"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_event_type"), table_name="usage_events")
    op.drop_table("usage_events")
