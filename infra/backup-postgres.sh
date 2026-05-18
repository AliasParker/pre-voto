#!/usr/bin/env bash
# =============================================================================
# pre.voto — PostgreSQL Backup to Cloudflare R2
# Cron: 0 3 * * * /opt/prevoto/infra/backup-postgres.sh >> /var/log/prevoto-backup.log 2>&1
# =============================================================================
set -euo pipefail

APP_DIR="/opt/prevoto"
ENV_FILE="$APP_DIR/.env"
BACKUP_NAME="$(date +%Y%m%d).sql.gz"
RETENTION_DAYS=30

echo "=== Backup started at $(date -u) ==="

# ---- Load R2 credentials from .env ----
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found."
  exit 1
fi

# Source only the R2 variables we need
CLOUDFLARE_R2_ACCESS_KEY=$(grep -E '^CLOUDFLARE_R2_ACCESS_KEY=' "$ENV_FILE" | cut -d= -f2-)
CLOUDFLARE_R2_SECRET_KEY=$(grep -E '^CLOUDFLARE_R2_SECRET_KEY=' "$ENV_FILE" | cut -d= -f2-)
CLOUDFLARE_R2_ENDPOINT=$(grep -E '^CLOUDFLARE_R2_ENDPOINT=' "$ENV_FILE" | cut -d= -f2-)
CLOUDFLARE_R2_BUCKET=$(grep -E '^CLOUDFLARE_R2_BUCKET=' "$ENV_FILE" | cut -d= -f2- || echo "prevoto-backups")

if [ -z "$CLOUDFLARE_R2_ACCESS_KEY" ] || [ -z "$CLOUDFLARE_R2_SECRET_KEY" ] || [ -z "$CLOUDFLARE_R2_ENDPOINT" ]; then
  echo "ERROR: R2 credentials not set in $ENV_FILE."
  exit 1
fi

# ---- Export rclone env vars ----
export RCLONE_CONFIG_R2_TYPE="s3"
export RCLONE_CONFIG_R2_PROVIDER="Cloudflare"
export RCLONE_CONFIG_R2_ACCESS_KEY_ID="$CLOUDFLARE_R2_ACCESS_KEY"
export RCLONE_CONFIG_R2_SECRET_ACCESS_KEY="$CLOUDFLARE_R2_SECRET_KEY"
export RCLONE_CONFIG_R2_ENDPOINT="$CLOUDFLARE_R2_ENDPOINT"
export RCLONE_CONFIG_R2_NO_CHECK_BUCKET="true"

# ---- Dump and upload ----
echo "Dumping database and uploading to r2:$CLOUDFLARE_R2_BUCKET/$BACKUP_NAME..."
cd "$APP_DIR"
docker compose exec -T postgres pg_dump -U prevoto prevoto | gzip | rclone rcat "r2:$CLOUDFLARE_R2_BUCKET/$BACKUP_NAME"
echo "Backup uploaded: $BACKUP_NAME"

# ---- Retention: delete backups older than 30 days ----
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
rclone delete --min-age "${RETENTION_DAYS}d" "r2:$CLOUDFLARE_R2_BUCKET/"
echo "Retention cleanup done."

echo "=== Backup completed at $(date -u) ==="
