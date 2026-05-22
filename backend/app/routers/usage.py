"""Usage tracking endpoints.

- POST /usage/event — ingest quiz usage events (anonymous, rate-limited)
- GET /admin/usage/summary — aggregated stats (HTTP Basic Auth)
"""

import hashlib
import secrets
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.limiter import _get_remote_ip
from app.models.usage_event import UsageEvent

log = structlog.get_logger()

router = APIRouter(prefix="/usage", tags=["usage"])
admin_usage_router = APIRouter(prefix="/admin/usage", tags=["admin"])

security = HTTPBasic()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class EventType(str, Enum):
    question_viewed = "question_viewed"
    question_answered = "question_answered"
    quiz_started = "quiz_started"
    quiz_completed = "quiz_completed"
    share_clicked = "share_clicked"


class UsageEventIn(BaseModel):
    event_type: EventType
    statement_id: str | None = None
    position_value: int | None = Field(None, ge=-2, le=2)
    top_match_slug: str | None = None
    top_match_pct: float | None = Field(None, ge=0, le=100)
    duration_seconds: int | None = Field(None, ge=0)
    share_channel: Literal["whatsapp", "x", "telegram", "copy_link"] | None = None
    country: str = Field("co", min_length=2, max_length=2)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_session_hash(ip: str, user_agent: str) -> str:
    """One-way hash of IP + user-agent + UTC day + salt. Not reversible."""
    day_str = date.today().isoformat()
    raw = f"{ip}{user_agent}{day_str}{settings.session_hash_salt}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def _check_rate_limit(session_hash: str, db: AsyncSession) -> bool:
    """Return True if the session has exceeded 100 events in the last minute."""
    one_min_ago = func.now() - text("interval '1 minute'")
    result = await db.execute(
        select(func.count())
        .select_from(UsageEvent)
        .where(
            UsageEvent.session_hash == session_hash,
            UsageEvent.timestamp >= one_min_ago,
        )
    )
    count = result.scalar() or 0
    return count >= 100


def _verify_admin(credentials: HTTPBasicCredentials) -> None:
    """Verify HTTP Basic Auth credentials against settings."""
    correct_user = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        settings.admin_user.encode("utf-8"),
    )
    correct_pass = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        settings.admin_pass.encode("utf-8"),
    )
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


# ---------------------------------------------------------------------------
# POST /usage/event
# ---------------------------------------------------------------------------

