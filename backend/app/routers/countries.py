# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.country import Country
from app.models.election import Election
from app.schemas.country import CountryDetail, CountryOut, ElectionBrief

router = APIRouter(prefix="/countries", tags=["countries"])


@router.get("", response_model=list[CountryOut])
async def list_countries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Country)
        .options(selectinload(Country.elections))
        .where(Country.is_active.is_(True))
        .order_by(Country.name)
    )
    countries = result.scalars().all()

    out = []
    for c in countries:
        active_election = next((e for e in c.elections if e.is_active), None)
        country_out = CountryOut(
            id=c.id,
            code=c.code,
            name=c.name,
            language=c.language,
            is_active=c.is_active,
            next_election=ElectionBrief.model_validate(active_election) if active_election else None,
        )
        out.append(country_out)
    return out


@router.get("/{code}", response_model=CountryDetail)
async def get_country(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Country)
        .options(selectinload(Country.elections))
        .where(Country.code == code.lower(), Country.is_active.is_(True))
    )
    country = result.scalar_one_or_none()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    return CountryDetail(
        id=country.id,
        code=country.code,
        name=country.name,
        language=country.language,
        is_active=country.is_active,
        elections=[ElectionBrief.model_validate(e) for e in country.elections],
    )
