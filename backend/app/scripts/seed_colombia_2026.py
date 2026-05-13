"""
Seed script for Colombia 2026 presidential election demo data.

Run: python -m app.scripts.seed_colombia_2026

Idempotent — uses INSERT ... ON CONFLICT DO NOTHING.
"""

import asyncio
import uuid
from datetime import date, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

# ---------------------------------------------------------------------------
# Fixed UUIDs for deterministic seeding
# ---------------------------------------------------------------------------
COUNTRY_ID = uuid.UUID("a1000000-0000-0000-0000-000000000001")
ELECTION_ID = uuid.UUID("b1000000-0000-0000-0000-000000000001")

CANDIDATE_IDS = [
    uuid.UUID("c1000000-0000-0000-0000-000000000001"),
    uuid.UUID("c1000000-0000-0000-0000-000000000002"),
    uuid.UUID("c1000000-0000-0000-0000-000000000003"),
    uuid.UUID("c1000000-0000-0000-0000-000000000004"),
    uuid.UUID("c1000000-0000-0000-0000-000000000005"),
]

STATEMENT_IDS = [
    uuid.UUID("d1000000-0000-0000-0000-000000000001"),
    uuid.UUID("d1000000-0000-0000-0000-000000000002"),
    uuid.UUID("d1000000-0000-0000-0000-000000000003"),
    uuid.UUID("d1000000-0000-0000-0000-000000000004"),
    uuid.UUID("d1000000-0000-0000-0000-000000000005"),
    uuid.UUID("d1000000-0000-0000-0000-000000000006"),
    uuid.UUID("d1000000-0000-0000-0000-000000000007"),
    uuid.UUID("d1000000-0000-0000-0000-000000000008"),
]

SOURCE_IDS = [
    uuid.UUID("e1000000-0000-0000-0000-000000000001"),
    uuid.UUID("e1000000-0000-0000-0000-000000000002"),
    uuid.UUID("e1000000-0000-0000-0000-000000000003"),
    uuid.UUID("e1000000-0000-0000-0000-000000000004"),
    uuid.UUID("e1000000-0000-0000-0000-000000000005"),
]

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

COUNTRY = {
    "id": COUNTRY_ID,
    "code": "co",
    "name": "Colombia",
    "language": "es",
    "is_active": True,
}

ELECTION = {
    "id": ELECTION_ID,
    "country_id": COUNTRY_ID,
    "type": "presidential_r1",
    "election_date": date(2026, 5, 31),
    "description": "Elecciones presidenciales de Colombia 2026 — primera vuelta",
    "is_active": True,
}

CANDIDATES = [
    {
        "id": CANDIDATE_IDS[0],
        "election_id": ELECTION_ID,
        "slug": "maria-valencia",
        "name": "María Valencia",
        "party": "Alianza Ciudadana",
        "party_acronym": "AC",
        "bio_short": "Economista y exministra de Hacienda. Propone reformas fiscales progresivas.",
        "color": "#2A9D8F",
        "is_demo": True,
    },
    {
        "id": CANDIDATE_IDS[1],
        "election_id": ELECTION_ID,
        "slug": "carlos-restrepo",
        "name": "Carlos Restrepo",
        "party": "Movimiento Fuerza Nacional",
        "party_acronym": "MFN",
        "bio_short": "Exalcalde de Medellín. Enfoque en seguridad y desarrollo empresarial.",
        "color": "#C17F59",
        "is_demo": True,
    },
    {
        "id": CANDIDATE_IDS[2],
        "election_id": ELECTION_ID,
        "slug": "laura-castillo",
        "name": "Laura Castillo",
        "party": "Partido Verde Esperanza",
        "party_acronym": "PVE",
        "bio_short": "Ambientalista y senadora. Prioriza transición energética y reforma rural.",
        "color": "#4A7CB5",
        "is_demo": True,
    },
    {
        "id": CANDIDATE_IDS[3],
        "election_id": ELECTION_ID,
        "slug": "andres-molina",
        "name": "Andrés Molina",
        "party": "Convergencia Democrática",
        "party_acronym": "CD",
        "bio_short": "Abogado constitucionalista. Propone reforma judicial y anticorrupción.",
        "color": "#7B68A5",
        "is_demo": True,
    },
    {
        "id": CANDIDATE_IDS[4],
        "election_id": ELECTION_ID,
        "slug": "sofia-herrera",
        "name": "Sofía Herrera",
        "party": "Movimiento Raíces",
        "party_acronym": "MR",
        "bio_short": "Socióloga y activista comunitaria. Enfoque en equidad social y educación.",
        "color": "#A3768A",
        "is_demo": True,
    },
]