@router.post("/event", status_code=204)
async def ingest_event(
    body: UsageEventIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    ip = _get_remote_ip(request)
    ua = request.headers.get("user-agent", "")
    session_hash = _compute_session_hash(ip, ua)

    # Rate limit: 100 events per session per minute
    if await _check_rate_limit(session_hash, db):
        raise HTTPException(status_code=429, detail="Too many events")

    # Parse statement_id as UUID if provided
    statement_uuid = None
    if body.statement_id:
        try:
            import uuid
            statement_uuid = uuid.UUID(body.statement_id)
        except ValueError:
            pass  # ignore invalid UUIDs

    event = UsageEvent(
        event_type=body.event_type.value,
        session_hash=session_hash,
        statement_id=statement_uuid,
        position_value=body.position_value,
        top_match_slug=body.top_match_slug,
        top_match_pct=Decimal(str(body.top_match_pct)) if body.top_match_pct is not None else None,
        duration_seconds=body.duration_seconds,
        share_channel=body.share_channel,
        country=body.country.lower(),
    )
    db.add(event)
    await db.commit()

    return Response(status_code=204)


# ---------------------------------------------------------------------------
# GET /admin/usage/summary
# ---------------------------------------------------------------------------

@admin_usage_router.get("/summary")
async def usage_summary(
    credentials: HTTPBasicCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    country: str | None = Query(None, min_length=2, max_length=2),
) -> dict:
    _verify_admin(credentials)

    # Build base filter conditions
    conditions = []
    if from_date:
        conditions.append(UsageEvent.timestamp >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        conditions.append(UsageEvent.timestamp < datetime.combine(to_date, datetime.max.time()))
    if country:
        conditions.append(UsageEvent.country == country.lower())

    def with_conditions(stmt):
        for c in conditions:
            stmt = stmt.where(c)
        return stmt

    # 1. Total quiz_started
    q = with_conditions(
        select(func.count()).select_from(UsageEvent)
        .where(UsageEvent.event_type == "quiz_started")
    )
    total_started = (await db.execute(q)).scalar() or 0

    # 2. Total quiz_completed
    q = with_conditions(
        select(func.count()).select_from(UsageEvent)
        .where(UsageEvent.event_type == "quiz_completed")
    )
    total_completed = (await db.execute(q)).scalar() or 0

    # 3. Completion rate
    completion_rate = round((total_completed / total_started * 100), 1) if total_started > 0 else 0

    # 4. Abandonment by question
    q_viewed = with_conditions(
        select(
            UsageEvent.statement_id,
            func.count().label("count_arrived"),
        )
        .where(UsageEvent.event_type == "question_viewed")
        .where(UsageEvent.statement_id.isnot(None))
        .group_by(UsageEvent.statement_id)
    )
    viewed_rows = (await db.execute(q_viewed)).all()
    viewed_map = {str(r.statement_id): r.count_arrived for r in viewed_rows}

    q_answered = with_conditions(
        select(
            UsageEvent.statement_id,
            func.count().label("count_answered"),
        )
        .where(UsageEvent.event_type == "question_answered")
        .where(UsageEvent.statement_id.isnot(None))
        .group_by(UsageEvent.statement_id)
    )
    answered_rows = (await db.execute(q_answered)).all()
    answered_map = {str(r.statement_id): r.count_answered for r in answered_rows}

    all_stmt_ids = set(viewed_map.keys()) | set(answered_map.keys())
    abandonment = []
    for sid in sorted(all_stmt_ids):
        arrived = viewed_map.get(sid, 0)
        answered = answered_map.get(sid, 0)
        abandonment.append({
            "statement_id": sid,
            "count_arrived": arrived,
            "count_answered": answered,
            "count_abandoned": max(0, arrived - answered),
        })

    # 5. Response distribution per statement
    q_dist = with_conditions(
        select(
            UsageEvent.statement_id,
            UsageEvent.position_value,
            func.count().label("cnt"),
        )
        .where(UsageEvent.event_type == "question_answered")
        .where(UsageEvent.statement_id.isnot(None))
        .where(UsageEvent.position_value.isnot(None))
        .group_by(UsageEvent.statement_id, UsageEvent.position_value)
    )
    dist_rows = (await db.execute(q_dist)).all()
    dist_map: dict[str, dict[str, int]] = {}
    for r in dist_rows:
        sid = str(r.statement_id)
        if sid not in dist_map:
            dist_map[sid] = {"-2": 0, "-1": 0, "0": 0, "1": 0, "2": 0}
        dist_map[sid][str(r.position_value)] = r.cnt

    response_distribution = [
        {"statement_id": sid, "distribution": dist}
        for sid, dist in sorted(dist_map.items())
    ]

    # 6. Top matches (top 12 by frequency)
    q_matches = with_conditions(
        select(
            UsageEvent.top_match_slug,
            func.count().label("cnt"),
        )
        .where(UsageEvent.event_type == "quiz_completed")
        .where(UsageEvent.top_match_slug.isnot(None))
        .group_by(UsageEvent.top_match_slug)
        .order_by(func.count().desc())
        .limit(12)
    )
    match_rows = (await db.execute(q_matches)).all()
    top_matches = [
        {"slug": r.top_match_slug, "count": r.cnt}
        for r in match_rows
    ]

    # 7. Average duration
    q_dur = with_conditions(
        select(func.avg(UsageEvent.duration_seconds))
        .where(UsageEvent.event_type == "quiz_completed")
        .where(UsageEvent.duration_seconds.isnot(None))
    )
    avg_duration = (await db.execute(q_dur)).scalar()
    avg_duration_seconds = round(float(avg_duration), 1) if avg_duration else 0

    # 8. Shares by channel
    q_shares = with_conditions(
        select(
            UsageEvent.share_channel,
            func.count().label("cnt"),
        )
        .where(UsageEvent.event_type == "share_clicked")
        .where(UsageEvent.share_channel.isnot(None))
        .group_by(UsageEvent.share_channel)
    )
    share_rows = (await db.execute(q_shares)).all()
    shares_by_channel = {
        "whatsapp": 0, "x": 0, "telegram": 0, "copy_link": 0,
    }
    for r in share_rows:
        if r.share_channel in shares_by_channel:
            shares_by_channel[r.share_channel] = r.cnt

    return {
        "total_quiz_started": total_started,
        "total_quiz_completed": total_completed,
        "completion_rate": completion_rate,
        "abandonment_by_question": abandonment,
        "response_distribution": response_distribution,
        "top_matches": top_matches,
        "average_duration_seconds": avg_duration_seconds,
        "shares_by_channel": shares_by_channel,
    }
