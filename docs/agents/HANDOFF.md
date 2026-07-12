# Handoff — BaleMed (new Agent chat)

**Date:** 2026-07-12  
**Branch:** `main` (Milestone 9 merged)
**Merged PR:** https://github.com/hosseintajdari/bale-med/pull/38
**Milestone:** 9 merged → **VPS shadow deploy + verify pending reviews** (owner runs on server)

Copy this file into a new chat, or say: *Read `docs/agents/HANDOFF.md` and continue.*

---

## Done from Cursor web (cloud agent)

| Step | Status |
|------|--------|
| Milestone 9 LLM layer coded | ✅ merged to `main` |
| `make validate` (88 tests) | ✅ |
| PR #38 merged | ✅ |
| VPS SSH / HTTPS from cloud | ❌ blocked (Iran VPS resets US cloud connections) |

**Cloud agents cannot SSH to `balemed` or curl `embednet.systems` from Cursor web.** Deploy must run on your laptop/desktop with `ssh balemed`.

---

## Your next step (P1 — VPS shadow deploy)

### 1. Add LLM env on VPS

```bash
ssh balemed
sudo nano /opt/bale-bot/.env
```

Add (real key only on server):

```env
BALE_ENABLE_LLM=true
BALE_LLM_MODE=shadow
BALE_LLM_API_BASE_URL=https://YOUR_PROVIDER/v1
BALE_LLM_API_KEY=YOUR_KEY
BALE_LLM_MODEL=gpt-4o-mini
```

Keep `BALE_ENABLE_SENDING=false` unless 8J owner approval exists.

### 2. Pull `main` and run verify script

```bash
cd /opt/bale-bot
git fetch origin && git checkout main && git pull origin main
DOMAIN=embednet.systems bash deploy/scripts/10-shadow-llm-verify.sh
```

Or: `bash deploy/scripts/install.sh 9a`

### 3. Send test messages + confirm pending reviews

Send 5–10 messages to `@embednebot`, then on VPS:

```bash
curl -s http://127.0.0.1:8000/local/reviews/pending | python3 -m json.tool
sudo journalctl -u bale-bot -n 50 --no-pager | grep llm_status
```

**Expect:** template replies only; `llm_extracted` / `llm_status` (e.g. `shadow_ok`) on pending items; public `https://embednet.systems/local/reviews/pending` → **404**.

Paste JSON output in Agent chat to confirm shadow mode.

---

## P2 — Human go-live gate (before `BALE_LLM_MODE=live`)

Owner must approve and review 20–50 shadow messages before setting `BALE_LLM_MODE=live`.

---

## Env reference (Milestone 9)

| Variable | Default | Meaning |
|----------|---------|---------|
| `BALE_ENABLE_LLM` | `false` | Master switch |
| `BALE_LLM_MODE` | `shadow` | `shadow` = store only; `live` = union escalation |
| `BALE_LLM_API_BASE_URL` | empty | OpenAI-compatible base URL |
| `BALE_LLM_API_KEY` | empty | Never commit |
| `BALE_LLM_MODEL` | `gpt-4o-mini` | Model id for audit |

---

## Key files

| Purpose | Path |
|---------|------|
| LLM service | `app/llm/service.py` |
| VPS shadow verify | `deploy/scripts/10-shadow-llm-verify.sh` |
| Safety rules | `docs/SAFETY_RULES.md` |
| Deploy runbook | `docs/DEPLOYMENT_VPS.md` |

**Pin this chat** before archive — Milestone 9 merge + VPS shadow checklist.
