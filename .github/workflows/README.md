# CI (local and VPS)

GitHub Actions **tests workflow is disabled** — previous self-hosted runs failed at startup (runner/path mismatch; no GitHub-hosted minutes needed).

## On your laptop (before push)

```bash
make validate
# or: ./scripts/verify.sh  |  scripts/verify.ps1
```

## On the VPS (after deploy, safe dry-run)

```bash
cd /opt/bale-bot
bash deploy/scripts/09-monitor-dry-run.sh
```

This checks `BALE_ENABLE_SENDING=false`, recent DB rows (text length only), backup, and service logs — no real Bale sends.

## Re-enable GitHub Actions later

Only if you add a working self-hosted runner or paid GitHub-hosted runners. Until then, use local `make validate`.
