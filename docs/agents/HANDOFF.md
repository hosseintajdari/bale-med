# Handoff — BaleMed (new Agent chat)

**Date:** 2026-07-12  
**Branch:** `cursor/vps-iran-deployment-39a7`  
**Open PR:** https://github.com/hosseintajdari/bale-med/pull/37  
**Milestone:** 8 (VPS dry-run complete) → **8J** pending owner decision

Copy this file into a new chat, or say: *Read `docs/agents/HANDOFF.md` and continue.*

---

## Priority order (do in this sequence)

### P1 — Confirm dry-run end-to-end (blocking for 8J)

1. User sends one test message to **`@embednebot`** in Bale (e.g. `سلام تست`).
2. On VPS (`ssh balemed`):
   ```bash
   bash /opt/bale-bot/deploy/scripts/09-monitor-dry-run.sh
   ```
3. **Expect:**
   - Message count increases (was **3** on 2026-07-11).
   - `BALE_ENABLE_SENDING=false` in `/opt/bale-bot/.env`.
   - Webhook `POST` → **200** in `journalctl -u bale-bot`.
   - **No** auto-reply in Bale app.

### P2 — Merge deploy work to `main`

1. Review and merge **PR #37** after local verify:
   ```bash
   make validate
   # or: scripts/verify.ps1
   ```
2. No GitHub Actions on push (removed broken workflow). CI = local + VPS only — see `.github/workflows/README.md`.

### P3 — Milestone 8J (owner decision only)

- **Do not** set `BALE_ENABLE_SENDING=true` unless pharmacy owner explicitly approves.
- If approved later:
  ```bash
  sudo nano /opt/bale-bot/.env   # BALE_ENABLE_SENDING=true
  sudo systemctl restart bale-bot
  ```
- Rollback: set back to `false` and restart.

### P4 — Repo / agent hygiene (lower urgency)

- Reload Cursor after skill/rule changes (`Developer: Reload Window`).
- Skills: lean set in `.cursor/skills/README.md`; auto-routing in `.cursor/rules/auto-skill-routing.mdc`.
- Optional marketplace: `/add-plugin agent-compatibility`, `/add-plugin github`.

### P5 — Product next (after 8 stable)

- Milestone 9 (LLM): use `/grilling` + safety boundaries in `docs/SAFETY_RULES.md`.
- Build `CONTEXT.md` (domain glossary) with `domain-modeling`.

---

## What is already done

| Area | Status |
|------|--------|
| DNS | `embednet.ir` and `embednet.systems` → VPS IP |
| HTTPS | `https://embednet.systems/health` → `ok` |
| Caddy | `/local/*` → 404 publicly |
| systemd | `bale-bot` + `caddy` active |
| Webhook | Registered; Bale API OK with real token on server |
| Dry-run | Sending disabled; messages stored in SQLite |
| Deploy scripts | CRLF normalize, `fix-env-reply-text.py`, 8J sending-gate tests |
| Verify | `make validate` = unittest + compileall + ruff + `git diff --check` |
| Skills | 10 project skills incl. `devops-agent`; 14 duplicates removed |

---

## VPS quick reference

| Item | Value |
|------|--------|
| SSH | `ssh balemed` (local alias; details in gitignored `deploy/servers/balemed.md`) |
| App path | `/opt/bale-bot` |
| Domain | `embednet.systems` (production HTTPS) |
| Secrets | **Only** in `/opt/bale-bot/.env` (`chmod 600`) — never commit |

**After `scp` from Windows:**
```bash
python3 deploy/scripts/normalize-deploy-scripts.py deploy/scripts
```

**Monitor dry-run:**
```bash
bash /opt/bale-bot/deploy/scripts/09-monitor-dry-run.sh
```

---

## Privacy rules (always)

- Do **not** commit: `.env`, tokens, webhook secrets, real IPs in checklists.
- `deploy/servers/balemed.md` and filled `server-info-checklist.md` stay local.
- Test placeholders only in repo (`test-token`, `secret-token`).

---

## Pharmacy safety (always)

- No diagnosis, dosage advice, or prescription replacement.
- See `docs/SAFETY_RULES.md` and `AGENTS.md`.

---

## Key files

| Purpose | Path |
|---------|------|
| Deploy runbook | `docs/DEPLOYMENT_VPS.md` |
| Quick deploy | `deploy/README.md` |
| Agent start | `docs/agents/GETTING-STARTED.md` |
| Verify | `Makefile`, `scripts/verify.sh`, `scripts/verify.ps1` |
| CI note | `.github/workflows/README.md` |

---

## Suggested first message in new chat

```text
Read docs/agents/HANDOFF.md.

We are on Milestone 8J. I sent a test message to @embednebot — please confirm DB + logs (dry-run, no reply).
Then help merge PR #37 if verify passes.
```

---

## Git state (last known)

```
1e2755d feat: auto skill routing, devops agent, and local CI
ee6399d feat: lean skills, deploy helpers, and agent score tooling
```

**Pin this chat** if you archive the session — it has VPS setup, dry-run proof, and PR context.
