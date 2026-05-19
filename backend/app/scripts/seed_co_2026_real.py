"""
Seed script for Colombia 2026 — REAL production data.

Reads seeds/co_2026/{candidates,statements,positions}.json and replaces
the demo seed (Alfa/Beta/Gamma/Delta/Epsilon) with real candidates.

Run: python -m app.scripts.seed_co_2026_real

Idempotent: safe to run multiple times. Uses a single atomic transaction.
"""

import asyncio
import json
import sys
import uuid
from collections import Counter
from datetime import date as date_type
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# Try container path first (/app/seeds/), fall back to repo root
_container_path = Path("/app/seeds/co_2026")
_repo_path = Path(__file__).resolve().parents[3] / "seeds" / "co_2026"
SEEDS_DIR = _container_path if _container_path.exists() else _repo_path

# ---------------------------------------------------------------------------
# Fixed UUIDs (deterministic, match existing demo seed for country/election)
# ---------------------------------------------------------------------------
COUNTRY_ID = uuid.UUID("a1000000-0000-0000-0000-000000000001")
ELECTION_ID = uuid.UUID("b1000000-0000-0000-0000-000000000001")

# Deterministic UUIDs for real candidates (c2 prefix to not collide with demo c1)
def _candidate_uuid(n: int) -> uuid.UUID:
    return uuid.UUID(f"c2000000-0000-0000-0000-{n:012d}")

# Deterministic UUIDs for real statements (d2 prefix)
def _statement_uuid(n: int) -> uuid.UUID:
    return uuid.UUID(f"d2000000-0000-0000-0000-{n:012d}")

# ---------------------------------------------------------------------------
# Value mapping
# ---------------------------------------------------------------------------
POSITION_MAP = {
    "very_agree": 2,
    "agree": 1,
    "neutral": 0,
    "disagree": -1,
    "very_disagree": -2,
}


def load_json(filename: str) -> dict:
    path = SEEDS_DIR / filename
    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def compute_high_confidence_pct(positions: list[dict], candidate_slug: str) -> int:
    """Count confidence='high' positions for a candidate, return percentage."""
    cand_positions = [p for p in positions if p["candidate_slug"] == candidate_slug]
    if not cand_positions:
        return 0
    high_count = sum(1 for p in cand_positions if p["confidence"] == "high")
    return round(high_count / len(cand_positions) * 100)


