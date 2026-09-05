# CI (local and GitHub Actions)

## GitHub Actions

[validate.yml](validate.yml) runs on every push to `main`, on pull requests, or
manually from the Actions tab:

- `unittest`
- `compileall`
- `ruff check`

## On your laptop (before push)

```bash
make validate
# or: ./scripts/verify.sh  |  scripts/verify.ps1
```

On Windows without Git Bash, use `scripts\verify.ps1` instead of `make validate`.

## On the VPS (after deploy, safe dry-run)

```bash
cd /opt/bale-bot
bash deploy/scripts/09-monitor-dry-run.sh
```

This checks `BALE_ENABLE_SENDING=false`, recent DB rows (text length only), backup, and service logs — no real Bale sends.

For Milestone 9 shadow LLM checks, see [docs/agents/HANDOFF.md](../../docs/agents/HANDOFF.md) and `deploy/scripts/10-shadow-llm-verify.sh`.
