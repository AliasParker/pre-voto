# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
"""add newsletter_sends table

Revision ID: 0002
Revises: 0001
Create Date: 2025-05-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "newsletter_sends",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("country_id", sa.Uuid(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("recipient_count", sa.Integer(), nullable=False),
        sa.Column("beehiiv_broadcast_id", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"], name=op.f("fk_newsletter_sends_country_id_countries")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_newsletter_sends")),
        sa.CheckConstraint("status IN ('sent', 'dry_run', 'failed')", name=op.f("ck_newsletter_sends_status_valid")),
    )
    op.create_index(op.f("ix_newsletter_sends_country_id"), "newsletter_sends", ["country_id"])


def downgrade() -> None:
    op.drop_table("newsletter_sends")
