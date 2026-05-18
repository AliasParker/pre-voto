#!/usr/bin/env bash
# =============================================================================
# pre.voto — PostgreSQL Restore from Cloudflare R2
# Usage: bash /opt/prevoto/infra/restore-postgres.sh [YYYYMMDD]
#   If no date is given, lists available backups.
# =============================================================================
set -euo pipefail

APP_DIR="/opt/prevoto"
ENV_FILE="$APP_DIR/.env"
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

echo "=== pre.voto restore started at $(date -u) ==="

# ---- Load R2 credentials from .env ----
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found."
  exit 1
fi

CLOUDFLARE_R2_ACCESS_KEY=$(grep -E '^CLOUDFLARE_R2_ACCESS_KEY=' "$ENV_FILE" | cut -d= -f2-)
CLOUDFLARE_R2_SECRET_KEY=$(grep -E '^CLOUDFLARE_R2_SECRET_KEY=' "$ENV_FILE" | cut -d= -f2-)
CLOUDFLARE_R2_ENDPOINT=$(grep -E '^CLOUDFLARE_R2_ENDPOINT=' "$ENV_FILE" | cut -d= -f2-)
CLOUDFLARE_R2_BUCKET=$(grep -E '^CLOUDFLARE_R2_BUCKET=' "$ENV_FILE" | cut -d= -f2- || echo "prevoto-backups")

if [ -z "$CLOUDFLARE_R2_ACCESS_KEY" ] || [ -z "$CLOUDFLARE_R2_SECRET_KEY" ] || [ -z "$CLOUDFLARE_R2_ENDPOINT" ]; then
  echo "ERROR: R2 credentials not set in $ENV_FILE."
  exit 1
fi

export RCLONE_CONFIG_R2_TYPE="s3"
export RCLONE_CONFIG_R2_PROVIDER="Cloudflare"
export RCLONE_CONFIG_R2_ACCESS_KEY_ID="$CLOUDFLARE_R2_ACCESS_KEY"
export RCLONE_CONFIG_R2_SECRET_ACCESS_KEY="$CLOUDFLARE_R2_SECRET_KEY"
export RCLONE_CONFIG_R2_ENDPOINT="$CLOUDFLARE_R2_ENDPOINT"
export RCLONE_CONFIG_R2_NO_CHECK_BUCKET="true"

# ---- If no date given, list available backups ----
if [ $# -eq 0 ]; then
  echo ""
  echo "Available backups in r2:$CLOUDFLARE_R2_BUCKET/:"
  rclone ls "r2:$CLOUDFLARE_R2_BUCKET/"
  echo ""
  echo "Usage: $0 YYYYMMDD"
  echo "Example: $0 20260518"
  exit 0
fi

DATE="$1"
BACKUP_FILE="${DATE}.sql.gz"
TMP_FILE="/tmp/prevoto-restore-${DATE}.sql.gz"

# ---- Download backup ----
echo "Downloading r2:$CLOUDFLARE_R2_BUCKET/$BACKUP_FILE..."
rclone copyto "r2:$CLOUDFLARE_R2_BUCKET/$BACKUP_FILE" "$TMP_FILE"
echo "  Downloaded to $TMP_FILE ($(du -h "$TMP_FILE" | cut -f1))."

# ---- Confirm ----
echo ""
echo "WARNING: This will DROP and recreate the prevoto database."
echo "Press Ctrl+C to cancel, or Enter to continue."
read -r

# ---- Stop API and worker ----
echo "Stopping api and worker..."
cd "$APP_DIR"
$COMPOSE stop api worker
echo "  Containers stopped."

# ---- Restore ----
echo "Restoring database from $BACKUP_FILE..."
gunzip -c "$TMP_FILE" | docker compose exec -T postgres psql -U prevoto -d prevoto -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" 2>/dev/null
gunzip -c "$TMP_FILE" | docker compose exec -T postgres psql -U prevoto -d prevoto
echo "  Database restored."

# ---- Restart containers ----
echo "Restarting containers..."
$COMPOSE up -d
echo "  Containers restarted."

# ---- Cleanup ----
rm -f "$TMP_FILE"

# ---- Verification ----
echo ""
echo "Verification — row counts:"
docker compose exec -T postgres psql -U prevoto -d prevoto -c "
  SELECT 'countries' AS table_name, count(*) FROM countries
  UNION ALL SELECT 'elections', count(*) FROM elections
  UNION ALL SELECT 'candidates', count(*) FROM candidates
  UNION ALL SELECT 'statements', count(*) FROM statements
  UNION ALL SELECT 'articles', count(*) FROM articles
  UNION ALL SELECT 'subscribers', count(*) FROM subscribers
  ORDER BY table_name;
"

echo ""
echo "=== Restore completed at $(date -u) ==="
