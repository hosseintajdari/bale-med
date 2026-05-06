# Bale Pharmacy Assistant Bot

Minimal FastAPI skeleton for a pharmacy automation chatbot connected to Bale messenger.

The first milestone is intentionally small: receive a Bale webhook update, store it in SQLite, and prepare a safe reply path. The bot does not provide diagnosis, prescriptions, dosage recommendations, or medical advice.

## MVP Guarantees vs Non-Goals

| Area | Current MVP |
| --- | --- |
| In scope | Receive Bale webhook payload, store message data, prepare safe acknowledgement path |
| Not in scope | Diagnosis, treatment advice, dosage changes, prescription replacement |
| Bale outbound API | Placeholder only, not enabled for real delivery |
| Deployment | Local-first with VPS runbook, not full production hardening |

## Project Structure

```text
app/
  main.py          FastAPI app and routes
  config.py        Environment-based settings
  bale_client.py   Placeholder Bale API client
  handlers.py      Basic update router
  models.py        Simple data models
  database.py      SQLite setup and storage helpers
docs/
  PROJECT_PLAN.md  MVP plan and next milestones
  SAFETY_RULES.md  Pharmacy safety boundaries
  ASSUMPTIONS_BALE_API.md  Canonical Bale API assumptions
  DEPLOYMENT_VPS.md        Minimal VPS deployment runbook
```

## Setup on Windows PowerShell

```powershell
cd C:\Users\Maryam-pc\projects\bale
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
BALE_REPLY_TEXT=پیام شما دریافت شد. این ربات جایگزین نظر داروساز نیست و در صورت نیاز توسط داروساز بررسی میشود.
DATABASE_PATH=bale_bot.db
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

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
```

## Local getMe Test (PowerShell)

Use this command to test token connectivity against Bale without sending messages:

```powershell
python -c "from app.bale_client import BaleClient; import json; print(json.dumps(BaleClient().get_me(), ensure_ascii=False, indent=2))"
```

## Local Webhook Test

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/webhook/bale `
  -ContentType "application/json" `
  -Body '{"message":{"chat":{"id":"demo-chat"},"text":"Hello pharmacy"}}'
```

Dry-run behavior note: keep `BALE_ENABLE_SENDING=false` so webhook processing stores the message and prepares reply metadata without calling Bale `sendMessage`.

## Local Smoke Test (PowerShell)

```powershell
# 1) Start server
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another PowerShell window:

```powershell
# 2) Health check
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/health

# 3) Webhook test with mock payload
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/webhook/bale `
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

```powershell
python -m unittest discover -s tests
```

Run this before and after changes. These tests currently check:
- local `.env` loading
- webhook routing, SQLite storage, and dry-run reply preparation

## Bale API Assumptions

Current parsing is intentionally conservative and based on Telegram-like structure:
- Top-level `message` object may exist.
- `message.chat.id` may provide chat identity.
- `message.message_id` and `message.text` may exist.

These are assumptions, not confirmed Bale contract. Track and verify them in [ASSUMPTIONS_BALE_API.md](/C:/Users/Maryam-pc/projects/bale/docs/ASSUMPTIONS_BALE_API.md) before enabling outbound calls.

## Bale Client (Milestone 2)

Implemented methods:
- `getMe`
- `sendMessage`
- `setWebhook`
- `getWebhookInfo`

Webhook behavior:
- Always stores incoming updates.
- Supports only `message.text` path for acknowledgement behavior.
- If `BALE_ENABLE_SENDING=false`, reply is prepared but not sent.
- If `BALE_ENABLE_SENDING=true`, sends:
  `پیام شما دریافت شد. این ربات جایگزین نظر داروساز نیست و در صورت نیاز توسط داروساز بررسی میشود.`
- Do not call `setWebhook` to `127.0.0.1` because Bale requires public HTTPS URL for webhook delivery.

## VPS Notes

Minimal VPS deployment guidance is documented in [DEPLOYMENT_VPS.md](/C:/Users/Maryam-pc/projects/bale/docs/DEPLOYMENT_VPS.md). Treat webhook authentication and HTTPS reverse-proxy setup as deployment blockers before public exposure.