async def seed() -> None:
    # Load seed data
    candidates_data = load_json("candidates.json")
    statements_data = load_json("statements.json")
    positions_data = load_json("positions.json")

    candidates = candidates_data["candidates"]
    statements = statements_data["statements"]
    positions = positions_data["positions"]

    # Validate counts
    active_candidates = [c for c in candidates if not c.get("withdrawn", False)]
    assert len(statements) == 20, f"Expected 20 statements, got {len(statements)}"
    assert len(positions) == 240, f"Expected 240 positions, got {len(positions)}"
    assert len(active_candidates) == 12, f"Expected 12 active candidates, got {len(active_candidates)}"

    # Validate each active candidate has exactly 20 positions
    slug_counts = Counter(p["candidate_slug"] for p in positions)
    for c in active_candidates:
        count = slug_counts.get(c["slug"], 0)
        assert count == 20, f"Candidate {c['slug']} has {count} positions, expected 20"

    # Build UUID maps
    candidate_uuid_map = {c["slug"]: _candidate_uuid(c["id"]) for c in candidates}
    statement_uuid_map = {s["id"]: _statement_uuid(s["id"]) for s in statements}

    # Compute real high_confidence_pct from positions
    high_pct_map = {}
    for c in candidates:
        if c.get("withdrawn", False):
            high_pct_map[c["slug"]] = None
        else:
            high_pct_map[c["slug"]] = compute_high_confidence_pct(positions, c["slug"])

    engine = create_async_engine(settings.database_url)

    async with engine.begin() as conn:
        # ---------------------------------------------------------------
        # Step 1: Delete demo data (within the same transaction)
        # ---------------------------------------------------------------
        # Delete demo positions (cascade from demo candidates)
        await conn.execute(text("""
            DELETE FROM candidate_positions
            WHERE candidate_id IN (
                SELECT id FROM candidates WHERE is_demo = true AND election_id = :eid
            )
        """), {"eid": ELECTION_ID})

        # Delete demo candidates
        result = await conn.execute(text("""
            DELETE FROM candidates WHERE is_demo = true AND election_id = :eid
        """), {"eid": ELECTION_ID})
        demo_candidates_deleted = result.rowcount

        # Delete demo statements
        result = await conn.execute(text("""
            DELETE FROM statements WHERE is_demo = true AND election_id = :eid
        """), {"eid": ELECTION_ID})
        demo_statements_deleted = result.rowcount

        # Delete demo articles for this country
        result = await conn.execute(text("""
            DELETE FROM articles WHERE is_demo = true AND country_id = :cid
        """), {"cid": COUNTRY_ID})
        demo_articles_deleted = result.rowcount

        print(f"  Demo data deleted: {demo_candidates_deleted} candidates, "
              f"{demo_statements_deleted} statements, {demo_articles_deleted} articles")

        # ---------------------------------------------------------------
        # Step 2: Ensure country and election exist (idempotent)
        # ---------------------------------------------------------------
        await conn.execute(text("""
            INSERT INTO countries (id, code, name, language, is_active)
            VALUES (:id, 'co', 'Colombia', 'es', true)
            ON CONFLICT (code) DO NOTHING
        """), {"id": COUNTRY_ID})

        await conn.execute(text("""
            INSERT INTO elections (id, country_id, type, election_date, description, is_active)
            VALUES (:id, :country_id, 'presidential_r1', '2026-05-31',
                    'Elecciones presidenciales de Colombia 2026 — primera vuelta', true)
            ON CONFLICT DO NOTHING
        """), {"id": ELECTION_ID, "country_id": COUNTRY_ID})

        # ---------------------------------------------------------------
        # Step 3: Insert real statements
        # ---------------------------------------------------------------
        statements_inserted = 0
        for s in statements:
            sid = statement_uuid_map[s["id"]]
            result = await conn.execute(text("""
                INSERT INTO statements (id, election_id, slug, text, category,
                                        short_label, weight, display_order, is_demo)
                VALUES (:id, :eid, :slug, :text, :category,
                        :short_label, 1, :display_order, false)
                ON CONFLICT DO NOTHING
            """), {
                "id": sid,
                "eid": ELECTION_ID,
                "slug": s["slug"],
                "text": s["text"],
                "category": s["axis"],
                "short_label": s["short_label"],
                "display_order": s["id"],
            })
            statements_inserted += result.rowcount

        # ---------------------------------------------------------------
        # Step 4: Insert real candidates
        # ---------------------------------------------------------------
        candidates_inserted = 0
        for c in candidates:
            cid = candidate_uuid_map[c["slug"]]
            result = await conn.execute(text("""
                INSERT INTO candidates (
                    id, election_id, slug, name, coalition,
                    bio_short, ballot_position, running_mate,
                    positioning, age, plan_url, high_confidence_pct,
                    withdrawn, withdrawn_date, endorses, is_demo
                )
                VALUES (
                    :id, :eid, :slug, :name, :coalition,
                    :bio_short, :ballot_position, :running_mate,
                    :positioning, :age, :plan_url, :high_confidence_pct,
                    :withdrawn, :withdrawn_date, :endorses, false
                )
                ON CONFLICT (election_id, slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    coalition = EXCLUDED.coalition,
                    bio_short = EXCLUDED.bio_short,
                    ballot_position = EXCLUDED.ballot_position,
                    running_mate = EXCLUDED.running_mate,
                    positioning = EXCLUDED.positioning,
                    age = EXCLUDED.age,
                    plan_url = EXCLUDED.plan_url,
                    high_confidence_pct = EXCLUDED.high_confidence_pct,
                    withdrawn = EXCLUDED.withdrawn,
                    withdrawn_date = EXCLUDED.withdrawn_date,
                    endorses = EXCLUDED.endorses,
                    is_demo = false
            """), {
                "id": cid,
                "eid": ELECTION_ID,
                "slug": c["slug"],
                "name": c["full_name"],
                "coalition": c.get("coalition"),
                "bio_short": c.get("bio_short"),
                "ballot_position": c.get("ballot_position"),
                "running_mate": c.get("running_mate"),
                "positioning": c.get("positioning"),
                "age": c.get("age"),
                "plan_url": c.get("plan_url"),
                "high_confidence_pct": high_pct_map.get(c["slug"]),
                "withdrawn": c.get("withdrawn", False),
                "withdrawn_date": (
                    date_type.fromisoformat(c["withdrawn_date"])
                    if c.get("withdrawn_date") else None
                ),
                "endorses": c.get("endorses"),
            })
            candidates_inserted += result.rowcount

        # ---------------------------------------------------------------
        # Step 5: Insert real positions
        # ---------------------------------------------------------------
        positions_inserted = 0
        for p in positions:
            cid = candidate_uuid_map[p["candidate_slug"]]
            sid = statement_uuid_map[p["statement_id"]]
            value = POSITION_MAP[p["position"]]

            result = await conn.execute(text("""
                INSERT INTO candidate_positions (
                    candidate_id, statement_id, value,
                    confidence, source_type,
                    source_quote, source_url, notes, coded_by
                )
                VALUES (
                    :cid, :sid, :value,
                    :confidence, :source_type,
                    :source_quote, :source_url, :notes, 'seed_co_2026_real'
                )
                ON CONFLICT (candidate_id, statement_id) DO UPDATE SET
                    value = EXCLUDED.value,
                    confidence = EXCLUDED.confidence,
                    source_type = EXCLUDED.source_type,
                    source_quote = EXCLUDED.source_quote,
                    source_url = EXCLUDED.source_url,
                    notes = EXCLUDED.notes,
                    coded_by = EXCLUDED.coded_by
            """), {
                "cid": cid,
                "sid": sid,
                "value": value,
                "confidence": p["confidence"],
                "source_type": p["source_type"],
                "source_quote": p.get("source_quote"),
                "source_url": p.get("source_url"),
                "notes": p.get("notes"),
            })
            positions_inserted += result.rowcount

        # ---------------------------------------------------------------
        # Step 6: Validation queries
        # ---------------------------------------------------------------
        r = await conn.execute(text(
            "SELECT count(*) FROM candidates WHERE election_id = :eid"
        ), {"eid": ELECTION_ID})
        total_candidates = r.scalar()

        r = await conn.execute(text(
            "SELECT count(*) FROM candidates WHERE election_id = :eid AND withdrawn = false"
        ), {"eid": ELECTION_ID})
        active_count = r.scalar()

        r = await conn.execute(text(
            "SELECT count(*) FROM statements WHERE election_id = :eid"
        ), {"eid": ELECTION_ID})
        total_statements = r.scalar()

        r = await conn.execute(text("""
            SELECT count(*) FROM candidate_positions cp
            JOIN candidates c ON cp.candidate_id = c.id
            WHERE c.election_id = :eid
        """), {"eid": ELECTION_ID})
        total_positions = r.scalar()

        # Verify no positions for withdrawn candidates
        r = await conn.execute(text("""
            SELECT count(*) FROM candidate_positions cp
            JOIN candidates c ON cp.candidate_id = c.id
            WHERE c.election_id = :eid AND c.withdrawn = true
        """), {"eid": ELECTION_ID})
        withdrawn_positions = r.scalar()

    await engine.dispose()

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    print("\n=== Seed Colombia 2026 (REAL) — Resumen ===")
    print(f"  statements inserted/updated:  {statements_inserted}")
    print(f"  candidates inserted/updated:  {candidates_inserted}")
    print(f"  positions  inserted/updated:  {positions_inserted}")
    print()
    print("=== Validation ===")
    print(f"  Total candidates:    {total_candidates} (expected 14)")
    print(f"  Active candidates:   {active_count} (expected 12)")
    print(f"  Total statements:    {total_statements} (expected 20)")
    print(f"  Total positions:     {total_positions} (expected 240)")
    print(f"  Withdrawn positions: {withdrawn_positions} (expected 0)")
    print()

    # High confidence % per candidate
    print("=== high_confidence_pct (calculado) ===")
    for c in sorted(candidates, key=lambda x: x["ballot_position"]):
        if c.get("withdrawn"):
            print(f"  {c['slug']:30s}  (withdrawn)")
        else:
            pct = high_pct_map[c["slug"]]
            print(f"  {c['slug']:30s}  {pct}%")

    # Final checks
    ok = True
    if total_candidates != 14:
        print(f"\n  FAIL: expected 14 candidates, got {total_candidates}")
        ok = False
    if active_count != 12:
        print(f"\n  FAIL: expected 12 active candidates, got {active_count}")
        ok = False
    if total_statements != 20:
        print(f"\n  FAIL: expected 20 statements, got {total_statements}")
        ok = False
    if total_positions != 240:
        print(f"\n  FAIL: expected 240 positions, got {total_positions}")
        ok = False
    if withdrawn_positions != 0:
        print(f"\n  FAIL: withdrawn candidates have {withdrawn_positions} positions")
        ok = False

    if ok:
        print("\n  ALL CHECKS PASSED")
    else:
        print("\n  SOME CHECKS FAILED — review output above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed())
