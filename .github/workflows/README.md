# CI (local and GitHub Actions)

## GitHub Actions

[validate.yml](validate.yml) runs on every push to `main`, on pull requests, and manually (`workflow_dispatch`):

- `unittest`
- `compileall`
- `ruff check`
- `git diff --check`

It mirrors `make validate` / `scripts/verify.sh`.

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

## Troubleshooting: `startup_failure` / `BuildFailed`

If Actions runs show **startup_failure** with path `BuildFailed` and **0 jobs**, the workflow file is fine — GitHub could not start any runner. Common causes on a **private** repo:

1. **Actions disabled** — Repo → **Settings** → **Actions** → **General** → allow actions.
2. **Account billing** — Private repos need Actions minutes on your GitHub plan; add a payment method if required.
3. **Organization policy** — If the repo moves under an org, check org Actions policy.

After enabling Actions:

1. Open **Actions** → **validate** → **Run workflow** (manual dispatch).
2. Or push a small commit to `main` and confirm the run uses workflow `validate`, not `BuildFailed`.

Local `make validate` remains the source of truth when GitHub Actions is unavailable.
