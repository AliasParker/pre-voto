#!/usr/bin/env bash
# =============================================================================
# pre.voto — Deploy Script
# Run from the VPS:  ssh deploy@VPS 'bash /opt/prevoto/infra/deploy.sh'
# Or locally on VPS: bash /opt/prevoto/infra/deploy.sh
#
# Ordering: API must be running before frontend build because Astro SSG
# calls the API during getStaticPaths() to enumerate countries, candidates,
# articles, etc. The frontend-builder service runs on the Docker network
# where it can reach http://api:8000.
# =============================================================================
set -euo pipefail

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"
APP_DIR="/opt/prevoto"
HEALTH_URL="https://pre.voto/api/health"
MAX_WAIT=60
HEALTH_INTERVAL=2

echo "=== pre.voto deploy started at $(date -u) ==="

# ---- 1. Pull latest code ----
echo "[1/8] Pulling latest code..."
cd "$APP_DIR"
git pull --ff-only
echo "  Code updated to $(git rev-parse --short HEAD)."

# ---- 2. Build all Docker images ----
echo "[2/8] Building Docker images..."
$COMPOSE --profile build build
echo "  Images built."

# ---- 3. Start API stack (postgres, redis, api, worker) ----
echo "[3/8] Starting API stack..."
$COMPOSE up -d postgres redis api worker
echo "  API stack started."

# ---- 4. Wait for API to be healthy ----
echo "[4/8] Waiting for API to be healthy..."
SECONDS_WAITED=0
while [ $SECONDS_WAITED -lt $MAX_WAIT ]; do
  STATUS=$($COMPOSE ps -q api 2>/dev/null | head -1 | xargs -I{} docker inspect --format='{{.State.Health.Status}}' {} 2>/dev/null || echo "starting")
  if [ "$STATUS" = "healthy" ]; then
    echo "  API is healthy."
    break
  fi
  echo "  Waiting... ($STATUS) [${SECONDS_WAITED}s]"
  sleep "$HEALTH_INTERVAL"
  SECONDS_WAITED=$((SECONDS_WAITED + HEALTH_INTERVAL))
done

if [ $SECONDS_WAITED -ge $MAX_WAIT ]; then
  echo "  ERROR: API did not become healthy within ${MAX_WAIT}s."
  echo "  Check logs: $COMPOSE logs api --tail=50"
  exit 1
fi

# ---- 5. Run database migrations ----
echo "[5/8] Running database migrations..."
$COMPOSE exec -T api alembic upgrade head
echo "  Migrations applied."

# ---- 6. Build frontend static site (API is now accessible) ----
echo "[6/8] Building frontend static site..."
$COMPOSE run --rm frontend-builder
echo "  Frontend built."

# ---- 7. Start remaining services (frontend, caddy) ----
echo "[7/8] Starting all services..."
$COMPOSE up -d
echo "  All services started."

# TODO: Uncomment when warmup script exists
# echo "[7b/8] Running warmup..."
# $COMPOSE exec -T api python -m app.scripts.warmup

# ---- 8. Health check via HTTPS ----
echo "[8/8] Running health check..."
sleep 3
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
  echo "  1. Check API logs:     $COMPOSE logs api --tail=50"
  echo "  2. Check Caddy logs:   $COMPOSE logs caddy --tail=50"
  echo "  3. Check DNS:          dig pre.voto +short"
  echo "  4. Test internally:    curl http://localhost:8000/health"
  echo ""
  echo "  To rollback:"
  echo "    cd $APP_DIR"
  echo "    git log --oneline -5   # find previous commit"
  echo "    git checkout <commit>"
  echo "    bash /opt/prevoto/infra/deploy.sh"
  echo "============================================================"
  exit 1
fi
