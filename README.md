# Bale Pharmacy Assistant Bot

Local-first FastAPI MVP for a Bale-based pharmacy workflow assistant.

**Verify before push:** `make validate` (see [`.github/workflows/README.md`](.github/workflows/README.md)).

The project supports safe pharmacy message intake, pharmacist review tracking, duplicate webhook handling, SQLite backup/restore, and optional admin review notifications. It is intended for constrained pharmacy workflows, including rural or border healthcare settings where clear handoff to a pharmacist matters.

This is not a deployed production system and not a clinically validated product. The bot does not provide diagnosis, prescriptions, dosage recommendations, autonomous triage, or medication-change advice.

## Current Status

**Active milestone:** 9 — LLM shadow classification on VPS (P1 shadow confirmed; P2 owner review before live mode).

Latest deploy state and next steps: [docs/agents/HANDOFF.md](docs/agents/HANDOFF.md).

## Table of Contents

- [Quick Start (Any OS)](#quick-start-any-os)
- [Long-Term Product Vision](#long-term-product-vision)
- [Milestone Map](#milestone-map)
- [MVP Guarantees vs Non-Goals](#mvp-guarantees-vs-non-goals)
- [Setup on Windows PowerShell](#setup-on-windows-powershell)
- [Run Locally](#run-locally)
- [Local Webhook Test](#local-webhook-test)
- [Local Pending Review List](#local-pending-review-list)
- [Local SQLite Backup](#local-sqlite-backup)
- [Run Tests](#run-tests)
- [Current Limitations and Next Priorities](#current-limitations-and-next-priorities)
- [VPS Notes](#vps-notes)

## Long-Term Product Vision

Build a safe pharmacy automation assistant for Bale that helps a real pharmacy receive messages, collect structured intake information, keep an auditable history, and route cases to a pharmacist when human judgment is needed.

The system is workflow-based, pharmacist-centered, safety-first, local-first, and AI-optional. Later milestones may add real VPS deployment, stronger pharmacist/admin tools, and LLM/AI support. Any AI features must stay inside pharmacist-approved safety boundaries and must not diagnose, prescribe, replace a pharmacist, or recommend medication changes.

This vision and the milestone order are allowed to change as the pharmacy workflow becomes clearer. When direction changes, update the milestone plan before changing implementation.

## Quick Start (Any OS)

Use this path for a cold local bootstrap. Tests pass without a real Bale bot token; only the optional `getMe` connectivity check needs a valid `BALE_BOT_TOKEN`.

```bash
cd /path/to/bale-med
python3 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # Windows: Copy-Item .env.example .env
python3 -m unittest discover -s tests
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/webhook/bale/CHANGE_ME \
  -H "Content-Type: application/json" \
  -d '{"message":{"chat":{"id":"demo-chat"},"text":"Hello pharmacy"}}'
```

Notes:
- Prefer `python3 -m uvicorn` if `uvicorn` is not on your PATH.
- Keep `BALE_ENABLE_SENDING=false` for safe local dry-run behavior.
- If `BALE_WEBHOOK_SECRET` is unset, the webhook returns HTTP 503 with a configuration message instead of processing the update.
- Run `./scripts/verify.sh` to execute the standard verification commands from the repo root.

## Milestone Map

- Milestone 1: Done - Project skeleton and local foundation.
- Milestone 2: Done - Real Bale webhook on local laptop with tunnel and real reply.
- Milestone 3: Done - Secure webhook with secret path.
- Milestone 4: Done - Basic bot commands.
- Milestone 5: Done - Safe pharmacy reply layer.
- Milestone 6: Done - Better logging and admin review.
- Milestone 7: Done - VPS deployment preparation and repository alignment.
  - Milestone 7A: Done - Bale webhook duplicate-delivery guard.
  - Milestone 7B: Done - Minimal local pharmacist review actions.
  - Milestone 7C: Done - Local SQLite backup and retention safety foundation.
  - Milestone 7D: Done - Final deployment readiness checklist.
  - Milestone 7E: Done - Local SQLite restore rehearsal.
  - Milestone 7F: Done - Persian and RTL-safe user-facing replies.
  - Milestone 7G: Done - Optional Bale admin review notifications.
  - Milestone 7I: Done - Repository context and issue alignment.
- Milestone 8: In progress - Real VPS deployment workflow.
  - Milestone 8A–8I: VPS deployed dry-run on Iran host; see [HANDOFF.md](docs/agents/HANDOFF.md).
- Milestone 9: Started - LLM/AI integration (optional classification layer; shadow default).

## MVP Guarantees vs Non-Goals

| Area | Current MVP |
| --- | --- |
| In scope | Secure Bale webhook intake, SQLite message storage, safe Persian replies, duplicate-delivery guard, pharmacist-review metadata/actions, backup/restore helpers, optional admin review notifications, optional LLM classification (internal only, shadow default) |
| Not in scope | Diagnosis, treatment advice, dosage changes, prescription replacement, autonomous clinical decision-making, Web UI, patient-facing LLM replies |
| Bale outbound API | Available only when explicitly enabled; keep disabled by default |
| Deployment | Local-first; VPS runbook in `docs/DEPLOYMENT_VPS.md` and scripts in `deploy/` |
| Clinical status | Safety-oriented workflow support only; not clinically validated |

## Project Structure

```text
app/
  main.py          FastAPI app and routes
  config.py        Environment-based settings
  bale_client.py   Cautious Bale API client
  handlers.py      Update router and reply logic
  replies.py       Safe Persian reply templates
  models.py        Data models
  database.py      SQLite setup and storage helpers
  llm/             Optional LLM classification (Milestone 9)
deploy/
  scripts/         VPS install, verify, and shadow LLM helpers
  templates/       systemd, Caddy, production .env template
docs/
  agents/HANDOFF.md        Current milestone status (start here for agents)
  PROJECT_PLAN.md            MVP plan and milestones
  SAFETY_RULES.md            Pharmacy safety boundaries
  ASSUMPTIONS_BALE_API.md    Canonical Bale API assumptions
  DEPLOYMENT_VPS.md          VPS deployment runbook
  adr/                       Architecture decision records
CONTEXT.md         Domain glossary (pharmacy workflow terms)
scripts/           verify.sh and verify.ps1
```

## Repository Standards

| Doc | Purpose |
| --- | --- |
| [HANDOFF.md](docs/agents/HANDOFF.md) | Current milestone status and VPS next steps |
| [VISION-AND-ROADMAP.md](docs/VISION-AND-ROADMAP.md) | Long-term direction and three-project portfolio arc |
| [CAREER-NARRATIVE.md](docs/CAREER-NARRATIVE.md) | Resume / portfolio wording (draft) |
| [CONTEXT.md](CONTEXT.md) | Domain glossary |
| [SAFETY_RULES.md](docs/SAFETY_RULES.md) | Pharmacy safety boundaries |
| [DEPLOYMENT_VPS.md](docs/DEPLOYMENT_VPS.md) | VPS runbook |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Local setup and commit rules |
| [SECURITY.md](SECURITY.md) | Secrets and sensitive data handling |

- GitHub issue and pull request templates are in [.github/](.github/).
- Keep changes small, milestone-aligned, and safe for a real pharmacy workflow.

## Setup on Windows PowerShell

```powershell
cd C:\path\to\bale-med
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set the required values. The app loads this file automatically
when you run commands from the project folder. Do not commit `.env`.

```env
BALE_BOT_TOKEN=...
BALE_API_BASE_URL=https://tapi.bale.ai
BALE_ENABLE_SENDING=false
BALE_REPLY_TEXT=پیام شما دریافت شد. این ربات جایگزین نظر داروساز یا پزشک نیست. در صورت نیاز، پیام شما توسط داروساز بررسی می‌شود.
DATABASE_PATH=bale_bot.db
BALE_WEBHOOK_SECRET=...
BALE_ADMIN_CHAT_ID=
BALE_ENABLE_ADMIN_NOTIFICATIONS=false
```

`BALE_ENABLE_SENDING` defaults to `false` and prevents accidental real sends.
Set `BALE_BOT_TOKEN` to your real bot token value in `.env`.
Warning: never commit `.env` to Git.

Enable/disable real sending:
- Disable (safe default): `BALE_ENABLE_SENDING=false`
- Enable real sends: `BALE_ENABLE_SENDING=true`

For a controlled local test, you can temporarily set `BALE_REPLY_TEXT` in `.env`,
for example `BALE_REPLY_TEXT=سلام حسین جان!`. Use a general, patient-safe message
before allowing real users to contact the bot.

## Run Locally

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

After activating a virtual environment, `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload` also works.

Open:

```text
http://127.0.0.1:8000/health
```

## Local getMe Test

Use this command to test token connectivity against Bale without sending messages. It requires a valid `BALE_BOT_TOKEN` in `.env`; placeholder values return a Bale API error.

```bash
python3 -c "from app.bale_client import BaleClient; import json; print(json.dumps(BaleClient().get_me(), ensure_ascii=False, indent=2))"
```

## Local Webhook Test

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/webhook/bale/your-secret `
  -ContentType "application/json" `
  -Body '{"message":{"chat":{"id":"demo-chat"},"text":"Hello pharmacy"}}'
```

Dry-run behavior note: keep `BALE_ENABLE_SENDING=false` so webhook processing stores the message and prepares reply metadata without calling Bale `sendMessage`.

## Local Pending Review List

After the app is running locally, use this read-only JSON endpoint to see messages waiting for pharmacist review:

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/local/reviews/pending
```

The endpoint returns only pending review rows and does not include stored raw webhook payloads. It is intended for local inspection, not public deployment.

To mark a pending review item as reviewed locally, use the stored message `id` from the pending list:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/local/reviews/1/mark-reviewed
```

This changes only `pending` items to `reviewed`. Missing items return 404, and already reviewed items return a safe unchanged response.

## Optional Bale Admin Notifications

For MVP pharmacist awareness, the bot can prepare a safe Bale notification when a message needs pharmacist review. This is optional and disabled by default:

```env
BALE_ADMIN_CHAT_ID=
BALE_ENABLE_ADMIN_NOTIFICATIONS=false
```

Keep `BALE_ENABLE_ADMIN_NOTIFICATIONS=false` until you have tested the admin chat id and the send path. Notifications are sent only when both `BALE_ENABLE_ADMIN_NOTIFICATIONS=true` and `BALE_ENABLE_SENDING=true`.

The notification includes the stored message id, review reason, a short sanitized preview, and an instruction to check `/local/reviews/pending`. It must not include raw webhook payloads, secrets, chat ids, or full patient text.

No Web UI is needed for the current MVP. Admin notifications plus the local pending review list are the minimal review-awareness path for now.

## Optional LLM Classification (Milestone 9)

The LLM layer is **disabled by default** and never sends generated text to patients. See [docs/SAFETY_RULES.md](docs/SAFETY_RULES.md) and [docs/adr/0001-llm-shadow-mode.md](docs/adr/0001-llm-shadow-mode.md).

```env
BALE_ENABLE_LLM=false
BALE_LLM_MODE=shadow
BALE_LLM_API_BASE_URL=
BALE_LLM_API_KEY=
BALE_LLM_MODEL=gpt-4o-mini
BALE_LLM_TIMEOUT_SECONDS=10
```

- **shadow** — persist LLM fields on `incoming_messages` only; patient replies unchanged.
- **live** — LLM `needs_review` unions with keyword escalation; failures use fail-safe review.

Before `BALE_LLM_MODE=live`, the pharmacy owner must review 20–50 shadow messages. VPS helpers: `deploy/scripts/list-shadow-reviews.py`, `deploy/scripts/10-shadow-llm-verify.sh`. Current VPS state: [docs/agents/HANDOFF.md](docs/agents/HANDOFF.md).

## Local SQLite Backup

Create a local SQLite backup before risky local operations or before moving toward VPS deployment:

```powershell
python -c "from app.database import create_sqlite_backup; result = create_sqlite_backup(); print(result.backup_path)"
```

The helper reads `DATABASE_PATH`, creates `backups/` if needed, and copies only the configured SQLite database file to a timestamped backup filename. It does not copy `.env`, tokens, logs, or tunnel output. Backup files are local operational files and should not be committed.

To rehearse a local restore, stop the app first, point to the backup file, and restore into the configured `DATABASE_PATH`:

```powershell
python -c "from app.database import restore_sqlite_backup; result = restore_sqlite_backup('backups/YOUR_BACKUP_FILE.db'); print(result.restored_path)"
```

The restore helper refuses to overwrite an existing database by default. For a real restore, first move the current database aside or call the helper with `overwrite=True` only after you intentionally choose to replace the current SQLite file.

## Data Retention Notes

The local SQLite database stores incoming message metadata, message text, duplicate-delivery identifiers, review status, review reason, timestamps, and raw webhook storage status. Raw webhook payload storage is disabled by default through `BALE_STORE_RAW_UPDATES=false`, so the default database stores `{"raw_update_storage": "disabled"}` instead of the full webhook payload.

Patient and message data should not be kept forever without a pharmacy-approved retention policy. Automatic deletion, retention scheduling, encrypted backups, and cloud backup are postponed until the workflow and deployment environment are clearer.

## Local Smoke Test (PowerShell)

```bash
# 1) Start server
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another PowerShell window:

```powershell
# 2) Health check
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/health

# 3) Webhook test with mock payload
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/webhook/bale/your-secret `
  -ContentType "application/json" `
  -Body '{"message":{"chat":{"id":"demo-chat"},"text":"Hello pharmacy"}}'

# 4) Verify latest SQLite row (PowerShell-safe REPL method)
python
```

In the Python prompt (`>>>`), run:

```python
import sqlite3
conn = sqlite3.connect("bale_bot.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cur.fetchall())
cur.execute("SELECT id, chat_id, text FROM incoming_messages ORDER BY id DESC LIMIT 1;")
print(cur.fetchone())
conn.close()
exit()
```

Expected health output:

```json
{"status":"ok"}
```

Expected latest message row example:

```text
(2, 'demo-chat', 'Hello pharmacy')
```

The first number is the auto-increment id and may differ on your machine.

## Run Tests

```bash
python3 -m unittest discover -s tests
```

Or run all standard verification checks:

```bash
./scripts/verify.sh
```

Tests pass without a real Bale bot token. Run this before and after changes. These tests currently check:
- local `.env` loading
- webhook routing, SQLite storage, duplicate-delivery handling, review metadata, local pending-review listing, and dry-run reply preparation
- basic command replies
- Persian safe intake and pharmacist-review escalation replies
- optional admin review notification metadata and safe skip behavior

## Bale API Assumptions

Current parsing is intentionally conservative and based on Telegram-like structure:
- Top-level `update_id` may exist.
- Top-level `message` object may exist.
- `message.chat.id` may provide chat identity.
- `message.message_id` and `message.text` may exist.

These are assumptions, not confirmed Bale contract. Track and verify them in [ASSUMPTIONS_BALE_API.md](docs/ASSUMPTIONS_BALE_API.md) before enabling outbound calls for real users.

## Bale Client

Implemented methods:
- `getMe`
- `sendMessage`
- `setWebhook`
- `getWebhookInfo`

Webhook behavior:
- Stores new incoming updates.
- Recognizes duplicate deliveries when top-level `update_id` exists, or when both `message.chat.id` and `message.message_id` exist. Duplicate deliveries return the existing stored row id, do not insert a second row, and do not prepare another reply.
- Still stores messages when no stable duplicate key can be derived.
- Stores basic pharmacist-review metadata for incoming messages.
- Supports local-only pharmacist review actions for marking pending review items as reviewed.
- Prepares optional Bale admin notifications for pharmacist-review cases. Notifications are disabled by default and duplicate webhook deliveries do not prepare another admin notification.
- Uses `/webhook/bale/{secret}` and returns 404 for a wrong secret.
- Supports only `message.text` path for acknowledgement behavior.
- Handles `/start`, `/help`, and `/status` with simple Persian, non-medical command replies. `/status` reports whether sending is on or off without exposing secrets.
- Unknown text keeps the configured safe acknowledgement reply.
- If `BALE_ENABLE_SENDING=false`, reply is prepared but not sent.
- Writes sanitized operational logs for incoming webhook handling and reply preparation. Logs include stored row id, whether text exists, text length, review status, and send mode; they should not include secrets, raw webhook payloads, chat ids, or full message text.
- If `BALE_ENABLE_SENDING=true`, sends:
  `پیام شما دریافت شد. این ربات جایگزین نظر داروساز یا پزشک نیست. در صورت نیاز، پیام شما توسط داروساز بررسی می‌شود.`
- Do not call `setWebhook` to `127.0.0.1` because Bale requires public HTTPS URL for webhook delivery.

## Current Limitations and Next Priorities

Milestone 8 deployment is in progress. An Iran-based VPS has been purchased. Use [deploy/README.md](deploy/README.md) and [deploy/server-info-checklist.md](deploy/server-info-checklist.md) on the server after SSH works. Steps 8A–8E do not require a domain; 8F–8H require DNS and HTTPS.

Before running server commands, collect the server IP address, SSH username and port, OS version, provider console or rescue link, backup/snapshot option, and confirmation that ports 80 and 443 can be opened.

Before public exposure, verify Bale webhook and `sendMessage` assumptions, configure HTTPS/reverse proxy/firewall rules, protect local-only endpoints, test backup/restore on the deployment host, confirm sanitized logs, and approve a retention/deletion policy.

Future milestone work should use a small branch, draft pull request, review/checks, merge, and local `main` sync before the next submilestone starts. Use branch names like `codex/milestone-8a-vps-readiness`.

AI, Web UI, clinical protocols, diagnosis, autonomous triage, and patient outcome claims remain postponed.

## VPS Notes

Milestone 7 deployment preparation is complete. VPS guidance is in [DEPLOYMENT_VPS.md](docs/DEPLOYMENT_VPS.md). Executable scripts and templates are in [deploy/](deploy/). Treat Bale webhook assumption verification, HTTPS reverse-proxy setup, firewall planning, local-only endpoint exposure, deployment-host backup/restore proof, rollback planning, sanitized logs, and real sending approval as blockers before public exposure.
