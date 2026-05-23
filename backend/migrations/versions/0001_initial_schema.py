# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
"""initial schema

Revision ID: 0001
Revises:
Create Date: 2025-05-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Extensions ---
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # --- countries ---
    op.create_table(
        "countries",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(2), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("language", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_countries")),
        sa.UniqueConstraint("code", name=op.f("uq_countries_code")),
    )

    # --- elections ---
    op.create_table(
        "elections",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("country_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("election_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"], name=op.f("fk_elections_country_id_countries")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_elections")),
    )
    op.create_index(op.f("ix_elections_country_id"), "elections", ["country_id"])

    # --- candidates ---
    op.create_table(
        "candidates",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("election_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("party", sa.Text(), nullable=True),
        sa.Column("party_acronym", sa.Text(), nullable=True),
        sa.Column("bio_short", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("photo_author", sa.Text(), nullable=True),
        sa.Column("photo_license", sa.Text(), nullable=True),
        sa.Column("photo_attribution", sa.Text(), nullable=True),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("is_demo", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("sources", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["election_id"], ["elections.id"], name=op.f("fk_candidates_election_id_elections")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_candidates")),
        sa.UniqueConstraint("election_id", "slug", name=op.f("uq_candidates_election_id")),
        sa.CheckConstraint(r"color ~ '^#[0-9A-Fa-f]{6}$'", name=op.f("ck_candidates_color_hex_format")),
    )
    op.create_index(op.f("ix_candidates_election_id"), "candidates", ["election_id"])
    op.create_index(op.f("ix_candidates_slug"), "candidates", ["slug"])

    # --- statements ---
    op.create_table(
        "statements",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("election_id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("weight", sa.Integer(), server_default="1", nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("is_demo", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["election_id"], ["elections.id"], name=op.f("fk_statements_election_id_elections")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_statements")),
        sa.CheckConstraint("weight BETWEEN 1 AND 3", name=op.f("ck_statements_weight_range")),
    )
    op.create_index(op.f("ix_statements_election_id"), "statements", ["election_id"])

    # statements.embedding — vector column added via raw SQL
    op.execute("ALTER TABLE statements ADD COLUMN embedding vector(1536)")

    # --- candidate_positions ---
    op.create_table(
        "candidate_positions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("candidate_id", sa.Uuid(), nullable=False),
        sa.Column("statement_id", sa.Uuid(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("source_quote", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("source_date", sa.Date(), nullable=True),
        sa.Column("coded_by", sa.Text(), nullable=True),
        sa.Column("coded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], name=op.f("fk_candidate_positions_candidate_id_candidates")),
        sa.ForeignKeyConstraint(["statement_id"], ["statements.id"], name=op.f("fk_candidate_positions_statement_id_statements")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_candidate_positions")),
        sa.UniqueConstraint("candidate_id", "statement_id", name=op.f("uq_candidate_positions_candidate_id")),
        sa.CheckConstraint("value BETWEEN -2 AND 2", name=op.f("ck_candidate_positions_value_range")),
    )

    # --- articles ---
    op.create_table(
        "articles",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("country_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("dek", sa.Text(), nullable=True),
        sa.Column("body_markdown", sa.Text(), nullable=False),
        sa.Column("hero_image_url", sa.Text(), nullable=True),
        sa.Column("hero_image_attribution", sa.Text(), nullable=True),
        sa.Column("author", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_demo", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"], name=op.f("fk_articles_country_id_countries")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_articles")),
        sa.UniqueConstraint("country_id", "slug", name=op.f("uq_articles_country_id")),
    )
    op.create_index(op.f("ix_articles_country_id"), "articles", ["country_id"])
    op.create_index(op.f("ix_articles_slug"), "articles", ["slug"])
    op.create_index("ix_articles_country_id_published_at", "articles", ["country_id", "published_at"])

    # articles.embedding — vector column added via raw SQL
    op.execute("ALTER TABLE articles ADD COLUMN embedding vector(1536)")

    # --- sources ---
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("country_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("feed_url", sa.Text(), nullable=False),
        sa.Column("site_url", sa.Text(), nullable=True),
        sa.Column("last_pulled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"], name=op.f("fk_sources_country_id_countries")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sources")),
        sa.UniqueConstraint("feed_url", name=op.f("uq_sources_feed_url")),
    )
    op.create_index(op.f("ix_sources_country_id"), "sources", ["country_id"])

    # --- news_items ---
    op.create_table(
        "news_items",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("country_id", sa.Uuid(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("snippet", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Text(), server_default=sa.text("'raw'"), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], name=op.f("fk_news_items_source_id_sources")),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"], name=op.f("fk_news_items_country_id_countries")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_news_items")),
        sa.UniqueConstraint("url", name=op.f("uq_news_items_url")),
    )
    op.create_index(op.f("ix_news_items_country_id"), "news_items", ["country_id"])
    op.create_index(op.f("ix_news_items_source_id"), "news_items", ["source_id"])

    # --- polls ---
    op.create_table(
        "polls",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("election_id", sa.Uuid(), nullable=False),
        sa.Column("pollster", sa.Text(), nullable=False),
        sa.Column("field_start", sa.Date(), nullable=False),
        sa.Column("field_end", sa.Date(), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("methodology", sa.Text(), nullable=True),
        sa.Column("results", postgresql.JSONB(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["election_id"], ["elections.id"], name=op.f("fk_polls_election_id_elections")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_polls")),
    )
    op.create_index(op.f("ix_polls_election_id"), "polls", ["election_id"])

    # --- poll_averages ---
    op.create_table(
        "poll_averages",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("election_id", sa.Uuid(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("results", postgresql.JSONB(), nullable=False),
        sa.Column("polls_included", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["election_id"], ["elections.id"], name=op.f("fk_poll_averages_election_id_elections")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_poll_averages")),
    )
    op.create_index(op.f("ix_poll_averages_election_id"), "poll_averages", ["election_id"])

    # --- subscribers ---
    op.create_table(
        "subscribers",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("country_code", sa.String(2), nullable=True),
        sa.Column("language", sa.Text(), server_default=sa.text("'es'"), nullable=False),
        sa.Column("beehiiv_id", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default=sa.text("'pending'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscribers")),
        sa.UniqueConstraint("email", name=op.f("uq_subscribers_email")),
    )

    # --- quiz_completions ---
    op.create_table(
        "quiz_completions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("election_id", sa.Uuid(), nullable=False),
        sa.Column("session_hash", sa.Text(), nullable=True),
        sa.Column("statements_answered", sa.Integer(), nullable=True),
        sa.Column("top_match_candidate_id", sa.Uuid(), nullable=True),
        sa.Column("top_match_pct", sa.Numeric(4, 1), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["election_id"], ["elections.id"], name=op.f("fk_quiz_completions_election_id_elections")),
        sa.ForeignKeyConstraint(["top_match_candidate_id"], ["candidates.id"], name=op.f("fk_quiz_completions_top_match_candidate_id_candidates")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quiz_completions")),
    )
    op.create_index(op.f("ix_quiz_completions_election_id"), "quiz_completions", ["election_id"])

    # --- Trigger function: update_updated_at_column ---
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # --- Triggers for tables with updated_at ---
    for table in ("countries", "elections", "candidates", "statements", "candidate_positions", "articles"):
        op.execute(f"""
            CREATE TRIGGER tg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers
    for table in ("articles", "candidate_positions", "statements", "candidates", "elections", "countries"):
        op.execute(f"DROP TRIGGER IF EXISTS tg_{table}_updated_at ON {table}")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables in reverse dependency order
    op.drop_table("quiz_completions")
    op.drop_table("subscribers")
    op.drop_table("poll_averages")
    op.drop_table("polls")
    op.drop_table("news_items")
    op.drop_table("sources")
    op.drop_table("articles")
    op.drop_table("candidate_positions")
    op.drop_table("statements")
    op.drop_table("candidates")
    op.drop_table("elections")
    op.drop_table("countries")

    # Drop extensions
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
