# Handoff — BaleMed (new Agent chat)

**Date:** 2026-07-13  
**Branch:** `main`  
**Merged PR:** https://github.com/hosseintajdari/bale-med/pull/38  
**Issue #9:** closed after merge  
**Milestone:** 9 shadow LLM **live on VPS** (Arvan) → **verify `shadow_ok` on bot traffic**, then owner review

Copy this file into a new chat, or say: *Read `docs/agents/HANDOFF.md` and continue.*

---

## Current status (2026-07-13)

| Item | Status |
|------|--------|
| Milestone 9 code on `main` | ✅ |
| VPS `/opt/bale-bot` has `app/llm/` (deployed via scp) | ✅ |
| LLM provider: **Arvan Cloud AI** (DeepSeek-V3.2) | ✅ `test-llm-provider.py` → **200** |
| `BALE_LLM_MODE=shadow` | ✅ configured on VPS |
| Bot template replies to patients | ✅ unchanged (expected) |
| `shadow_ok` on real `@embednebot` messages | ⏳ confirm next |

**VPS deploy note:** `/opt/bale-bot` has no working `git pull` (no GitHub auth). Updates so far via **scp from laptop**. Optional: attach git (see below).

**Security:** If Arvan gateway URL/key was pasted in chat, **rotate** in Arvan panel and update `/opt/bale-bot/.env` only.

---

## Paste this in new Agent chat

```text
Read docs/agents/HANDOFF.md.

Arvan LLM test returns 200 on VPS. Help me confirm shadow_ok on real @embednebot messages and review /local/reviews/pending output.
```

---

## P1 — Confirm shadow on real bot traffic

On VPS:

```bash
ssh balemed
sudo systemctl restart bale-bot   # if .env changed recently
```

1. Send **3–5 new messages** to `@embednebot` (not repeats of old text).
2. Check:

```bash
cd /opt/bale-bot && . .venv/bin/activate
python3 deploy/scripts/vps-quick-check.py
sudo journalctl -u bale-bot -n 30 --no-pager | grep -i llm
curl -s http://127.0.0.1:8000/local/reviews/pending | python3 -m json.tool
```

**Expect:** recent rows with `llm_status=shadow_ok` and `llm_extracted` populated; patients still get template replies only.

---

## P2 — Human go-live gate (before `BALE_LLM_MODE=live`)

Owner must:

1. Approve LLM live mode explicitly.
2. Review **20–50 shadow messages** (extracted fields vs pharmacist judgment).
3. Run `make validate` / `scripts/verify.ps1`.

Then only on VPS `.env`:

```env
BALE_LLM_MODE=live
```

Live mode: LLM `needs_review` unions with keywords; failures → `llm_fail_safe`.

---

## Arvan Cloud AI env (working on Iran VPS)

In `/opt/bale-bot/.env` (secrets **only on server**):

```env
BALE_ENABLE_LLM=true
BALE_LLM_MODE=shadow
BALE_LLM_API_BASE_URL=https://arvancloudai.ir/gateway/models/DeepSeek-V3.2/<token-from-panel>/v1
BALE_LLM_API_KEY=<api-key-from-panel>
BALE_LLM_MODEL=DeepSeek-V3.2
BALE_LLM_TIMEOUT_SECONDS=90
```

- **One `=` per line** — `BALE_LLM_MODEL=DeepSeek-V3.2` (not `==`)
- Test: `python3 deploy/scripts/test-llm-provider.py` → `status=200`

### Provider notes (from VPS tests)

| Provider | Iran VPS |
|----------|----------|
| **Arvan Cloud AI** | ✅ Works |
| Groq | ✅ Works with valid key (`401` = bad key) |
| Ollama Cloud | ❌ 403 blocked from VPS IP |
| Local Ollama on VPS | ⚠️ Possible but tight on 2 vCPU / 4 GB RAM |

---

## VPS helpers (in repo)

| Script | Purpose |
|--------|---------|
| `deploy/scripts/test-llm-provider.py` | Test LLM API (no secrets printed) |
| `deploy/scripts/ensure-llm-env.py` | Add missing LLM env keys |
| `deploy/scripts/check-env-safe.py` | Safe `.env` health check |
| `deploy/scripts/vps-quick-check.py` | Sending + recent messages + LLM status |
| `deploy/scripts/10-shadow-llm-verify.sh` | Full shadow deploy verify |

---

## Optional — attach git on VPS

```bash
ssh balemed
cp /opt/bale-bot/.env /tmp/bale-bot.env.backup
cd /opt/bale-bot
git init
git remote add origin https://github.com/hosseintajdari/bale-med.git
git fetch origin
git checkout -B main origin/main
cp /tmp/bale-bot.env.backup .env
chmod 600 .env
```

Then `git pull` works for future deploys (or keep using scp).

---

## Key files

| Purpose | Path |
|---------|------|
| LLM provider | `app/llm/provider.py` |
| LLM service | `app/llm/service.py` |
| VPS shadow verify | `deploy/scripts/10-shadow-llm-verify.sh` |
| Safety rules | `docs/SAFETY_RULES.md` |
| Deploy runbook | `docs/DEPLOYMENT_VPS.md` |

**Pin this chat** before archive — Arvan shadow LLM deploy + verify checklist.
