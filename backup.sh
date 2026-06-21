#!/usr/bin/env bash
# The Vanity Edit — Backup script
# Creates a timestamped archive of the database and uploaded photos.
#
# Usage:
#   bash /opt/vanity-edits/backup.sh
#   bash /opt/vanity-edits/backup.sh /mnt/backups   # custom destination
#
# Automate with cron (daily at 2 AM):
#   0 2 * * * bash /opt/vanity-edits/backup.sh /mnt/backups

set -euo pipefail

APP_DIR="/opt/vanity-edits"
BACKUP_DIR="${1:-/opt/vanity-edits/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE="vanity-edit-backup-${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "==> The Vanity Edit — Backup"
echo "    Source  : $APP_DIR"
echo "    Dest    : $BACKUP_DIR/$ARCHIVE"
echo ""

# Build list of files to include
FILES_TO_BACKUP=""

if [ -f "$APP_DIR/data/vanity.db" ]; then
  FILES_TO_BACKUP="$FILES_TO_BACKUP data/vanity.db"
  echo "    [+] Database"
else
  echo "    [ ] Database (not found — skipping)"
fi

if [ -d "$APP_DIR/static/uploads" ] && [ "$(ls -A "$APP_DIR/static/uploads" 2>/dev/null)" ]; then
  FILES_TO_BACKUP="$FILES_TO_BACKUP static/uploads/"
  PHOTO_COUNT=$(find "$APP_DIR/static/uploads" -type f | wc -l)
  echo "    [+] Photos ($PHOTO_COUNT files)"
else
  echo "    [ ] Photos (none found — skipping)"
fi

if [ -z "$FILES_TO_BACKUP" ]; then
  echo ""
  echo "    Nothing to back up."
  exit 0
fi

tar -czf "$BACKUP_DIR/$ARCHIVE" -C "$APP_DIR" $FILES_TO_BACKUP

SIZE=$(du -h "$BACKUP_DIR/$ARCHIVE" | cut -f1)
echo ""
echo "==> Backup complete: $ARCHIVE ($SIZE)"

# Keep only the last 7 backups
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/vanity-edit-backup-*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 7 ]; then
  REMOVE_COUNT=$((BACKUP_COUNT - 7))
  ls -1t "$BACKUP_DIR"/vanity-edit-backup-*.tar.gz | tail -n "$REMOVE_COUNT" | xargs rm -f
  echo "    Pruned $REMOVE_COUNT old backup(s), keeping last 7"
fi
