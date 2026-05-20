"""
Import 5 editorial articles for Colombia 2026 from the seed markdown file.

Run: docker compose exec api python -m app.scripts.import_articles_co_2026

Reads: seeds/co_2026/articulos_prevoto_v1.1.md
Target table: articles
UPSERT key: (country_id, slug)

Idempotent — running twice does not create duplicates, only updates.
"""

import asyncio
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

# Path to the seed file (relative to repo root, which is /app inside container)
SEED_FILE = Path("/app/seeds/co_2026/articulos_prevoto_v1.1.md")

EXPECTED_SLUGS = [
    "metodologia",
    "comparativo-cinco-candidatos",
    "otros-siete-candidatos",
    "como-se-vota",
    "lanzamiento",
]


def parse_frontmatter(yaml_str: str) -> dict:
    """Parse simple YAML frontmatter without requiring PyYAML.

    Handles the specific format used in the seed file:
      key: "value"          (quoted strings)
      key: value            (unquoted strings/dates)
      key: 2026-05-23       (date-only → 08:00 Bogotá / UTC-5)
      key: 2026-05-20T08:00:00-05:00  (full ISO 8601 with tz)
    """
    # Bogotá timezone (UTC-5)
    tz_bogota = timezone(timedelta(hours=-5))

    result: dict = {}
    for line in yaml_str.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Split on first colon
        colon_pos = line.find(":")
        if colon_pos == -1:
            continue
        key = line[:colon_pos].strip()
        value = line[colon_pos + 1:].strip()
        # Remove surrounding quotes
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        elif len(value) >= 2 and value[0] == "'" and value[-1] == "'":
            value = value[1:-1]
        # Try to parse as date/datetime using fromisoformat (Python 3.11+)
        if re.match(r"^\d{4}-\d{2}-\d{2}", value):
            try:
                parsed = datetime.fromisoformat(value)
                # If naive (no timezone), assume Bogotá (UTC-5) at 08:00
                if parsed.tzinfo is None:
                    # fromisoformat("2026-05-23") gives datetime(2026,5,23,0,0)
                    parsed = parsed.replace(hour=8, tzinfo=tz_bogota)
                result[key] = parsed
            except ValueError:
                result[key] = value
        else:
            result[key] = value
    return result


def parse_articles(content: str) -> list[dict]:
    """Parse the compendium markdown into a list of article dicts.

    Each article block starts with '# N / `slug.md`' and contains:
    - A YAML frontmatter block between ```yaml and ```
    - The body markdown after the frontmatter block
    """
    # Split by article headers: # 1 / `slug.md` ...
    header_pattern = re.compile(r"^# (\d+) / `[^`]+`.*$", re.MULTILINE)
    headers = list(header_pattern.finditer(content))

    if len(headers) != 5:
        print(f"ERROR: Expected 5 article headers, found {len(headers)}. Aborting.")
        sys.exit(1)

    articles = []

    for i, match in enumerate(headers):
        # Extract the block for this article
        start = match.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(content)
        block = content[start:end].strip()

        # Extract YAML frontmatter between ```yaml\n---\n...\n---\n```
        yaml_match = re.search(
            r"```yaml\s*\n---\n(.*?)\n---\s*\n```", block, re.DOTALL
        )
        if not yaml_match:
            print(f"ERROR: Could not find YAML frontmatter in article #{i+1}. Aborting.")
            sys.exit(1)

        yaml_str = yaml_match.group(1)
        frontmatter = parse_frontmatter(yaml_str)

        # Validate required fields
        required = ["title", "slug", "publication_date", "author", "country", "description"]
        missing = [f for f in required if f not in frontmatter]
        if missing:
            print(f"ERROR: Article #{i+1} missing frontmatter fields: {missing}. Aborting.")
            sys.exit(1)

        # Extract body: everything after the closing ``` of the YAML block
        body_start = yaml_match.end()
        body = block[body_start:].strip()

        # Remove trailing article separator: the last '---' line
        # We keep the editorial footer as part of the article body but strip
        # the final --- that separates articles in the compendium
        body = re.sub(r"\n---\s*$", "", body).strip()

        if len(body) < 100:
            print(f"ERROR: Article #{i+1} body too short ({len(body)} chars). Aborting.")
            sys.exit(1)

        articles.append({
            "title": frontmatter["title"],
            "slug": frontmatter["slug"],
            "publication_date": frontmatter["publication_date"],
            "author": frontmatter["author"],
            "country_code": frontmatter["country"].lower(),
            "description": frontmatter["description"],
            "body_markdown": body,
        })

    return articles


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)

    # Read the seed file
    if not SEED_FILE.exists():
        print(f"ERROR: Seed file not found: {SEED_FILE}")
        sys.exit(1)

    content = SEED_FILE.read_text(encoding="utf-8")
    articles = parse_articles(content)

    print(f"Parsed {len(articles)} articles from {SEED_FILE.name}")
    for a in articles:
        print(f"  - [{a['slug']}] {a['title'][:60]}... ({len(a['body_markdown'])} chars)")

    async with engine.begin() as conn:
        # Look up country_id for CO
        result = await conn.execute(
            text("SELECT id FROM countries WHERE code = :code"),
            {"code": "co"},
        )
        row = result.fetchone()
        if not row:
            print("ERROR: Country 'co' not found in countries table. "
                  "Run seed_colombia_2026.py first. Aborting.")
            sys.exit(1)

        country_id = row[0]
        print(f"Resolved country 'co' → {country_id}")

        inserted = 0
        updated = 0

        for article in articles:
            # publication_date is already a tz-aware datetime from parse_frontmatter
            pub_dt = article["publication_date"]
            if not isinstance(pub_dt, datetime) or pub_dt.tzinfo is None:
                print(f"ERROR: Invalid publication_date for '{article['slug']}': {pub_dt}")
                sys.exit(1)

            # UPSERT: INSERT ... ON CONFLICT (country_id, slug) DO UPDATE
            result = await conn.execute(
                text("""
                    INSERT INTO articles (country_id, slug, title, dek, body_markdown,
                                          author, published_at, is_demo)
                    VALUES (:country_id, :slug, :title, :dek, :body_markdown,
                            :author, :published_at, false)
                    ON CONFLICT (country_id, slug) DO UPDATE SET
                        title = EXCLUDED.title,
                        dek = EXCLUDED.dek,
                        body_markdown = EXCLUDED.body_markdown,
                        author = EXCLUDED.author,
                        published_at = EXCLUDED.published_at,
                        is_demo = false,
                        updated_at = now()
                    RETURNING (xmax = 0) AS is_insert
                """),
                {
                    "country_id": str(country_id),
                    "slug": article["slug"],
                    "title": article["title"],
                    "dek": article["description"],
                    "body_markdown": article["body_markdown"],
                    "author": article["author"],
                    "published_at": pub_dt,
                },
            )
            row = result.fetchone()
            if row and row[0]:
                inserted += 1
            else:
                updated += 1

    print(f"\nDone: {inserted} inserted, {updated} updated.")
    print(f"Total articles for CO: {inserted + updated}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
