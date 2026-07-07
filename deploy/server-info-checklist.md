# VPS Server Info Checklist (Milestone 8)

Fill this out from your VPS provider panel **before** running deployment scripts.
Keep this file local only — do not commit real IPs, passwords, or tokens to Git.

## Provider and Server

| Field | Your value | Notes |
| --- | --- | --- |
| Provider name | | e.g. Iran-based VPS host |
| Server public IPv4 | | Required for SSH and DNS A record |
| SSH username | | Usually `root` on first login |
| SSH port | | Usually `22` |
| OS name and version | | Prefer Ubuntu 22.04 LTS or 24.04 LTS |
| vCPU / RAM / disk | | Minimum: 1 vCPU, 1.5 GB RAM, 25 GB SSD |
| Static IPv4 confirmed | yes / no | IP must not change unexpectedly |
| Provider console / rescue URL | | Use if UFW blocks SSH |

## Network and Ports

| Field | Your value | Notes |
| --- | --- | --- |
| Port 22 (SSH) open | yes / no | Provider firewall + later UFW |
| Port 80 (HTTP) open | yes / no | Required for Caddy HTTPS |
| Port 443 (HTTPS) open | yes / no | Required for Bale webhook |
| Snapshot or backup available | yes / no | Rollback path before hardening |

## Domain and Bale (do not paste secrets here)

| Field | Your value | Notes |
| --- | --- | --- |
| Domain for production | | e.g. `bot.example.ir` |
| DNS A record points to server IP | yes / no / pending | Required before step 8F |
| Bale bot token ready | yes / no | Set only in server `.env` |
| Webhook secret chosen | yes / no | Long random string; server `.env` only |
| Repository clone URL | | `git@github.com:hosseintajdari/bale-med.git` or HTTPS |

## Pre-flight SSH Test

From your local machine (PowerShell or terminal):

```bash
ssh -p YOUR_SSH_PORT YOUR_SSH_USER@YOUR_SERVER_IP
```

On the server after login:

```bash
whoami
cat /etc/os-release | head -5
```

If SSH works, run the deployment preflight script on the server:

```bash
cd /opt/bale-bot   # after clone in step 8B, or clone first
sudo bash deploy/scripts/00-preflight.sh
```

## Safety Defaults (first deployment)

- `BALE_ENABLE_SENDING=false`
- `BALE_ENABLE_ADMIN_NOTIFICATIONS=false`
- `BALE_STORE_RAW_UPDATES=false`
- Uvicorn binds `127.0.0.1:8000` only
- `/local/*` blocked at Caddy reverse proxy
