# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
"""Make donation email nullable (email comes from Stripe webhook, not creation).

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-20

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("donations", "email", nullable=True)


def downgrade() -> None:
    op.execute("UPDATE donations SET email = '' WHERE email IS NULL")
    op.alter_column("donations", "email", nullable=False)
