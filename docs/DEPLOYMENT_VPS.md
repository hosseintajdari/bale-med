# Minimal VPS Deployment Runbook

This runbook is for the current MVP only. It does not replace production security hardening.

## Milestone 7 Checklist

Milestone 7 preparation is complete. Do not deploy to a real VPS, change DNS, configure SSL, edit firewall rules, register a production webhook, or enable real outgoing Bale messages until Milestone 8 is explicitly approved.

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
- Optional admin notifications exist but remain disabled by default with `BALE_ENABLE_ADMIN_NOTIFICATIONS=false`.
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
- Bale send-message assumptions still require verification before `BALE_ENABLE_SENDING=true` or before admin notifications are enabled.
- Sanitized logs must be rechecked on the VPS to confirm they do not expose secrets, chat ids, raw payloads, or full patient text.
- Retention duration and deletion process must be approved before storing real patient messages long term.

### Go Decision
Milestone 8 may start only after the deployment owner confirms the blockers above are either resolved or explicitly accepted as controlled risks. Public webhook registration and real outgoing sending remain separate approval-gated actions.

## Milestone 8 VPS Deployment Execution Plan

Milestone 8 is the first real VPS deployment milestone. Milestone 8A has started as readiness and GitHub workflow tracking only. Real server work starts only after a VPS is purchased and SSH access works. It does not include AI, a Web UI, a dashboard, medical logic changes, DNS changes before approval, or enabling real outgoing Bale messages.

Milestone 8 GitHub rule: use one small branch and pull request per submilestone, then merge and sync `main` before starting the next submilestone.

Default deployment choice: use Caddy as the reverse proxy because it is beginner-friendly and can manage HTTPS automatically. Nginx is a valid alternative if the VPS provider, hosting panel, or future operator is more comfortable with Nginx.

Required safety rule for the first VPS deployment:

```env
BALE_ENABLE_SENDING=false
BALE_ENABLE_ADMIN_NOTIFICATIONS=false
```

The FastAPI app must listen only on `127.0.0.1:8000`. Public traffic should reach only the HTTPS reverse proxy. Local-only endpoints such as `/local/reviews/pending` and `/local/reviews/{message_id}/mark-reviewed` must not be exposed publicly.

### VPS Purchase Checklist

Prefer an Iran-based VPS first, unless testing shows Bale webhook delivery or operator access requires a different country. Before buying, confirm:

- OS: Ubuntu 22.04 LTS or Ubuntu 24.04 LTS.
- Minimum size: 1 vCPU, 1.5-2 GB RAM, 25 GB SSD.
- Preferred size: 2 vCPU, 2 GB RAM, 40 GB SSD.
- Static IPv4 address.
- Ports 80 and 443 can be opened.
- SSH access is included.
- Snapshot or backup support is available.
- Provider allows long-running web services.
- Provider allows installing Caddy or Nginx.
- A rollback path exists through snapshot, manual backup, or rebuilding from Git.

Do not buy if ports 80/443 are blocked, SSH is unavailable, the IP changes unexpectedly, or there is no practical backup/snapshot option.

### 8A: VPS Base Access and Hardening Checklist

Goal: Get safe SSH access and basic server hardening in place before app deployment.

Status: Started for readiness tracking and GitHub workflow only. Waiting for confirmed VPS access before running server commands.

Scope IN:
- Confirm SSH access.
- Create a non-root deploy user.
- Update packages.
- Configure firewall for SSH, HTTP, and HTTPS only.

Scope OUT:
- No app clone.
- No webhook registration.
- No DNS or HTTPS setup yet.
- No real Bale sending.

Exact commands, run from Windows PowerShell:

```powershell
ssh root@YOUR_SERVER_IP
```

Exact commands, run on Ubuntu:

```bash
apt update
apt upgrade -y
adduser deploy
usermod -aG sudo deploy
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status verbose
```

Verification:

```powershell
ssh deploy@YOUR_SERVER_IP
```

```bash
whoami
sudo whoami
ufw status verbose
```

Rollback:
- If the firewall blocks SSH, use the VPS provider rescue console to disable or fix UFW.
- If the deploy user fails, log in as root again and recreate or repair the user.
- If package updates break the server, restore the provider snapshot if available.

