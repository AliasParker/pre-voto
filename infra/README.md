# pre.voto — Production Deployment Guide

Zero-to-production guide for deploying pre.voto on a Hetzner VPS with Cloudflare.

---

## Prerequisites

- **Hetzner account** — [console.hetzner.cloud](https://console.hetzner.cloud)
- **Cloudflare account** — [dash.cloudflare.com](https://dash.cloudflare.com)
- **Domain** — `pre.voto` added to Cloudflare
- **S3-compatible bucket** — for database backups (e.g. Cloudflare R2, AWS S3, MinIO)
- **Mac (or Linux)** — for running SSH commands locally
- **GitHub Personal Access Token (PAT)** — for cloning the repo during automated deploys (see below)

---

## 1. Generate GitHub PAT

The bootstrap script uses a GitHub Personal Access Token for automated cloning and deploys.

1. Go to **GitHub** → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**
2. Configure:
   - **Token name**: `prevoto-deploy`
   - **Expiration**: 1 year (you will need to rotate it — see [Rotating the PAT](#rotating-the-pat))
   - **Repository access**: Only select repositories → `AliasParker/pre-voto`
   - **Permissions**: Repository permissions → **Contents** → **Read-only** (nothing else)
3. Click **Generate token** and copy the value (starts with `github_pat_`)
4. Save it somewhere safe (password manager). You'll need it for the bootstrap command.

> **Security notes:**
> - The PAT is passed as an environment variable during bootstrap only — it is **not** stored in `.env` or any config file committed to the repo.
> - The bootstrap script stores it in `~deploy/.git-credentials` (chmod 600) so that `deploy.sh` can `git pull` for future deployments.
> - The PAT **never** appears in any git remote URL or log file.

---

## 2. Generate SSH Key

On your Mac:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/prevoto -C "deploy@pre.voto"
```

This creates:
- `~/.ssh/prevoto` — private key (keep safe, never share)
- `~/.ssh/prevoto.pub` — public key (paste into Hetzner)

Add to SSH config for convenience:

```bash
cat >> ~/.ssh/config <<'EOF'

Host prevoto
  HostName YOUR_VPS_IP
  User deploy
  IdentityFile ~/.ssh/prevoto
EOF
```

---

## 3. Create VPS on Hetzner

1. Go to [Hetzner Cloud Console](https://console.hetzner.cloud) > **New Project** > "pre.voto"
2. **Add Server**:
   - **Location**: Ashburn or Falkenstein (closest to your users)
   - **Image**: Ubuntu 24.04
   - **Type**: CX22 (2 vCPU, 4 GB RAM, 40 GB disk) — sufficient for launch
   - **SSH Key**: Paste contents of `~/.ssh/prevoto.pub`
   - **Name**: `prevoto-prod`
3. Note the IP address.

---

## 4. Bootstrap the VPS

From your Mac, run the bootstrap script on the fresh VPS. Pass the GitHub PAT as an environment variable:

```bash
GITHUB_DEPLOY_PAT="github_pat_xxx" \
  ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP 'sudo -E bash -s' < infra/bootstrap-vps.sh
```

> `-E` preserves environment variables through `sudo` so the script can read `GITHUB_DEPLOY_PAT`.

This will:
- Create `deploy` user with your SSH key
- Harden SSH (disable root login, password auth)
- Configure firewall (ports 22, 80, 443)
- Install Docker, rclone, unattended-upgrades
- Clone the repo to `/opt/prevoto` (using the PAT for authentication)
- Store git credentials in `~deploy/.git-credentials` for future pulls
- Create `.env` from the production template
- Configure 2GB swap, UTC timezone

After bootstrap completes, **root SSH is disabled**. Use the `deploy` user from now on:

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP
```

---

## 5. Cloudflare Setup

### 4.1 DNS

1. Go to **Cloudflare Dashboard** > **pre.voto** > **DNS** > **Records**
2. Add records:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | `pre.voto` | `YOUR_VPS_IP` | Proxied (orange cloud) |
| A | `www` | `YOUR_VPS_IP` | Proxied (orange cloud) |

3. Ensure Cloudflare nameservers are set at your domain registrar:
   - Check: `dig pre.voto NS +short` (should show Cloudflare nameservers)

### 4.2 SSL/TLS

1. **SSL/TLS** > **Overview** > Set mode to **Full (strict)**
2. **SSL/TLS** > **Origin Server** > **Create Certificate**:
   - Private key type: RSA (2048)
   - Hostnames: `pre.voto`, `*.pre.voto`
   - Validity: 15 years
   - Click **Create**
3. Save the certificate as `origin.crt` and the key as `origin.key` on your Mac

### 4.3 Install Origin Certificate on VPS

```bash
# Copy certificate files to VPS
scp -i ~/.ssh/prevoto origin.crt deploy@YOUR_VPS_IP:/tmp/
scp -i ~/.ssh/prevoto origin.key deploy@YOUR_VPS_IP:/tmp/

# SSH into VPS and move to Caddy directory
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP

sudo mkdir -p /etc/caddy
sudo mv /tmp/origin.crt /etc/caddy/origin.crt
sudo mv /tmp/origin.key /etc/caddy/origin.key
sudo chmod 644 /etc/caddy/origin.crt
sudo chmod 600 /etc/caddy/origin.key
```

### 4.4 Cache Rules

Go to **Caching** > **Cache Rules** > **Create rule**:

**Rule 1 — Cache static assets (1 year)**:
- If: `URI Path` contains `/_astro/` OR `URI Path` contains `/fonts/` OR `URI Path` contains `/og/`
- Then: Cache eligible, Edge TTL = 1 year

**Rule 2 — Cache HTML (5 min)**:
- If: `URI Path` does not start with `/api/`
- Then: Cache eligible, Edge TTL = 5 minutes
- Cache status code: 200

**Rule 3 — Bypass cache for API**:
- If: `URI Path` starts with `/api/`
- Then: Bypass cache

### 4.5 WAF Rate Limiting

Go to **Security** > **WAF** > **Rate limiting rules** > **Create rule**:

- Name: "API rate limit"
- If: `URI Path` starts with `/api/`
- Rate: 100 requests per minute per IP
- Action: Block for 60 seconds

### 4.6 Performance

- **Speed** > **Optimization** > **Content Optimization** > Enable **Brotli**
- **Security** > **Settings** > Security level: **Medium**

---

## 6. Configure Environment

SSH into the VPS and edit the environment file:

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP
nano /opt/prevoto/.env
```

Required changes:

```bash
# Generate secure passwords:
openssl rand -base64 32  # Run this 2x, one for PG password, one for admin key

# Update these lines in .env:
POSTGRES_PASSWORD=<generated-password-1>
DATABASE_URL=postgresql+asyncpg://prevoto:<generated-password-1>@postgres:5432/prevoto
ADMIN_API_KEY=<generated-password-2>

# Set R2 credentials (from Cloudflare Dashboard > R2 > Manage R2 API Tokens):
CLOUDFLARE_R2_ACCESS_KEY=<your-r2-access-key>
CLOUDFLARE_R2_SECRET_KEY=<your-r2-secret-key>
CLOUDFLARE_R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com

# Set SMTP if using email features:
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
```

---

## 7. First Deploy

From your Mac:

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP 'bash /opt/prevoto/infra/deploy.sh'
```

The script will:
1. Pull latest code
2. Build Docker images
3. Start all services
4. Wait for API health
5. Run database migrations
6. Health-check `https://pre.voto/api/health`

### Seed Demo Data

After the first deploy:

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP \
  'cd /opt/prevoto && docker compose exec -T api python -m app.scripts.seed_colombia_2026'
```

### Verify

```bash
curl -s https://pre.voto/api/health
# Expected: {"status":"ok"}

curl -s -o /dev/null -w "%{http_code}" https://pre.voto/
# Expected: 200
```

---

## 8. Backup Cron

Set up daily automated backups at 3 AM UTC:

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP

# Open crontab
crontab -e

# Add this line:
0 3 * * * /opt/prevoto/infra/backup-postgres.sh >> /var/log/prevoto-backup.log 2>&1
```

Verify the cron is set:

```bash
crontab -l
```

### Manual Backup

```bash
bash /opt/prevoto/infra/backup-postgres.sh
```

### Restore from Backup

```bash
# List available backups
bash /opt/prevoto/infra/restore-postgres.sh

# Restore specific date
bash /opt/prevoto/infra/restore-postgres.sh 20260518
```

---

## 9. Monitoring

### UptimeRobot (free tier)

1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. **Add New Monitor**:
   - Type: HTTP(s)
   - URL: `https://pre.voto/api/health`
   - Interval: 5 minutes
   - Alert contact: your email

### Log Rotation

Docker logs are rotated automatically with the default json-file driver. To check logs:

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP

# API logs
cd /opt/prevoto && docker compose logs api --tail=100

# All services
cd /opt/prevoto && docker compose logs --tail=50

# Follow logs in real time
cd /opt/prevoto && docker compose logs -f api caddy
```

---

## 10. Routine Operations

### Deploy an Update

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP 'bash /opt/prevoto/infra/deploy.sh'
```

### Restart a Service

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP 'cd /opt/prevoto && docker compose restart api'
```

### Run a One-Off Command

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP \
  'cd /opt/prevoto && docker compose exec -T api python -c "from app.config import settings; print(settings.env)"'
```

### Check Disk Space

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP 'df -h / && docker system df'
```

### Prune Docker (reclaim disk)

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP 'docker system prune -af --volumes'
```

---

## 11. Rotating the PAT

The GitHub PAT expires after 1 year. When it expires, `deploy.sh` will fail on `git pull`. To rotate:

1. Generate a new fine-grained PAT in GitHub (same settings as step 1)
2. SSH into the VPS and update the credential file:

```bash
ssh -i ~/.ssh/prevoto deploy@YOUR_VPS_IP

# Replace the credential (the file has exactly one line)
echo "https://oauth2:NEW_PAT_HERE@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
```

3. Verify it works:

```bash
cd /opt/prevoto && git pull --ff-only
```

4. Delete the old PAT in GitHub → Settings → Developer settings → Personal access tokens

> **Reminder:** Set a calendar reminder for 11 months from now to rotate before expiration.

---

## 12. Troubleshooting

### DNS propagation delay

**Symptom**: `curl https://pre.voto` times out or resolves to wrong IP.

```bash
dig pre.voto +short
# Should return Cloudflare IPs (104.x.x.x or 172.x.x.x)

dig pre.voto +short @8.8.8.8
# Compare with Cloudflare dashboard
```

**Fix**: Wait up to 24h for DNS propagation. Ensure nameservers are pointed to Cloudflare at the registrar. Flush local DNS: `sudo dscacheutil -flushcache` (macOS).

### Origin certificate mismatch

**Symptom**: 526 error in browser, or "SSL handshake failed" in Caddy logs.

```bash
# Check certificate on VPS
ssh deploy@YOUR_VPS_IP 'sudo openssl x509 -in /etc/caddy/origin.crt -text -noout | grep -A1 "Subject Alternative"'
# Should include pre.voto and *.pre.voto

# Check Caddy logs
ssh deploy@YOUR_VPS_IP 'cd /opt/prevoto && docker compose logs caddy --tail=20'
```

**Fix**: Regenerate origin certificate in Cloudflare ensuring both `pre.voto` and `*.pre.voto` are included. Re-copy to VPS.

### Firewall blocking

**Symptom**: Connection refused when accessing the VPS directly.

```bash
ssh deploy@YOUR_VPS_IP 'sudo ufw status verbose'
# Should show 22, 80, 443 ALLOW

# Test from VPS internally
ssh deploy@YOUR_VPS_IP 'curl -v http://localhost:80'
```

**Fix**: `sudo ufw allow 80/tcp && sudo ufw allow 443/tcp`.

### Alembic migration stuck

**Symptom**: `alembic upgrade head` hangs or errors with lock.

```bash
# Check current migration state
ssh deploy@YOUR_VPS_IP 'cd /opt/prevoto && docker compose exec -T api alembic current'

# Check for PostgreSQL locks
ssh deploy@YOUR_VPS_IP 'cd /opt/prevoto && docker compose exec -T postgres psql -U prevoto -c "SELECT * FROM pg_locks WHERE NOT granted;"'
```

**Fix**: If locked, restart postgres: `docker compose restart postgres`, then retry migrations.

### OOM killer (out of memory)

**Symptom**: Containers randomly restarting, `dmesg` shows OOM.

```bash
ssh deploy@YOUR_VPS_IP 'sudo dmesg | grep -i oom | tail -5'
ssh deploy@YOUR_VPS_IP 'free -h'
```

**Fix**:
1. Ensure swap exists: `swapon --show`
2. Reduce API workers in `docker-compose.prod.yml` (default is 2)
3. Consider upgrading VPS to CX32 (8 GB RAM)
