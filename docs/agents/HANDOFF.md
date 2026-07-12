# Handoff — BaleMed (new Agent chat)

**Date:** 2026-07-13  
**Branch:** `main`  
**Merged PR:** https://github.com/hosseintajdari/bale-med/pull/38  
**Issue #9:** closed after merge  
**Milestone:** 9 shadow LLM on VPS (Arvan) — **P1 done** → **P2 owner review** before live

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
| `shadow_ok` on real `@embednebot` messages | ✅ confirmed (e.g. row id 20, `update:26`) |

**VPS deploy note:** `/opt/bale-bot` has no working `git pull` (no GitHub auth). Updates so far via **scp from laptop**. Optional: attach git (see below).

**Shadow note:** `/local/reviews/pending` may stay **empty** in shadow mode — LLM fields are stored on `incoming_messages` even when keywords do not set `needs_review`. Use `vps-quick-check.py` or `list-shadow-reviews.py`.

**VPS `.env` hygiene:** run `python3 deploy/scripts/dedupe-env-keys.py` if `check-env-safe.py` reports duplicate keys (e.g. `BALE_LLM_MODEL`).

**Security:** If Arvan gateway URL/key was pasted in chat, **rotate** in Arvan panel and update `/opt/bale-bot/.env` only.

---

## Paste this in new Agent chat

```text
Read docs/agents/HANDOFF.md.

P1 shadow_ok is confirmed on VPS. Help me with P2: review 20–50 shadow messages (list-shadow-reviews.py) before BALE_LLM_MODE=live.
```

---

## P1 — Confirm shadow on real bot traffic ✅

Confirmed 2026-07-13: newest message `llm_status=shadow_ok`; older rows still `shadow_error` from pre-Arvan (Ollama) config.

Quick re-check on VPS:

```bash
ssh balemed
cd /opt/bale-bot && . .venv/bin/activate
python3 deploy/scripts/vps-quick-check.py
```

---

## P2 — Human go-live gate (before `BALE_LLM_MODE=live`)

Owner must:

1. Approve LLM live mode explicitly.
2. Review **20–50 shadow messages** — compare `llm_extracted` vs pharmacist judgment:

```bash
ssh balemed
cd /opt/bale-bot && . .venv/bin/activate
python3 deploy/scripts/list-shadow-reviews.py 50
```

3. Run `make validate` / `scripts/verify.ps1` locally before any live switch.

Then **only on VPS** `.env` (after owner approval):

```env
BALE_LLM_MODE=live
```

Restart: `sudo systemctl restart bale-bot`

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
- **One line per key** — run `dedupe-env-keys.py` if duplicates exist
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
| `deploy/scripts/test-shadow-classify.py` | One-shot classify via app LLM service |
| `deploy/scripts/post-shadow-test-webhooks.py` | Local loopback webhooks for shadow test |
| `deploy/scripts/ensure-llm-env.py` | Add missing LLM env keys |
| `deploy/scripts/check-env-safe.py` | Safe `.env` health check |
| `deploy/scripts/dedupe-env-keys.py` | Remove duplicate `.env` keys (keep last) |
| `deploy/scripts/vps-quick-check.py` | Sending + recent messages + LLM status |
| `deploy/scripts/list-shadow-reviews.py` | P2 — list `shadow_ok` rows + extracted fields |
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
python3 deploy/scripts/dedupe-env-keys.py
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

**Pin this chat** before archive — P1 shadow_ok confirmed; P2 owner review checklist.
