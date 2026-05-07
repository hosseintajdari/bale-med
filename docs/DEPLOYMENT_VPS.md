# Minimal VPS Deployment Runbook

This runbook is for the current MVP only. It does not replace production security hardening.

## Milestone 7 Checklist

Milestone 7 is preparation only. Do not deploy to a real VPS, change DNS, configure SSL, edit firewall rules, register a production webhook, or enable real outgoing Bale messages until Milestone 8 is explicitly approved.

Work through these pieces in order:

1. Confirm target server basics: Ubuntu VPS, SSH access, non-root deploy user, Python 3.11+, and a stable domain or HTTPS endpoint.
2. Confirm secret handling: real values stay only in `.env` on the server, never in Git, screenshots, logs, or chat.
3. Confirm safe environment defaults: `BALE_ENABLE_SENDING=false`, strong `BALE_WEBHOOK_SECRET`, and `DATABASE_PATH=/opt/bale-bot/data/bale_bot.db`.
4. Confirm app run path: repo files under `/opt/bale-bot`, virtual environment under `/opt/bale-bot/.venv`, and uvicorn bound only to `127.0.0.1:8000`.
5. Choose reverse proxy approach: Nginx or Caddy terminates HTTPS and forwards requests to `127.0.0.1:8000`.
6. Confirm storage and backup: SQLite file lives in `/opt/bale-bot/data`, backup location is known, and restore steps are tested before broad use.
7. Confirm operations commands: restart, status, logs, health check, webhook smoke test, rollback.
8. Confirm deployment blockers are resolved before Milestone 8 starts.

## Prerequisites
- Ubuntu VPS with Python 3.11+.
- Non-root deploy user with sudo access.
- Reverse proxy (Nginx or Caddy) terminating HTTPS.
- Firewall open only for SSH and HTTPS.
- A stable domain or HTTPS endpoint for Bale webhook delivery.

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
BALE_API_BASE_URL=https://tapi.bale.ai
BALE_ENABLE_SENDING=false
BALE_REPLY_TEXT=پیام شما دریافت شد. این ربات جایگزین نظر داروساز نیست و در صورت نیاز توسط داروساز بررسی میشود.
DATABASE_PATH=/opt/bale-bot/data/bale_bot.db
BALE_WEBHOOK_SECRET=...
```

Keep `BALE_ENABLE_SENDING=false` until webhook schema, send-message behavior, and pharmacist safety flow are verified.

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

Public webhook path format:
```text
https://your-domain.example/webhook/bale/YOUR_SECRET
```

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
- Confirm Bale webhook authentication/signature validation beyond secret-path protection, if Bale supports it.
- Confirm exact Bale webhook and send-message schemas.
- Verify reverse proxy TLS and request size/timeouts for webhook traffic.
- Verify `BALE_WEBHOOK_SECRET` is strong and not committed to Git.
- Keep `BALE_ENABLE_SENDING=false` until real sending is intentionally approved.
- Verify backup and restore steps for the SQLite database.
- Confirm sanitized logs still do not include tokens, secrets, raw payloads, chat ids, or full message text.