STATEMENTS = [
    {
        "id": STATEMENT_IDS[0],
        "election_id": ELECTION_ID,
        "text": "El gobierno debe aumentar los impuestos a las grandes fortunas para financiar programas sociales.",
        "category": "economy",
        "weight": 2,
        "display_order": 1,
        "is_demo": True,
    },
    {
        "id": STATEMENT_IDS[1],
        "election_id": ELECTION_ID,
        "text": "Las fuerzas armadas deben tener más autonomía para combatir el narcotráfico y los grupos armados.",
        "category": "security",
        "weight": 2,
        "display_order": 2,
        "is_demo": True,
    },
    {
        "id": STATEMENT_IDS[2],
        "election_id": ELECTION_ID,
        "text": "El Estado debe garantizar un ingreso básico universal para todos los ciudadanos en situación de pobreza.",
        "category": "social",
        "weight": 1,
        "display_order": 3,
        "is_demo": True,
    },
    {
        "id": STATEMENT_IDS[3],
        "election_id": ELECTION_ID,
        "text": "Colombia debe prohibir el fracking y acelerar la transición hacia energías renovables.",
        "category": "environment",
        "weight": 2,
        "display_order": 4,
        "is_demo": True,
    },
    {
        "id": STATEMENT_IDS[4],
        "election_id": ELECTION_ID,
        "text": "La política de drogas debe priorizar la legalización regulada sobre la erradicación forzosa.",
        "category": "drugs",
        "weight": 3,
        "display_order": 5,
        "is_demo": True,
    },
    {
        "id": STATEMENT_IDS[5],
        "election_id": ELECTION_ID,
        "text": "Colombia debe fortalecer su relación comercial con Estados Unidos y la Unión Europea por encima de alianzas regionales.",
        "category": "foreign_policy",
        "weight": 1,
        "display_order": 6,
        "is_demo": True,
    },
    {
        "id": STATEMENT_IDS[6],
        "election_id": ELECTION_ID,
        "text": "El sistema de salud debe avanzar hacia un modelo de cobertura pública universal, reduciendo la participación del sector privado.",
        "category": "health",
        "weight": 2,
        "display_order": 7,
        "is_demo": True,
    },
    {
        "id": STATEMENT_IDS[7],
        "election_id": ELECTION_ID,
        "text": "La educación universitaria pública debe ser completamente gratuita para todos los estratos socioeconómicos.",
        "category": "education",
        "weight": 1,
        "display_order": 8,
        "is_demo": True,
    },
]

# 5 candidates x 8 statements = 40 positions
# Values: -2 (muy en contra), -1 (en contra), 0 (neutro), 1 (a favor), 2 (muy a favor)
POSITION_VALUES = [
    # economy, security, social, environment, drugs, foreign_policy, health, education
    [ 2,  -1,   2,   1,   1,  -1,   2,   2],  # María Valencia
    [-1,   2,  -1,  -1,  -2,   2,  -1,  -1],  # Carlos Restrepo
    [ 1,  -2,   1,   2,   2,  -1,   1,   2],  # Laura Castillo
    [ 0,   0,   0,   1,   1,   0,   0,   1],  # Andrés Molina
    [ 2,  -1,   2,   1,   0,  -2,   2,   2],  # Sofía Herrera
]

SOURCES = [
    {
        "id": SOURCE_IDS[0],
        "country_id": COUNTRY_ID,
        "name": "El Tiempo",
        "feed_url": "https://www.eltiempo.com/rss/politica.xml",
        "site_url": "https://www.eltiempo.com",
        "is_active": True,
    },
    {
        "id": SOURCE_IDS[1],
        "country_id": COUNTRY_ID,
        "name": "El Espectador",
        "feed_url": "https://www.elespectador.com/rss/politica.xml",
        "site_url": "https://www.elespectador.com",
        "is_active": True,
    },
    {
        "id": SOURCE_IDS[2],
        "country_id": COUNTRY_ID,
        "name": "La Silla Vacía",
        "feed_url": "https://www.lasillavacia.com/feed/",
        "site_url": "https://www.lasillavacia.com",
        "is_active": True,
    },
    {
        "id": SOURCE_IDS[3],
        "country_id": COUNTRY_ID,
        "name": "Semana",
        "feed_url": "https://www.semana.com/rss/nacion.xml",
        "site_url": "https://www.semana.com",
        "is_active": True,
    },
    {
        "id": SOURCE_IDS[4],
        "country_id": COUNTRY_ID,
        "name": "Razón Pública",
        "feed_url": "https://razonpublica.com/feed/",
        "site_url": "https://razonpublica.com",
        "is_active": True,
    },
]