Done when:
- `deploy` can log in by SSH.
- `sudo whoami` returns `root`.
- UFW allows only SSH, port 80, and port 443.

### 8B: Install Python, Git, Venv, and Clone Repo

Goal: Prepare the server runtime and put the project under `/opt/bale-bot`.

Scope IN:
- Install Python, venv, pip, Git, and curl.
- Clone the repository.
- Install Python dependencies into a virtual environment.

Scope OUT:
- No `.env` secrets yet.
- No systemd service.
- No reverse proxy.
- No webhook registration.

Exact commands:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl
python3 --version
git --version
sudo mkdir -p /opt/bale-bot
sudo chown -R deploy:deploy /opt/bale-bot
git clone YOUR_REPOSITORY_URL /opt/bale-bot
cd /opt/bale-bot
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Verification:

```bash
cd /opt/bale-bot
source .venv/bin/activate
python -m compileall app tests
```

Rollback:
- If clone fails, check repository URL and GitHub access, then remove the incomplete directory only after confirming the path:
  `pwd` must show `/opt/bale-bot` before cleaning anything inside it.
- If dependencies fail, keep the error output and fix only the missing package or version issue.

Done when:
- Repository exists at `/opt/bale-bot`.
- `.venv` exists.
- Dependencies install without errors.
- Compile check passes.

### 8C: Configure `.env` with Placeholders and Keep Sending Disabled

Goal: Create the server `.env` safely without committing or printing secrets.

Scope IN:
- Create `/opt/bale-bot/.env` on the server.
- Set production-like paths.
- Keep sending and admin notifications disabled.
- Create the SQLite data directory.

Scope OUT:
- No secret sharing in chat, screenshots, logs, or commits.
- No `BALE_ENABLE_SENDING=true`.
- No webhook registration.

Exact commands:

```bash
cd /opt/bale-bot
mkdir -p /opt/bale-bot/data
nano .env
chmod 600 .env
```

Use this shape, replacing only the placeholder values on the server:

```env
BALE_BOT_TOKEN=REAL_TOKEN_ON_SERVER_ONLY
BALE_API_BASE_URL=https://tapi.bale.ai
BALE_ENABLE_SENDING=false
BALE_REPLY_TEXT=پیام شما دریافت شد. این ربات جایگزین نظر داروساز یا پزشک نیست. در صورت نیاز، پیام شما توسط داروساز بررسی می‌شود.
DATABASE_PATH=/opt/bale-bot/data/bale_bot.db
BALE_WEBHOOK_SECRET=LONG_RANDOM_SECRET_ON_SERVER_ONLY
BALE_STORE_RAW_UPDATES=false
BALE_ADMIN_CHAT_ID=
BALE_ENABLE_ADMIN_NOTIFICATIONS=false
```

Verification:

```bash
cd /opt/bale-bot
test -f .env
test "$(stat -c '%a' .env)" = "600"
grep -E "BALE_ENABLE_SENDING=false|BALE_ENABLE_ADMIN_NOTIFICATIONS=false|BALE_STORE_RAW_UPDATES=false" .env
git status --short
```

Rollback:
- If a wrong value is saved, edit `.env` again with `nano .env`.
- If a secret is accidentally pasted into a command history or public log, rotate that secret before continuing.

Done when:
- `.env` exists only on the server.
- `.env` permissions are `600`.
- Sending, admin notifications, and raw webhook storage are disabled.
- `git status --short` does not show `.env`.

### 8D: Run App Manually on `127.0.0.1:8000`

Goal: Prove the app starts on the VPS before adding systemd or HTTPS.

Scope IN:
- Start uvicorn manually.
- Confirm local health check.
- Confirm mock webhook processing with sending disabled.

Scope OUT:
- No public exposure.
- No webhook registration.
- No real outgoing messages.

Exact commands:

```bash
cd /opt/bale-bot
source .venv/bin/activate
set -a
. ./.env
set +a
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second SSH session:

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST "http://127.0.0.1:8000/webhook/bale/YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"message":{"chat":{"id":"demo-chat"},"message_id":1,"text":"Hello pharmacy"}}'
```

