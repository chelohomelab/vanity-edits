#!/usr/bin/env bash
# The Vanity Edit — Proxmox LXC setup script
# Usage:
#   cd /opt
#   git clone https://github.com/chelohomelab/vanity-edits.git
#   cd vanity-edits
#   bash proxmox-setup.sh

set -euo pipefail

APP_DIR="/opt/vanity-edits"
SERVICE="vanity-edits"

echo "==> The Vanity Edit — Setup"
echo ""

# ── System packages ────────────────────────────────────────────────────────────
echo "==> Installing system packages…"
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv gcc python3-dev libffi-dev

# ── Virtual environment & dependencies ─────────────────────────────────────────
echo "==> Creating virtual environment…"
python3 -m venv "$APP_DIR/venv"

echo "==> Installing dependencies…"
"$APP_DIR/venv/bin/pip" install --no-cache-dir -r "$APP_DIR/requirements.txt"

# ── Verify uvicorn installed ───────────────────────────────────────────────────
if [ ! -x "$APP_DIR/venv/bin/uvicorn" ]; then
  echo ""
  echo "ERROR: uvicorn was not installed correctly."
  echo "       Check the pip output above for errors."
  exit 1
fi
echo "==> uvicorn OK"

# ── Data directories ──────────────────────────────────────────────────────────
mkdir -p "$APP_DIR/data" "$APP_DIR/static/uploads" "$APP_DIR/static/backgrounds"

# ── systemd service ───────────────────────────────────────────────────────────
echo "==> Installing systemd service…"
cp "$APP_DIR/vanity-edits.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable "$SERVICE"
systemctl start "$SERVICE"

echo ""
echo "==> Setup complete!"
echo ""
echo "    Visit http://$(hostname -I | awk '{print $1}'):8000/setup to create your admin account."
echo ""
echo "    Logs    : journalctl -u $SERVICE -f"
echo "    Status  : systemctl status $SERVICE"
echo "    Restart : systemctl restart $SERVICE"
echo ""
echo "    To update later:"
echo "      cd $APP_DIR && git pull"
echo "      venv/bin/pip install --no-cache-dir -r requirements.txt"
echo "      systemctl restart $SERVICE"