async def seed() -> None:
    engine = create_async_engine(settings.database_url)

    async with engine.begin() as conn:
        # --- Country ---
        result = await conn.execute(
            text("""
                INSERT INTO countries (id, code, name, language, is_active)
                VALUES (:id, :code, :name, :language, :is_active)
                ON CONFLICT (code) DO NOTHING
            """),
            COUNTRY,
        )
        countries_inserted = result.rowcount

        # --- Election ---
        result = await conn.execute(
            text("""
                INSERT INTO elections (id, country_id, type, election_date, description, is_active)
                VALUES (:id, :country_id, :type, :election_date, :description, :is_active)
                ON CONFLICT DO NOTHING
            """),
            ELECTION,
        )
        elections_inserted = result.rowcount

        # --- Candidates ---
        candidates_inserted = 0
        for c in CANDIDATES:
            result = await conn.execute(
                text("""
                    INSERT INTO candidates (id, election_id, slug, name, party, party_acronym, bio_short, color, is_demo)
                    VALUES (:id, :election_id, :slug, :name, :party, :party_acronym, :bio_short, :color, :is_demo)
                    ON CONFLICT (election_id, slug) DO NOTHING
                """),
                c,
            )
            candidates_inserted += result.rowcount

        # --- Statements ---
        statements_inserted = 0
        for s in STATEMENTS:
            result = await conn.execute(
                text("""
                    INSERT INTO statements (id, election_id, text, category, weight, display_order, is_demo)
                    VALUES (:id, :election_id, :text, :category, :weight, :display_order, :is_demo)
                    ON CONFLICT DO NOTHING
                """),
                s,
            )
            statements_inserted += result.rowcount

        # --- Candidate Positions ---
        positions_inserted = 0
        for ci, candidate_id in enumerate(CANDIDATE_IDS):
            for si, statement_id in enumerate(STATEMENT_IDS):
                value = POSITION_VALUES[ci][si]
                result = await conn.execute(
                    text("""
                        INSERT INTO candidate_positions
                            (candidate_id, statement_id, value, source_quote, source_url, coded_by)
                        VALUES
                            (:candidate_id, :statement_id, :value, :source_quote, :source_url, :coded_by)
                        ON CONFLICT (candidate_id, statement_id) DO NOTHING
                    """),
                    {
                        "candidate_id": candidate_id,
                        "statement_id": statement_id,
                        "value": value,
                        "source_quote": f"Posición demo del candidato sobre {STATEMENTS[si]['category']}.",
                        "source_url": f"https://example.com/fuente-demo/{CANDIDATES[ci]['slug']}",
                        "coded_by": "seed",
                    },
                )
                positions_inserted += result.rowcount

        # --- Sources ---
        sources_inserted = 0
        for s in SOURCES:
            result = await conn.execute(
                text("""
                    INSERT INTO sources (id, country_id, name, feed_url, site_url, is_active)
                    VALUES (:id, :country_id, :name, :feed_url, :site_url, :is_active)
                    ON CONFLICT (feed_url) DO NOTHING
                """),
                s,
            )
            sources_inserted += result.rowcount

    await engine.dispose()

    # --- Summary ---
    print("\n=== Seed Colombia 2026 — Resumen ===")
    print(f"  countries:           {countries_inserted} insertado(s)")
    print(f"  elections:           {elections_inserted} insertado(s)")
    print(f"  candidates:          {candidates_inserted} insertado(s)")
    print(f"  statements:          {statements_inserted} insertado(s)")
    print(f"  candidate_positions: {positions_inserted} insertado(s)")
    print(f"  sources:             {sources_inserted} insertado(s)")

    total = (
        countries_inserted
        + elections_inserted
        + candidates_inserted
        + statements_inserted
        + positions_inserted
        + sources_inserted
    )
    if total == 0:
        print("\n  (Todos los registros ya existían — idempotente)")
    print()


if __name__ == "__main__":
    asyncio.run(seed())