Verification:
- Health response is `{"status":"ok"}`.
- Webhook returns a normal JSON response.
- No Bale message is sent because `BALE_ENABLE_SENDING=false`.
- SQLite file is created under `/opt/bale-bot/data`.

Rollback:
- Stop manual uvicorn with `Ctrl+C`.
- If the app fails to start, fix only the missing environment value or dependency reported by the error.

Done when:
- Manual run works locally on the VPS.
- Mock webhook works.
- Sending remains disabled.

### 8E: Add Systemd Service

Goal: Run the app as a managed Linux service.

Scope IN:
- Create `bale-bot.service`.
- Start and enable the service.
- Check logs for sanitized output.

Scope OUT:
- No reverse proxy yet.
- No webhook registration.
- No real outgoing messages.

Exact commands:

```bash
sudo nano /etc/systemd/system/bale-bot.service
```

Service file:

```ini
[Unit]
Description=Bale Pharmacy Bot
After=network.target

[Service]
User=deploy
WorkingDirectory=/opt/bale-bot
EnvironmentFile=/opt/bale-bot/.env
ExecStart=/opt/bale-bot/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bale-bot
sudo systemctl start bale-bot
sudo systemctl status bale-bot --no-pager
curl -s http://127.0.0.1:8000/health
sudo journalctl -u bale-bot -n 50 --no-pager
```

Verification:
- Service status is active.
- Health check works.
- Logs do not show tokens, webhook secret, chat ids, raw payloads, or full patient text.

Rollback:

```bash
sudo systemctl stop bale-bot
sudo systemctl disable bale-bot
sudo rm /etc/systemd/system/bale-bot.service
sudo systemctl daemon-reload
```

Done when:
- Service starts after reboot-capable enablement.
- Local health check passes through `127.0.0.1`.
- Logs remain sanitized.

### 8F: Add Reverse Proxy and HTTPS

Goal: Expose only the needed public HTTPS paths while keeping the app local.

Scope IN:
- Install Caddy.
- Configure HTTPS reverse proxy to `127.0.0.1:8000`.
- Block `/local/*` at the proxy.

Scope OUT:
- No webhook registration until smoke tests pass.
- No real sending.
- No exposing local review endpoints publicly.

