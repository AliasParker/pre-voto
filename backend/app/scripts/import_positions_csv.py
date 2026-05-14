"""
CSV import script for candidate positions.

Run: python -m app.scripts.import_positions_csv /path/to/file.csv

CSV columns: candidate_slug, statement_id, value, source_quote, source_url, source_date, coded_by, notes

- candidate_slug: slug of the candidate (e.g. "maria-valencia")
- statement_id: UUID of the statement OR exact statement text for lookup
- value: integer -2..+2
- source_quote: optional quote from source
- source_url: optional URL
- source_date: optional ISO date (YYYY-MM-DD)
- coded_by: optional coder name
- notes: optional notes

Idempotent: uses INSERT ON CONFLICT (candidate_id, statement_id) DO UPDATE.
"""

import asyncio
import csv
import sys
import uuid
from datetime import date
from urllib.parse import urlparse

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings


def _is_valid_uuid(s: str) -> bool:
    try:
        uuid.UUID(s)
        return True
    except ValueError:
        return False


def _is_valid_url(s: str) -> bool:
    if not s:
        return True
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _is_valid_date(s: str) -> bool:
    if not s:
        return True
    try:
        date.fromisoformat(s)
        return True
    except ValueError:
        return False


async def import_csv(filepath: str) -> None:
    engine = create_async_engine(settings.database_url)

    errors: list[str] = []
    created = 0
    updated = 0

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate headers
        required = {"candidate_slug", "statement_id", "value"}
        if not required.issubset(set(reader.fieldnames or [])):
            print(f"ERROR: CSV must have columns: {required}")
            print(f"  Found: {reader.fieldnames}")
            await engine.dispose()
            sys.exit(1)

        rows = list(reader)

    async with engine.begin() as conn:
        # Pre-load all candidates (slug -> id)
        result = await conn.execute(text("SELECT id, slug FROM candidates"))
        candidate_map = {row.slug: row.id for row in result}

        # Pre-load all statements (id -> weight, text -> id)
        result = await conn.execute(text("SELECT id, text FROM statements"))
        statement_rows = result.fetchall()
        statement_by_id = {str(row.id): row.id for row in statement_rows}
        statement_by_text = {row.text: row.id for row in statement_rows}

        for i, row in enumerate(rows, start=2):  # start=2 because row 1 is header
            candidate_slug = row["candidate_slug"].strip()
            statement_ref = row["statement_id"].strip()
            value_str = row["value"].strip()
            source_quote = row.get("source_quote", "").strip() or None
            source_url = row.get("source_url", "").strip() or None
            source_date_str = row.get("source_date", "").strip() or None
            coded_by = row.get("coded_by", "").strip() or None
            notes = row.get("notes", "").strip() or None

            # Validate candidate
            if candidate_slug not in candidate_map:
                errors.append(f"Row {i}: candidate '{candidate_slug}' not found")
                continue
            candidate_id = candidate_map[candidate_slug]

            # Resolve statement
            statement_id = None
            if _is_valid_uuid(statement_ref):
                if statement_ref in statement_by_id:
                    statement_id = statement_by_id[statement_ref]
                else:
                    errors.append(f"Row {i}: statement UUID '{statement_ref}' not found")
                    continue
            elif statement_ref in statement_by_text:
                statement_id = statement_by_text[statement_ref]
            else:
                # Try pg_trgm similarity to suggest closest match
                sim_result = await conn.execute(
                    text(
                        "SELECT text, similarity(text, :ref) AS sim "
                        "FROM statements "
                        "WHERE similarity(text, :ref) > 0.1 "
                        "ORDER BY sim DESC LIMIT 1"
                    ),
                    {"ref": statement_ref},
                )
                closest = sim_result.fetchone()
                suggestion = ""
                if closest:
                    suggestion = f" Did you mean: '{closest.text[:80]}...'?"
                errors.append(
                    f"Row {i}: statement not found for '{statement_ref[:60]}...'.{suggestion}"
                )
                continue

            # Validate value
            try:
                value = int(value_str)
                if value < -2 or value > 2:
                    raise ValueError()
            except ValueError:
                errors.append(f"Row {i}: value must be integer -2..+2, got '{value_str}'")
                continue

            # Validate source_url
            if not _is_valid_url(source_url or ""):
                errors.append(f"Row {i}: invalid source_url '{source_url}'")
                continue

            # Validate source_date
            if not _is_valid_date(source_date_str or ""):
                errors.append(f"Row {i}: invalid source_date '{source_date_str}' (expected YYYY-MM-DD)")
                continue

            # Upsert
            result = await conn.execute(
                text("""
                    INSERT INTO candidate_positions
                        (candidate_id, statement_id, value, source_quote, source_url, source_date, coded_by, notes)
                    VALUES
                        (:candidate_id, :statement_id, :value, :source_quote, :source_url,
                         CAST(:source_date AS DATE), :coded_by, :notes)
                    ON CONFLICT (candidate_id, statement_id) DO UPDATE SET
                        value = EXCLUDED.value,
                        source_quote = EXCLUDED.source_quote,
                        source_url = EXCLUDED.source_url,
                        source_date = EXCLUDED.source_date,
                        coded_by = EXCLUDED.coded_by,
                        notes = EXCLUDED.notes
                    RETURNING (xmax = 0) AS inserted
                """),
                {
                    "candidate_id": candidate_id,
                    "statement_id": statement_id,
                    "value": value,
                    "source_quote": source_quote,
                    "source_url": source_url,
                    "source_date": source_date_str,
                    "coded_by": coded_by,
                    "notes": notes,
                },
            )
            row_result = result.fetchone()
            if row_result and row_result.inserted:
                created += 1
            else:
                updated += 1

    await engine.dispose()

    # Summary
    print("\n=== CSV Import — Summary ===")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Errors:  {len(errors)}")
    if errors:
        print("\n  Error details:")
        for err in errors:
            print(f"    - {err}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.scripts.import_positions_csv <path/to/file.csv>")
        sys.exit(1)
    asyncio.run(import_csv(sys.argv[1]))
