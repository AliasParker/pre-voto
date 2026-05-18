#!/usr/bin/env bash
# =============================================================================
# pre.voto — VPS Bootstrap Script
# Idempotent setup for a fresh Ubuntu 24.04 (Hetzner CX22 or similar)
# Run as root: ssh root@IP 'bash -s' < infra/bootstrap-vps.sh
# =============================================================================
set -euo pipefail

LOG="/var/log/prevoto-bootstrap.log"
exec > >(tee -a "$LOG") 2>&1
echo "=== pre.voto bootstrap started at $(date -u) ==="

# ---- 1. System update ----
echo "[1/12] Updating system packages..."
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq

# ---- 2. Create deploy user ----
echo "[2/12] Creating deploy user..."
if id -u deploy &>/dev/null; then
  echo "  User 'deploy' already exists, skipping."
else
  adduser --disabled-password --gecos "" deploy
  usermod -aG sudo deploy
  # Allow sudo without password
  echo "deploy ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/deploy
  chmod 440 /etc/sudoers.d/deploy
  # Copy root's authorized_keys to deploy
  mkdir -p /home/deploy/.ssh
  cp /root/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
  chown -R deploy:deploy /home/deploy/.ssh
  chmod 700 /home/deploy/.ssh
  chmod 600 /home/deploy/.ssh/authorized_keys
  echo "  User 'deploy' created with SSH keys from root."
fi

# ---- 3. Harden SSH ----
echo "[3/12] Hardening SSH..."
SSHD_CONFIG="/etc/ssh/sshd_config"
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' "$SSHD_CONFIG"
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' "$SSHD_CONFIG"
sed -i 's/^#\?KbdInteractiveAuthentication.*/KbdInteractiveAuthentication no/' "$SSHD_CONFIG"
# Keep UsePAM yes — Ubuntu relies on PAM for systemd-logind sessions,
# MOTD, /etc/environment, and ulimits. Disabling it breaks those.
sed -i 's/^#\?UsePAM.*/UsePAM yes/' "$SSHD_CONFIG"
systemctl restart ssh
echo "  SSH hardened: root login disabled, password auth disabled."

# ---- 4. Configure UFW ----
echo "[4/12] Configuring firewall..."
if ! command -v ufw &>/dev/null; then
  apt-get install -y -qq ufw
fi
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment "SSH"
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"
ufw --force enable
echo "  UFW enabled: 22, 80, 443 allowed."

# ---- 5. Install Docker CE ----
echo "[5/12] Installing Docker..."
if command -v docker &>/dev/null; then
  echo "  Docker already installed: $(docker --version)"
else
  apt-get install -y -qq ca-certificates curl
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  echo "  Docker installed: $(docker --version)"
fi

# ---- 6. Add deploy to docker group ----
echo "[6/12] Adding deploy to docker group..."
usermod -aG docker deploy
echo "  deploy added to docker group."

# ---- 7. Install rclone ----
echo "[7/12] Installing rclone..."
if command -v rclone &>/dev/null; then
  echo "  rclone already installed: $(rclone version | head -1)"
else
  curl -fsSL https://rclone.org/install.sh | bash
  echo "  rclone installed: $(rclone version | head -1)"
fi

# Create rclone config for R2 (deploy user)
# The actual credentials must be set in /opt/prevoto/.env
# This creates a skeleton config; deploy.sh reads .env at runtime
RCLONE_DIR="/home/deploy/.config/rclone"
mkdir -p "$RCLONE_DIR"
if [ ! -f "$RCLONE_DIR/rclone.conf" ]; then
  cat > "$RCLONE_DIR/rclone.conf" <<'RCLONE_EOF'
[r2]
type = s3
provider = Cloudflare
env_auth = false
# These are populated by the backup script from /opt/prevoto/.env
# access_key_id and secret_access_key are passed via environment variables
# endpoint is passed via environment variable
RCLONE_EOF
  chown -R deploy:deploy /home/deploy/.config
  echo "  rclone config skeleton created."
else
  echo "  rclone config already exists, skipping."
fi

# ---- 8. Unattended upgrades ----
echo "[8/12] Configuring unattended upgrades..."
apt-get install -y -qq unattended-upgrades
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF
echo "  Unattended upgrades configured (security-only)."

# ---- 9. Create swap ----
echo "[9/12] Configuring swap..."
if swapon --show | grep -q "/swapfile"; then
  echo "  Swap already active, skipping."
else
  if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
  fi
  swapon /swapfile
  if ! grep -q "/swapfile" /etc/fstab; then
    echo "/swapfile none swap sw 0 0" >> /etc/fstab
  fi
  echo "  2GB swap configured."
fi

# ---- 10. Set timezone to UTC ----
echo "[10/12] Setting timezone to UTC..."
timedatectl set-timezone UTC
echo "  Timezone set to UTC."

# ---- 11. Clone repository ----
echo "[11/12] Setting up /opt/prevoto..."
if [ -d /opt/prevoto/.git ]; then
  echo "  Repository already cloned, pulling latest..."
  cd /opt/prevoto
  git pull --ff-only || echo "  Warning: git pull failed, continuing with existing code."
else
  mkdir -p /opt/prevoto
  git clone https://github.com/AliasParker/prevoto.git /opt/prevoto
fi
chown -R deploy:deploy /opt/prevoto
echo "  /opt/prevoto ready."

# ---- 12. Copy env template ----
echo "[12/12] Setting up environment file..."
if [ ! -f /opt/prevoto/.env ]; then
  cp /opt/prevoto/infra/.env.production.template /opt/prevoto/.env
  chown deploy:deploy /opt/prevoto/.env
  chmod 600 /opt/prevoto/.env
  echo "  .env created from template — EDIT IT BEFORE DEPLOYING."
else
  echo "  .env already exists, skipping (not overwriting)."
fi

# ---- Done ----
echo ""
echo "============================================================"
echo "  BOOTSTRAP COMPLETE"
echo "============================================================"
echo ""
echo "  NEXT STEPS:"
echo ""
echo "  1. SSH in as deploy:  ssh deploy@$(hostname -I | awk '{print $1}')"
echo "  2. Edit .env:         nano /opt/prevoto/.env"
echo "     - Set real POSTGRES_PASSWORD, ADMIN_API_KEY"
echo "     - Set Cloudflare R2 credentials"
echo "     - Set SMTP credentials (if using email)"
echo "     - Set PUBLIC_API_URL=https://pre.voto"
echo "     - Set PUBLIC_SITE_URL=https://pre.voto"
echo "  3. Install origin certificate:"
echo "     scp origin.crt deploy@VPS:/tmp/"
echo "     scp origin.key deploy@VPS:/tmp/"
echo "     sudo mkdir -p /etc/caddy"
echo "     sudo mv /tmp/origin.crt /tmp/origin.key /etc/caddy/"
echo "     sudo chmod 644 /etc/caddy/origin.crt"
echo "     sudo chmod 600 /etc/caddy/origin.key"
echo "  4. Deploy:            bash /opt/prevoto/infra/deploy.sh"
echo "  5. Seed data:         cd /opt/prevoto && docker compose exec -T api python -m app.scripts.seed_colombia_2026"
echo ""
echo "  Log saved to: $LOG"
echo "============================================================"
