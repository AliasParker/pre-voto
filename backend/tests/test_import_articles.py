"""Tests for the article import script's date parsing logic."""

from datetime import datetime, timedelta, timezone

from app.scripts.import_articles_co_2026 import parse_frontmatter

TZ_BOGOTA = timezone(timedelta(hours=-5))


def test_parse_date_only_defaults_to_bogota_8am():
    """YYYY-MM-DD (no time) → 08:00 Bogotá (UTC-5)."""
    fm = parse_frontmatter('publication_date: 2026-05-23')
    result = fm["publication_date"]
    expected = datetime(2026, 5, 23, 8, 0, 0, tzinfo=TZ_BOGOTA)
    assert result == expected
    assert result.utcoffset() == timedelta(hours=-5)


def test_parse_iso8601_with_timezone():
    """Full ISO 8601 with explicit timezone → parsed as-is."""
    fm = parse_frontmatter('publication_date: 2026-05-20T08:00:00-05:00')
    result = fm["publication_date"]
    expected = datetime(2026, 5, 20, 8, 0, 0, tzinfo=TZ_BOGOTA)
    assert result == expected
    assert result.utcoffset() == timedelta(hours=-5)


def test_parse_iso8601_utc():
    """ISO 8601 with Z suffix → parsed as UTC."""
    fm = parse_frontmatter('publication_date: 2026-05-20T13:00:00+00:00')
    result = fm["publication_date"]
    expected = datetime(2026, 5, 20, 13, 0, 0, tzinfo=timezone.utc)
    assert result == expected
    assert result.utcoffset() == timedelta(0)


def test_both_formats_represent_same_instant():
    """Date-only 2026-05-20 (→ 08:00-05:00) equals 2026-05-20T08:00:00-05:00."""
    fm_date = parse_frontmatter('publication_date: 2026-05-20')
    fm_iso = parse_frontmatter('publication_date: 2026-05-20T08:00:00-05:00')
    assert fm_date["publication_date"] == fm_iso["publication_date"]


def test_non_date_strings_unchanged():
    """Non-date values are returned as plain strings."""
    fm = parse_frontmatter('slug: "metodologia"\nauthor: "Equipo pre.voto"')
    assert fm["slug"] == "metodologia"
    assert fm["author"] == "Equipo pre.voto"
