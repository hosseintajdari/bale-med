# Handoff — BaleMed (new Agent chat)

**Date:** 2026-07-12  
**Branch:** `cursor/vps-iran-deployment-39a7` (local; commit Milestone 9 before push)  
**Open PR:** https://github.com/hosseintajdari/bale-med/pull/37  
**GitHub issue:** https://github.com/hosseintajdari/bale-med/issues/9  
**Milestone:** 9 MVP coded locally → **shadow deploy + owner review** next

Copy this file into a new chat, or say: *Read `docs/agents/HANDOFF.md` and continue.*

Works from **Cursor desktop, web, or mobile** — same repo path and issue #9 brief.

---

## What was just finished (this session)

Milestone 9 **LLM safety layer MVP** implemented per issue #9 agent brief:

| Piece | Path / note |
|-------|-------------|
| LLM module | `app/llm/` — client, validator, redaction, service |
| Wiring | `app/handlers.py` — shadow/live behind env flags |
| DB columns | `incoming_messages`: `llm_extracted_json`, `llm_model_id`, `llm_latency_ms`, `llm_validation_pass`, `llm_status` |
| Local review | `/local/reviews/pending` returns `llm_extracted`, `llm_status`, etc. |
| Safety docs | `docs/SAFETY_RULES.md` — LLM section |
| Env templates | `.env.example`, `deploy/templates/env.production.example` |
| Tests | `tests/test_llm.py` + updates; **88 tests pass** |

**Safety defaults (unchanged behavior until you opt in):**
- `BALE_ENABLE_LLM=false`
- `BALE_LLM_MODE=shadow`
- Patients still get **template replies only** (`app/replies.py`)
- LLM never sends text to patients
- Keyword escalation **cannot** be downgraded by LLM in live mode

---

## Priority order (do in this sequence)

### P1 — Commit + push Milestone 9 (if not done yet)

```bash
git status
make validate          # or: scripts/verify.ps1 on Windows
git add app/llm/ tests/test_llm.py app/config.py app/database.py app/handlers.py \
  .env.example deploy/templates/env.production.example docs/SAFETY_RULES.md \
  AGENTS.md README.md tests/test_config.py tests/test_main.py docs/agents/HANDOFF.md
git commit -m "feat: Milestone 9 LLM classification layer (shadow default)"
git push -u origin HEAD
```

Open or update PR; link **closes #9** when ready.

### P2 — VPS shadow test (recommended before live)

On VPS (`ssh balemed`), add to `/opt/bale-bot/.env` (never commit real key):

```env
BALE_ENABLE_LLM=true
BALE_LLM_MODE=shadow
BALE_LLM_API_BASE_URL=https://YOUR_PROVIDER/v1
BALE_LLM_API_KEY=YOUR_KEY
BALE_LLM_MODEL=gpt-4o-mini
```

Deploy updated code, restart:

```bash
sudo systemctl restart bale-bot
```

Send **5–10 test messages** to `@embednebot`. Confirm:

1. Replies unchanged (templates only; `BALE_ENABLE_SENDING` still your choice).
2. From VPS loopback only:
   ```bash
   curl -s http://127.0.0.1:8000/local/reviews/pending | python3 -m json.tool
   ```
3. Pending items show `llm_extracted` / `llm_status` when LLM ran.
4. Logs show `llm_status=shadow_ok` (no prompt/response text in logs).

### P3 — Human go-live gate (before `BALE_LLM_MODE=live`)

**Do not automate.** Owner must:

1. Approve LLM live mode explicitly.
2. Review **20–50 real shadow messages** (extracted fields vs pharmacist judgment).
3. Run `make validate` / `scripts/verify.ps1`.

Then only:

```env
BALE_LLM_MODE=live
```

Live mode: LLM `needs_review` **unions** with keywords; failures → `llm_fail_safe` escalation.

### P4 — Milestone 8 carry-over (if still open)

- PR #37 merge after verify.
- `BALE_ENABLE_SENDING=true` only with **pharmacy owner approval** (8J).
- Dry-run monitor: `bash /opt/bale-bot/deploy/scripts/09-monitor-dry-run.sh`

### P5 — Later (out of MVP scope)

- Multi-provider LLM
- Pharmacist draft summaries from LLM
- `CONTEXT.md` / domain glossary (`domain-modeling` skill)

---

## Env reference (Milestone 9)

| Variable | Default | Meaning |
|----------|---------|---------|
| `BALE_ENABLE_LLM` | `false` | Master switch |
| `BALE_LLM_MODE` | `shadow` | `shadow` = store only; `live` = union escalation |
| `BALE_LLM_API_BASE_URL` | empty | OpenAI-compatible base URL |
| `BALE_LLM_API_KEY` | empty | Never commit |
| `BALE_LLM_MODEL` | `gpt-4o-mini` | Model id for audit |
| `BALE_LLM_TIMEOUT_SECONDS` | `10` | Fail-safe timeout |

---

## Key files

| Purpose | Path |
|---------|------|
| Agent brief (source) | GitHub issue #9 |
| LLM service | `app/llm/service.py` |
| Validator (banned advice) | `app/llm/validator.py` |
| Routing seam | `app/handlers.py` → `route_update` |
| Template replies (unchanged) | `app/replies.py` |
| Safety rules | `docs/SAFETY_RULES.md` |
| Deploy runbook | `docs/DEPLOYMENT_VPS.md` |
| Verify | `Makefile`, `scripts/verify.ps1` |

---

## Pharmacy safety (always)

- No diagnosis, dosage advice, or prescription replacement.
- LLM output is **internal only**; validator rejects clinical advice in string fields.
- Admin Bale notifications must **not** include LLM extracted fields.

---

## Suggested first message in new chat (web / mobile)

```text
Read docs/agents/HANDOFF.md.

Continue Milestone 9: push the LLM shadow layer, deploy to VPS with BALE_ENABLE_LLM=true and BALE_LLM_MODE=shadow, then help me verify extracted fields on /local/reviews/pending.
```

---

## Verification checklist

```bash
python -m unittest discover -s tests
python -m compileall app tests
python -m ruff check app tests
git diff --check
```

**Pin this chat** before archive — Milestone 9 implementation + shadow go-live steps.