Exact commands:

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl gnupg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
sudo nano /etc/caddy/Caddyfile
```

Caddyfile:

```caddyfile
your-domain.example {
    respond /local/* 404
    reverse_proxy 127.0.0.1:8000
}
```

Apply:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
sudo systemctl status caddy --no-pager
```

Verification:

```bash
curl -i https://your-domain.example/health
curl -i https://your-domain.example/local/reviews/pending
```

Expected:
- `/health` returns HTTP 200 and `{"status":"ok"}`.
- `/local/reviews/pending` returns HTTP 404 from Caddy.
- `uvicorn` is still bound to `127.0.0.1:8000`, not `0.0.0.0`.

Rollback:

```bash
sudo systemctl stop caddy
sudo systemctl disable caddy
sudo systemctl restart bale-bot
```

Nginx alternative:
- Use Nginx only if Caddy is not suitable.
- Nginx must also forward to `127.0.0.1:8000`, terminate HTTPS, and block `/local/`.

Done when:
- Public HTTPS works.
- Local-only endpoints are blocked publicly.
- App remains local behind the proxy.

### 8G: Run Smoke Tests

Goal: Verify the VPS deployment without registering Bale webhook.

Scope IN:
- Health test.
- Mock webhook test through HTTPS.
- Database row check.
- Backup test.
- Log safety check.

Scope OUT:
- No real webhook registration.
- No real outgoing Bale sends.
- No real patient test data.

Exact commands:

```bash
curl -s https://your-domain.example/health
curl -s -X POST "https://your-domain.example/webhook/bale/YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"message":{"chat":{"id":"demo-chat"},"message_id":2,"text":"Hello pharmacy"}}'
cd /opt/bale-bot
source .venv/bin/activate
python -c "import sqlite3; conn=sqlite3.connect('/opt/bale-bot/data/bale_bot.db'); cur=conn.cursor(); cur.execute('select id, text, review_status from incoming_messages order by id desc limit 1'); print(cur.fetchone()); conn.close()"
python -c "from app.database import create_sqlite_backup; result = create_sqlite_backup(); print(result.backup_path)"
sudo journalctl -u bale-bot -n 100 --no-pager
```

Verification:
- HTTPS health works.
- Mock webhook stores a row.
- Backup command creates a backup file.
- Logs do not expose secrets, chat ids, raw payloads, or full patient text.
- `BALE_ENABLE_SENDING=false` is still present in `/opt/bale-bot/.env`.

Rollback:
- Stop Caddy if public HTTPS behavior is wrong.
- Stop `bale-bot` if logs or data handling look unsafe.
- Restore from snapshot or previous Git commit if deployment files are wrong.

Done when:
- All smoke tests pass.
- No public local-only endpoint exposure is found.
- No unsafe logs are found.

### 8H: Register Bale Webhook with Production URL

Goal: Point Bale to the production HTTPS webhook only after the deployment is safe.

Scope IN:
- Register webhook using the verified HTTPS URL.
- Check webhook info.
- Send one controlled test message to the bot.

Scope OUT:
- No `BALE_ENABLE_SENDING=true`.
- No real pharmacy user traffic yet.
- No AI, dashboard, or clinical logic changes.

Exact commands:

```bash
cd /opt/bale-bot
source .venv/bin/activate
set -a
. ./.env
set +a
python -c "from app.bale_client import BaleClient; import json; print(json.dumps(BaleClient().set_webhook('https://your-domain.example/webhook/bale/YOUR_SECRET'), ensure_ascii=False, indent=2))"
python -c "from app.bale_client import BaleClient; import json; print(json.dumps(BaleClient().get_webhook_info(), ensure_ascii=False, indent=2))"
```

Verification:
- Bale accepts the webhook URL.
- `getWebhookInfo` shows the intended HTTPS URL, if Bale returns that field.
- One controlled Bale message reaches the VPS and creates a database row.
- The bot does not send an outgoing reply because `BALE_ENABLE_SENDING=false`.

Rollback:
- If webhook registration is wrong, set the webhook again to the corrected HTTPS URL.
- If public delivery is unsafe, remove or replace the webhook using Bale API after confirming the exact supported method.
- Stop Caddy or `bale-bot` if incoming traffic must be paused quickly.

Done when:
- Bale delivery reaches the VPS.
- No outgoing send occurs.
- Logs and database behavior remain safe.

### 8I: First Monitored Dry-Run Operation

Goal: Run the deployed bot in dry-run mode while watching storage, logs, and pharmacist review metadata.

Scope IN:
- Keep sending disabled.
- Monitor logs and database rows.
- Confirm review metadata and duplicate guard behavior.
- Confirm backup works after real incoming webhook delivery.

Scope OUT:
- No real sending.
- No admin notification sending.
- No broad patient rollout.

Exact commands:

```bash
grep -E "BALE_ENABLE_SENDING=false|BALE_ENABLE_ADMIN_NOTIFICATIONS=false" /opt/bale-bot/.env
sudo journalctl -u bale-bot -f
```

In another SSH session:

```bash
cd /opt/bale-bot
source .venv/bin/activate
python -c "import sqlite3; conn=sqlite3.connect('/opt/bale-bot/data/bale_bot.db'); cur=conn.cursor(); cur.execute('select id, length(text), needs_review, review_reason, review_status from incoming_messages order by id desc limit 10'); print(cur.fetchall()); conn.close()"
python -c "from app.database import create_sqlite_backup; result = create_sqlite_backup(); print(result.backup_path)"
```

Verification:
- Incoming messages are stored.
- Review fields are populated.
- Duplicate deliveries do not create duplicate rows when stable identifiers exist.
- Backups work on the VPS.
- Logs remain sanitized.

Rollback:
- Pause public traffic by stopping Caddy: `sudo systemctl stop caddy`.
- Pause app processing by stopping the service: `sudo systemctl stop bale-bot`.
- Restore from snapshot or known-good Git commit if needed.

Done when:
- Dry-run operation is stable.
- Safety checks still pass.
- The owner confirms whether to continue observing or proceed to a later sending decision.

### 8J: Decide Whether to Enable Real Sending Later

Goal: Make a separate approval decision after dry-run evidence exists.

Scope IN:
- Review Bale API assumptions.
- Review safety rules.
- Review dry-run logs and database rows.
- Decide whether real sending should remain disabled or move to a new milestone.

Scope OUT:
- Do not enable real sending inside initial Milestone 8.
- No admin notification sending until `sendMessage` and admin chat behavior are verified.
- No AI or clinical advice.

Exact commands for review:

```bash
cd /opt/bale-bot
grep -E "BALE_ENABLE_SENDING|BALE_ENABLE_ADMIN_NOTIFICATIONS|BALE_STORE_RAW_UPDATES" .env
sudo journalctl -u bale-bot -n 200 --no-pager
source .venv/bin/activate
python -c "import sqlite3; conn=sqlite3.connect('/opt/bale-bot/data/bale_bot.db'); cur=conn.cursor(); cur.execute('select count(*), sum(case when needs_review then 1 else 0 end) from incoming_messages'); print(cur.fetchone()); conn.close()"
```

Verification:
- Bale `sendMessage` contract is verified against official documentation or a controlled non-production test.
- Safety replies are approved.
- Admin notification destination is verified if notifications are considered.
- The pharmacy owner explicitly approves any move toward real sending.

Rollback:
- Keep `BALE_ENABLE_SENDING=false`.
- If real sending is accidentally enabled, immediately set it back to `false` and restart:
  `sudo nano /opt/bale-bot/.env`
  `sudo systemctl restart bale-bot`

Done when:
- Decision is documented.
- Real sending remains disabled unless a later explicit milestone approves it.

## Final Pre-Purchase Checklist

- VPS country chosen: Iran first, unless Bale or operator access requires otherwise.
- Ubuntu 22.04 LTS or 24.04 LTS is available.
- VPS meets at least 1 vCPU, 1.5-2 GB RAM, and 25 GB SSD.
- Preferred option of 2 vCPU, 2 GB RAM, and 40 GB SSD is affordable.
- Static IPv4 is included.
- Ports 80 and 443 can be opened.
- SSH access is included.
- Snapshot or backup support exists.
- You have a domain or confirmed HTTPS endpoint plan.
- You are ready to keep `BALE_ENABLE_SENDING=false` during first deployment.

## Final Pre-Webhook Checklist

- `bale-bot` systemd service is active.
- Caddy HTTPS works for `/health`.
- Caddy blocks `/local/*` publicly.
- Uvicorn listens only on `127.0.0.1:8000`.
- `.env` exists only on the server and has `chmod 600`.
- `BALE_ENABLE_SENDING=false`.
- `BALE_ENABLE_ADMIN_NOTIFICATIONS=false`.
- `BALE_STORE_RAW_UPDATES=false`.
- SQLite backup command works on the VPS.
- Logs were checked for secrets, chat ids, raw payloads, and full patient text.
- Bale webhook URL uses HTTPS and the secret path.

## Final Pre-Real-Sending Checklist

- Dry-run deployment has been monitored.
- Bale `sendMessage` assumptions are verified.
- Bale webhook retry and duplicate behavior are understood well enough for production use.
- Safety replies are approved by the pharmacy owner.
- Admin notification behavior is tested only if needed.
- Retention duration and deletion process are approved.
- Backup and restore are tested on the deployment host.
- Rollback command is clear.
- The owner explicitly approves changing `BALE_ENABLE_SENDING` from `false` to `true`.

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
BALE_REPLY_TEXT=پیام شما دریافت شد. این ربات جایگزین نظر داروساز یا پزشک نیست. در صورت نیاز، پیام شما توسط داروساز بررسی می‌شود.
DATABASE_PATH=/opt/bale-bot/data/bale_bot.db
BALE_WEBHOOK_SECRET=...
BALE_ADMIN_CHAT_ID=
BALE_ENABLE_ADMIN_NOTIFICATIONS=false
```

Keep `BALE_ENABLE_SENDING=false` and `BALE_ENABLE_ADMIN_NOTIFICATIONS=false` until webhook schema, send-message behavior, the admin chat id, and pharmacist safety flow are verified.

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
