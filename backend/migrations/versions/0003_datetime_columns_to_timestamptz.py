"""convert datetime columns from timestamp to timestamptz

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-14

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All (table, column) pairs that need TIMESTAMP -> TIMESTAMPTZ conversion.
COLUMNS = [
    # TimestampMixin tables (created_at + updated_at)
    ("countries", "created_at"),
    ("countries", "updated_at"),
    ("elections", "created_at"),
    ("elections", "updated_at"),
    ("candidates", "created_at"),
    ("candidates", "updated_at"),
    ("statements", "created_at"),
    ("statements", "updated_at"),
    ("candidate_positions", "created_at"),
    ("candidate_positions", "updated_at"),
    ("articles", "created_at"),
    ("articles", "updated_at"),
    # Article-specific
    ("articles", "published_at"),
    ("articles", "deleted_at"),
    # news_items (append-only)
    ("news_items", "published_at"),
    ("news_items", "fetched_at"),
    # polls (append-only)
    ("polls", "created_at"),
    ("polls", "deleted_at"),
    # poll_averages (append-only)
    ("poll_averages", "computed_at"),
    # candidate_positions extra
    ("candidate_positions", "coded_at"),
    # quiz_completions (append-only)
    ("quiz_completions", "completed_at"),
    # sources (append-only)
    ("sources", "last_pulled_at"),
    ("sources", "created_at"),
    # subscribers (append-only)
    ("subscribers", "created_at"),
    # newsletter_sends (append-only)
    ("newsletter_sends", "sent_at"),
    ("newsletter_sends", "created_at"),
]


def upgrade() -> None:
    for table, column in COLUMNS:
        op.execute(
            f'ALTER TABLE {table} ALTER COLUMN {column} '
            f"TYPE TIMESTAMPTZ USING {column} AT TIME ZONE 'UTC'"
        )


def downgrade() -> None:
    for table, column in COLUMNS:
        op.execute(
            f'ALTER TABLE {table} ALTER COLUMN {column} '
            f"TYPE TIMESTAMP WITHOUT TIME ZONE "
            f"USING {column} AT TIME ZONE 'UTC'"
        )
