"""fase 8 schema additions: candidates, statements, positions, feature_flags

Add missing columns for Colombia 2026 real data import:
- candidates: ballot_position, running_mate, coalition, positioning, age,
  plan_url, high_confidence_pct, withdrawn, withdrawn_date, endorses
- statements: slug, short_label
- candidate_positions: confidence (enum), source_type (enum)
- New table: feature_flags

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# PostgreSQL enum types
confidence_level = sa.Enum("high", "medium", "low", name="confidence_level")
source_type_enum = sa.Enum(
    "plan_oficial", "entrevista", "cuenta_oficial", "trayectoria", "inferencia",
    name="source_type",
)


def upgrade() -> None:
    # -- Create enum types --
    confidence_level.create(op.get_bind(), checkfirst=True)
    source_type_enum.create(op.get_bind(), checkfirst=True)

    # -- candidates: add new columns --
    op.add_column("candidates", sa.Column("ballot_position", sa.Integer(), nullable=True))
    op.add_column("candidates", sa.Column("running_mate", sa.String(), nullable=True))
    op.add_column("candidates", sa.Column("coalition", sa.String(), nullable=True))
    op.add_column("candidates", sa.Column("positioning", sa.String(), nullable=True))
    op.add_column("candidates", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column("candidates", sa.Column("plan_url", sa.String(), nullable=True))
    op.add_column("candidates", sa.Column("high_confidence_pct", sa.Integer(), nullable=True))
    op.add_column(
        "candidates",
        sa.Column("withdrawn", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column("candidates", sa.Column("withdrawn_date", sa.Date(), nullable=True))
    op.add_column("candidates", sa.Column("endorses", sa.String(), nullable=True))

    # -- statements: add slug and short_label --
    op.add_column("statements", sa.Column("slug", sa.String(), nullable=True))
    op.add_column("statements", sa.Column("short_label", sa.String(), nullable=True))

    # -- candidate_positions: add confidence and source_type --
    op.add_column(
        "candidate_positions",
        sa.Column("confidence", confidence_level, nullable=True),
    )
    op.add_column(
        "candidate_positions",
        sa.Column("source_type", source_type_enum, nullable=True),
    )

    # -- feature_flags: create table --
    op.create_table(
        "feature_flags",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("country_scope", sa.String(2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_feature_flags"),
        sa.UniqueConstraint("key", "country_scope", name="uq_feature_flags_key_country"),
    )


def downgrade() -> None:
    # -- feature_flags: drop table --
    op.drop_table("feature_flags")

    # -- candidate_positions: drop columns --
    op.drop_column("candidate_positions", "source_type")
    op.drop_column("candidate_positions", "confidence")

    # -- statements: drop columns --
    op.drop_column("statements", "short_label")
    op.drop_column("statements", "slug")

    # -- candidates: drop columns --
    op.drop_column("candidates", "endorses")
    op.drop_column("candidates", "withdrawn_date")
    op.drop_column("candidates", "withdrawn")
    op.drop_column("candidates", "high_confidence_pct")
    op.drop_column("candidates", "plan_url")
    op.drop_column("candidates", "age")
    op.drop_column("candidates", "positioning")
    op.drop_column("candidates", "coalition")
    op.drop_column("candidates", "running_mate")
    op.drop_column("candidates", "ballot_position")

    # -- Drop enum types --
    source_type_enum.drop(op.get_bind(), checkfirst=True)
    confidence_level.drop(op.get_bind(), checkfirst=True)
