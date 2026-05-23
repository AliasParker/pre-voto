# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
"""Veda electoral — quiz disabled during election day voting hours."""

from datetime import datetime, timezone

from app.config import settings


def _parse_iso(value: str) -> datetime | None:
    """Parse an ISO 8601 timestamp, returning None if empty or invalid."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _in_window(start_str: str, end_str: str, now: datetime) -> bool:
    """Return True if `now` falls within the [start, end) window."""
    start = _parse_iso(start_str)
    end = _parse_iso(end_str)
    if not start or not end:
        return False
    return start <= now < end


def is_quiz_disabled(country: str, now: datetime | None = None) -> bool:
    """Check whether the quiz should be disabled for the given country.

    Returns True if `now` falls inside any configured veda window for
    that country.  Currently only Colombia ("co") is supported.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    # Ensure tz-aware
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    if country.lower() != "co":
        return False

    # 1ra vuelta
    if _in_window(settings.quiz_veda_start_co, settings.quiz_veda_end_co, now):
        return True

    # 2da vuelta
    if _in_window(settings.quiz_veda_start_co_2da, settings.quiz_veda_end_co_2da, now):
        return True

    return False
