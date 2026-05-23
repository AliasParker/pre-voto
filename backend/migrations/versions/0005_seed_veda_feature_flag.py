# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
"""Seed quiz_disabled_during_veda feature flag for Colombia.

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-20

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO feature_flags (id, key, value, enabled, country_scope)
        VALUES (
            gen_random_uuid(),
            'quiz_disabled_during_veda',
            'Pauses quiz during election day voting hours',
            false,
            'co'
        )
        ON CONFLICT (key, country_scope) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM feature_flags
        WHERE key = 'quiz_disabled_during_veda' AND country_scope = 'co';
        """
    )
