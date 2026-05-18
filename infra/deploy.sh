#!/usr/bin/env bash
# =============================================================================
# pre.voto — Deploy Script
# Run from the VPS:  ssh deploy@VPS 'bash /opt/prevoto/infra/deploy.sh'
# Or locally on VPS: bash /opt/prevoto/infra/deploy.sh
# =============================================================================
set -euo pipefail

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"
APP_DIR="/opt/prevoto"
HEALTH_URL="https://pre.voto/api/health"
HEALTH_RETRIES=30
HEALTH_INTERVAL=2

echo "=== pre.voto deploy started at $(date -u) ==="

# ---- 1. Pull latest code ----
echo "[1/6] Pulling latest code..."
cd "$APP_DIR"
git pull --ff-only
echo "  Code updated to $(git rev-parse --short HEAD)."

# ---- 2. Build images ----
echo "[2/6] Building Docker images..."
$COMPOSE build
echo "  Images built."

# ---- 3. Start services ----
echo "[3/6] Starting services..."
$COMPOSE up -d
echo "  Services started."

# ---- 4. Wait for API to be healthy ----
echo "[4/6] Waiting for API container to be healthy..."
SECONDS_WAITED=0
while [ $SECONDS_WAITED -lt $HEALTH_RETRIES ]; do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$(docker compose ps -q api 2>/dev/null)" 2>/dev/null || echo "starting")
  if [ "$STATUS" = "healthy" ]; then
    echo "  API container is healthy."
    break
  fi
  echo "  Waiting... ($STATUS) [${SECONDS_WAITED}s]"
  sleep "$HEALTH_INTERVAL"
  SECONDS_WAITED=$((SECONDS_WAITED + HEALTH_INTERVAL))
done

if [ $SECONDS_WAITED -ge $HEALTH_RETRIES ]; then
  echo "  WARNING: API did not become healthy within ${HEALTH_RETRIES}s."
  echo "  Continuing anyway — check logs: docker compose logs api"
fi

# ---- 5. Run migrations ----
echo "[5/6] Running database migrations..."
$COMPOSE exec -T api alembic upgrade head
echo "  Migrations applied."

# TODO: Uncomment when warmup script exists
# echo "[5b/6] Running warmup..."
# $COMPOSE exec -T api python -m app.scripts.warmup

# ---- 6. Health check via HTTPS ----
echo "[6/6] Running health check..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$HEALTH_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
  echo ""
  echo "============================================================"
  echo "  DEPLOY SUCCESSFUL"
  echo "============================================================"
  echo "  Commit:  $(git rev-parse --short HEAD)"
  echo "  Health:  $HEALTH_URL -> $HTTP_CODE"
  echo "  Time:    $(date -u)"
  echo "============================================================"
else
  echo ""
  echo "============================================================"
  echo "  DEPLOY WARNING — Health check failed (HTTP $HTTP_CODE)"
  echo "============================================================"
  echo ""
  echo "  The containers are running but the health endpoint"
  echo "  returned HTTP $HTTP_CODE instead of 200."
  echo ""
  echo "  Troubleshooting:"
  echo "  1. Check API logs:     docker compose logs api --tail=50"
  echo "  2. Check Caddy logs:   docker compose logs caddy --tail=50"
  echo "  3. Check DNS:          dig pre.voto +short"
  echo "  4. Test internally:    curl http://localhost:8000/health"
  echo ""
  echo "  To rollback:"
  echo "    cd $APP_DIR"
  echo "    git log --oneline -5   # find previous commit"
  echo "    git checkout <commit>"
  echo "    $COMPOSE up -d --build"
  echo "============================================================"
  exit 1
fi
