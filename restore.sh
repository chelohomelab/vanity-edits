#!/usr/bin/env bash
# The Vanity Edit — Restore script
# Restores database and photos from a backup archive.
#
# Usage:
#   bash /opt/vanity-edits/restore.sh /path/to/vanity-edit-backup-YYYYMMDD_HHMMSS.tar.gz
#
# The app should be stopped before restoring:
#   systemctl stop vanity-edits
#   bash /opt/vanity-edits/restore.sh <backup-file>
#   systemctl start vanity-edits

set -euo pipefail

APP_DIR="/opt/vanity-edits"
SERVICE="vanity-edits"

if [ $# -eq 0 ]; then
  echo "Usage: bash restore.sh <backup-archive>"
  echo ""
  # List available backups
  if ls "$APP_DIR/backups"/vanity-edit-backup-*.tar.gz &>/dev/null; then
    echo "Available backups:"
    ls -1th "$APP_DIR/backups"/vanity-edit-backup-*.tar.gz | while read f; do
      SIZE=$(du -h "$f" | cut -f1)
      NAME=$(basename "$f")
      echo "  $NAME  ($SIZE)"
    done
  else
    echo "No backups found in $APP_DIR/backups/"
  fi
  exit 1
fi

ARCHIVE="$1"

if [ ! -f "$ARCHIVE" ]; then
  echo "ERROR: File not found: $ARCHIVE"
  exit 1
fi

echo "==> The Vanity Edit — Restore"
echo "    Archive : $ARCHIVE"
echo "    Target  : $APP_DIR"
echo ""

# Show what's in the archive
echo "    Contents:"
tar -tzf "$ARCHIVE" | head -20
TOTAL=$(tar -tzf "$ARCHIVE" | wc -l)
if [ "$TOTAL" -gt 20 ]; then
  echo "    ... and $((TOTAL - 20)) more files"
fi
echo ""

# Confirm
read -p "    This will overwrite existing data. Continue? [y/N] " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "    Aborted."
  exit 0
fi

# Stop service if running
if systemctl is-active --quiet "$SERVICE" 2>/dev/null; then
  echo "==> Stopping $SERVICE…"
  systemctl stop "$SERVICE"
  RESTART=true
else
  RESTART=false
fi

# Restore
echo "==> Restoring files…"
tar -xzf "$ARCHIVE" -C "$APP_DIR"

echo "==> Restore complete"

# Restart if it was running
if [ "$RESTART" = true ]; then
  echo "==> Starting $SERVICE…"
  systemctl start "$SERVICE"
fi

echo ""
echo "==> Done. Your data has been restored."
