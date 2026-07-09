# VPS Deployment (Milestone 8)

Scripts and templates for deploying the Bale pharmacy bot to an Iran-based Ubuntu VPS in **dry-run mode** (`BALE_ENABLE_SENDING=false`).

Full runbook: [docs/DEPLOYMENT_VPS.md](../docs/DEPLOYMENT_VPS.md).

## Before You Start

1. Complete [server-info-checklist.md](server-info-checklist.md) from your provider panel (keep it local).
2. Read [SECURITY-CHECKLIST.md](SECURITY-CHECKLIST.md) — keep tokens and secrets off Git and chat.
2. Confirm SSH: `ssh root@YOUR_SERVER_IP`
3. Have a **domain** with DNS A record to the server IP before steps 8F–8H.
4. Prepare `BALE_BOT_TOKEN` and `BALE_WEBHOOK_SECRET` — set only in `/opt/bale-bot/.env` on the server.

## Quick Path

On the VPS as `root` (first login):

```bash
git clone https://github.com/hosseintajdari/bale-med.git /opt/bale-bot
cd /opt/bale-bot
sudo bash deploy/scripts/install.sh preflight
sudo bash deploy/scripts/install.sh 8a
```

As `deploy` user:

```bash
sudo -u deploy bash /opt/bale-bot/deploy/scripts/install.sh 8b
bash /opt/bale-bot/deploy/scripts/03-configure-env.sh
nano /opt/bale-bot/.env   # set real token and webhook secret
bash /opt/bale-bot/deploy/scripts/04-manual-test.sh
sudo bash /opt/bale-bot/deploy/scripts/05-systemd.sh
```

After DNS points to the server:

```bash
export DOMAIN=your-domain.example
sudo bash /opt/bale-bot/deploy/scripts/06-caddy.sh
bash /opt/bale-bot/deploy/scripts/07-smoke-tests.sh
bash /opt/bale-bot/deploy/scripts/08-register-webhook.sh
bash /opt/bale-bot/deploy/scripts/09-monitor-dry-run.sh
```

Or orchestrate:

```bash
sudo bash deploy/scripts/install.sh through-8e
export DOMAIN=your-domain.example
bash deploy/scripts/install.sh through-8i
```

## Directory Layout

```text
deploy/
  server-info-checklist.md
  templates/
    bale-bot.service
    Caddyfile
    env.production.example
  scripts/
    00-preflight.sh … 09-monitor-dry-run.sh
    install.sh
```

## Safety Defaults

- `BALE_ENABLE_SENDING=false` until explicit pharmacy owner approval (Milestone 8J).
- Uvicorn on `127.0.0.1:8000` only; Caddy terminates HTTPS.
- `/local/*` returns 404 at the reverse proxy.
- Never commit `.env`, tokens, or database files.

## Rollback

| Issue | Action |
| --- | --- |
| SSH blocked by UFW | Provider rescue console |
| Bad deployment | `sudo systemctl stop bale-bot caddy` |
| Wrong webhook | Re-run `08-register-webhook.sh` or stop Caddy |
| Data loss | Provider snapshot or SQLite restore helper |
