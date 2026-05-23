# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
from fastapi import APIRouter, Query

from app.services.veda import is_quiz_disabled

router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])


@router.get("/quiz-status")
async def quiz_status(country: str = Query(min_length=2, max_length=2)):
    disabled = is_quiz_disabled(country.lower())
    return {"quiz_disabled": disabled}
