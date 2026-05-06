# Minimal VPS Deployment Runbook

This runbook is for the current MVP only. It does not replace production security hardening.

## Prerequisites
- Ubuntu VPS with Python 3.11+.
- Non-root deploy user with sudo access.
- Reverse proxy (Nginx or Caddy) terminating HTTPS.
- Firewall open only for SSH and HTTPS.

## App Setup
```bash
cd /opt
sudo mkdir -p bale-bot
sudo chown -R $USER:$USER bale-bot
cd bale-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in project root:
```env
BALE_BOT_TOKEN=...
BALE_API_BASE_URL=...
DATABASE_PATH=/opt/bale-bot/data/bale_bot.db
```

Create data directory:
```bash
mkdir -p /opt/bale-bot/data
```

## Start Command
```bash
source /opt/bale-bot/.venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Use reverse proxy to expose HTTPS and forward to `127.0.0.1:8000`.

## Systemd Service Template
```ini
[Unit]
Description=Bale Pharmacy Bot
After=network.target

[Service]
User=<deploy-user>
WorkingDirectory=/opt/bale-bot
EnvironmentFile=/opt/bale-bot/.env
ExecStart=/opt/bale-bot/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## Operations
- Restart: `sudo systemctl restart bale-bot`
- Status: `sudo systemctl status bale-bot`
- Logs: `sudo journalctl -u bale-bot -f`

## Backup and Rollback Basics
- Back up SQLite file regularly: `/opt/bale-bot/data/bale_bot.db`.
- Keep release snapshots or tagged commits.
- Roll back by checking out previous commit and restarting service.

## Deployment Blockers Before Public Exposure
- Confirm Bale webhook authentication/signature validation.
- Confirm exact Bale webhook and send-message schemas.
- Verify reverse proxy TLS and request size/timeouts for webhook traffic.
