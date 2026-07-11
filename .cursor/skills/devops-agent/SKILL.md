---
name: devops-agent
description: Runs BaleMed VPS deploy, verify, rollback, and server hygiene workflows. Use when the user mentions deploy, VPS, SSH, systemd, Caddy, webhook, dry-run, Milestone 8, scp from Windows, server logs, or production ops without calling a slash command.
---

# DevOps agent (BaleMed)

Efficient ops for this repo. Execute — do not only list steps.

## Safety defaults (always)

- `BALE_ENABLE_SENDING=false` until owner explicitly approves (Milestone 8J).
- No tokens, webhook secrets, or `.env` in Git.
- Local server notes: `deploy/servers/balemed.md` (gitignored).
- Pharmacy bot safety: `docs/SAFETY_RULES.md`.

## Verify before commit

```bash
make validate
# or: ./scripts/verify.sh  |  scripts/verify.ps1
```

## Deploy quick path

Docs: `deploy/README.md`, `docs/DEPLOYMENT_VPS.md`.

| Step | Script |
|------|--------|
| Preflight | `deploy/scripts/00-preflight.sh` |
| Hardening | `01-hardening.sh` |
| Bootstrap | `02-bootstrap.sh` |
| Env | `03-configure-env.sh` (quotes Persian `BALE_REPLY_TEXT`) |
| Manual test | `04-manual-test.sh` |
| systemd | `05-systemd.sh` |
| Caddy + HTTPS | `06-caddy.sh` (needs `DOMAIN`) |
| Smoke | `07-smoke-tests.sh` |
| Webhook | `08-register-webhook.sh` |
| Dry-run monitor | `09-monitor-dry-run.sh` |

Orchestrate: `bash deploy/scripts/install.sh <step>`.

## After scp from Windows

```bash
python3 deploy/scripts/normalize-deploy-scripts.py deploy/scripts
```

Then run `install.sh`. CRLF breaks bash (`pipefail\r`).

## Common fixes

| Problem | Fix |
|---------|-----|
| `.env` bash parse error (Persian text) | `python3 deploy/scripts/fix-env-reply-text.py /opt/bale-bot/.env` |
| Webhook 404 on Bale API | Check real `BALE_BOT_TOKEN` on server |
| Bot replies when should not | Confirm `BALE_ENABLE_SENDING=false` |

## Logs and health

```bash
sudo systemctl status bale-bot
sudo journalctl -u bale-bot -n 100 --no-pager
curl -sS https://YOUR_DOMAIN/health
```

## Privacy before Git

Never commit: real IPs in checklists, tokens, filled `server-info-checklist.md` with secrets.

## Learn one line

**Dry-run** = webhook receives messages and stores them, but the bot does not send real Bale replies until you flip `BALE_ENABLE_SENDING=true`.
