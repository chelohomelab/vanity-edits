# The Vanity Edit

A self-hosted beauty collection tracker for makeup, perfumes, and nail polish.

**Stack:** FastAPI · SQLite · Jinja2 · Tailwind CSS

---

## Features

| Feature | Details |
|---|---|
| Inventory | Makeup, Perfumes, and Nail Polish with category-specific fields |
| Status tracking | New → Open → Finished per item |
| Sub-categories | Makeup: Lips / Eyes / Face — Nail Polish: Nudes / Pinks / Reds / Sheers / Other |
| Photo management | 2 image slots per item — upload from gallery or take with camera |
| Autocomplete | Brand, name, and shade suggestions from existing collection |
| Multi-user | Cookie-based sessions, remember-me, admin panel |
| Soft delete | Trash with restore / permanent delete |
| PWA | Installable on phone home screen with custom icon |
| Backup / Restore | One-command disaster recovery scripts |

---

## Local Development

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit **http://localhost:8000** — you'll be sent to `/setup` on first run to create your admin account.

---

## Proxmox LXC Deployment

### Prerequisites

A Debian or Ubuntu LXC container in Proxmox (unprivileged is fine) with SSH access.

Before running the setup script, update and install git:

```bash
apt-get update && apt-get upgrade -y
apt-get install -y git
```

### Install

```bash
cd /opt
git clone https://github.com/chelohomelab/vanity-edits.git
cd vanity-edits
bash proxmox-setup.sh
```

Visit `http://<lxc-ip>:8000/setup` to create your admin account.

### Updating

```bash
cd /opt/vanity-edits
git pull
venv/bin/pip install --no-cache-dir -r requirements.txt
systemctl restart vanity-edits
```

### Service Commands

```bash
systemctl status  vanity-edits
systemctl restart vanity-edits
systemctl stop    vanity-edits
journalctl -u     vanity-edits -f
```

---

## Data

| Path | Contents |
|---|---|
| `data/vanity.db` | SQLite database |
| `static/uploads/` | Item photos |

Back these up to preserve your collection data across reinstalls.

---

## Backup & Restore

### Manual Backup

```bash
bash /opt/vanity-edits/backup.sh
```

Creates a timestamped archive (`vanity-edit-backup-YYYYMMDD_HHMMSS.tar.gz`) containing the database and all photos. Saved to `/opt/vanity-edits/backups/` by default.

To save to a different location:

```bash
bash /opt/vanity-edits/backup.sh /mnt/backups
```

Only the last 7 backups are kept automatically.

### Automated Daily Backup

```bash
crontab -e
```

Add this line to run a backup every day at 2 AM:

```
0 2 * * * bash /opt/vanity-edits/backup.sh
```

### Restore from Backup

List available backups:

```bash
bash /opt/vanity-edits/restore.sh
```

Restore a specific backup:

```bash
bash /opt/vanity-edits/restore.sh /opt/vanity-edits/backups/vanity-edit-backup-20260620_020000.tar.gz
```

The script will stop the service, restore the database and photos, and restart the service automatically.

### Disaster Recovery (Full Rebuild)

If the LXC container is lost and you need to rebuild from scratch:

1. Create a new Debian/Ubuntu LXC container in Proxmox
2. Update the system and install git:
   ```bash
   apt-get update && apt-get upgrade -y
   apt-get install -y git
   ```
3. Clone and install:
   ```bash
   cd /opt
   git clone https://github.com/chelohomelab/vanity-edits.git
   cd vanity-edits
   bash proxmox-setup.sh
   ```
4. Stop the service:
   ```bash
   systemctl stop vanity-edits
   ```
5. Copy your backup archive to the server and restore:
   ```bash
   bash /opt/vanity-edits/restore.sh /path/to/vanity-edit-backup-YYYYMMDD_HHMMSS.tar.gz
   ```
6. The restore script starts the service automatically. Verify:
   ```bash
   systemctl status vanity-edits
   ```

Your collection, accounts, and photos will be exactly as they were.

---

## Default Port

**8000** — edit the `ExecStart` line in `/etc/systemd/system/vanity-edits.service` to change it, then `systemctl daemon-reload && systemctl restart vanity-edits`.
