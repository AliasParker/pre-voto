# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import uuid

from pydantic import BaseModel


class StatementCreate(BaseModel):
    election_id: uuid.UUID
    text: str
    category: str | None = None
    slug: str | None = None
    short_label: str | None = None
    weight: int = 1
    display_order: int | None = None
