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
6. Confirm storage and backup: SQLite file lives in `/opt/bale-bot/data`, local backup command is tested, backup location is known, and restore steps are tested before broad use.
7. Confirm operations commands: restart, status, logs, health check, webhook smoke test, rollback.
8. Confirm deployment blockers are resolved before Milestone 8 starts.

## Final Go/No-Go Checklist Before Milestone 8

Use this checklist as the final documentation gate before real VPS deployment starts. If any blocker is unresolved, do not start Milestone 8.

### Ready for Milestone 8 Planning
- Duplicate webhook delivery guard exists for stable update identifiers.
- Local pharmacist review listing and mark-reviewed action exist.
- Local SQLite backup helper exists and the backup command is documented.
- Local SQLite restore helper exists and refuses overwrite by default.
- Environment values are documented with placeholders, not real secrets.
- `BALE_ENABLE_SENDING=false` is the required first VPS deployment setting.
- `BALE_STORE_RAW_UPDATES=false` keeps raw webhook payload storage disabled by default.
- Webhook route requires `BALE_WEBHOOK_SECRET` through `/webhook/bale/{secret}`.
- Logs are designed to avoid secrets, chat ids, raw payloads, and full patient text.
- The app is intended to bind uvicorn to `127.0.0.1:8000` behind a reverse proxy.
- Rollback plan is documented as checking out a previous commit and restarting the service.

### Blocked Before Public Exposure
- HTTPS must be configured and verified through a reverse proxy such as Nginx or Caddy.
- Firewall plan must be defined before server exposure: allow SSH and HTTPS only unless a different need is explicitly approved.
- Local-only endpoints such as `/local/reviews/pending` and `/local/reviews/{message_id}/mark-reviewed` must not be publicly exposed through the reverse proxy.
- Backup command must be tested on the deployment host after `DATABASE_PATH` is set.
- Restore command must be tested on the deployment host after `DATABASE_PATH` is set.
- Bale webhook assumptions still require official verification, including payload schema, retry behavior, duplicate identifiers, and webhook authentication/signature support.
- Bale send-message assumptions still require verification before `BALE_ENABLE_SENDING=true`.
- Sanitized logs must be rechecked on the VPS to confirm they do not expose secrets, chat ids, raw payloads, or full patient text.
- Retention duration and deletion process must be approved before storing real patient messages long term.

### Go Decision
Milestone 8 may start only after the deployment owner confirms the blockers above are either resolved or explicitly accepted as controlled risks. Public webhook registration and real outgoing sending remain separate approval-gated actions.

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
- Current local helper:
  `python -c "from app.database import create_sqlite_backup; result = create_sqlite_backup(); print(result.backup_path)"`
- The helper copies only the configured SQLite database file into `backups/` with a timestamped filename. It does not copy `.env`, tokens, logs, or tunnel output.
- Restore rehearsal helper:
  `python -c "from app.database import restore_sqlite_backup; result = restore_sqlite_backup('backups/YOUR_BACKUP_FILE.db'); print(result.restored_path)"`
- Stop the app before restore. The restore helper refuses to overwrite an existing database by default; move the current database aside first, or use `overwrite=True` only after intentionally choosing to replace it.
- Keep backups outside Git. Do not commit database files, backup files, `.env`, logs, tunnel output, or generated QR output.
- Keep release snapshots or tagged commits.
- Roll back by checking out the previous known-good commit and restarting service:
  `git checkout <previous-good-commit>`
  `sudo systemctl restart bale-bot`

## Data Retention Notes
- Stored local data includes incoming message metadata, message text, duplicate-delivery identifiers, pharmacist-review metadata, timestamps, and raw webhook storage status.
- Raw webhook payload storage is disabled by default with `BALE_STORE_RAW_UPDATES=false`.
- Patient and message data should not be kept forever without a pharmacy-approved retention policy.
- Automatic deletion, retention scheduling, encrypted backups, and cloud backup are postponed until the workflow and deployment environment are clearer.

## Deployment Blockers Before Public Exposure
- Confirm Bale webhook authentication/signature validation beyond secret-path protection, if Bale supports it.
- Confirm exact Bale webhook and send-message schemas.
- Verify reverse proxy TLS and request size/timeouts for webhook traffic.
- Verify `BALE_WEBHOOK_SECRET` is strong and not committed to Git.
- Keep `BALE_ENABLE_SENDING=false` until real sending is intentionally approved.
- Verify backup and restore steps for the SQLite database.
- Confirm sanitized logs still do not include tokens, secrets, raw payloads, chat ids, or full message text.
