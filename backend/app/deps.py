# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
from fastapi import Depends, Header, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.db import get_db
from app.models.country import Country
from app.models.election import Election


async def require_admin(x_admin_key: str = Header()) -> str:
    if not x_admin_key:
        raise HTTPException(status_code=401, detail="Missing X-Admin-Key header")
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    return x_admin_key


async def get_country_with_election(
    country: str = Path(),
    db: AsyncSession = Depends(get_db),
) -> tuple[Country, Election]:
    result = await db.execute(
        select(Country)
        .options(selectinload(Country.elections))
        .where(Country.code == country.lower(), Country.is_active.is_(True))
    )
    country_obj = result.scalar_one_or_none()
    if not country_obj:
        raise HTTPException(status_code=404, detail="Country not found")

    election = next(
        (e for e in country_obj.elections if e.is_active),
        None,
    )
    if not election:
        raise HTTPException(status_code=404, detail="No active election for this country")

    return country_obj, election
