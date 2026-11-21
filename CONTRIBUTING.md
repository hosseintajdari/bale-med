# Contributing

This repository is a pharmacy workflow automation MVP connected to Bale messenger. Changes should stay small, reviewable, and safe for a real pharmacy context.

## Before You Change Code

1. Read [README.md](README.md), [docs/agents/HANDOFF.md](docs/agents/HANDOFF.md), [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md), and [docs/SAFETY_RULES.md](docs/SAFETY_RULES.md).
2. Confirm the change fits the current milestone.
3. Keep real secrets out of Git. Use `.env` locally and `.env.example` for placeholders.
4. Do not enable real outgoing Bale messages unless that is explicitly approved.

## Local Setup

Linux/macOS:

```bash
cd /path/to/bale-med
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
cd C:\path\to\bale-med
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with local values only. Do not commit `.env`.

## Verification

Run these before committing. On Linux/macOS, prefer `python3`. You can also run `./scripts/verify.sh` or `scripts\verify.ps1` on Windows.

```bash
make validate
# or manually:
python3 -m unittest discover -s tests
python3 -m compileall app tests
git diff --check
```

GitHub Actions runs the same checks on every pull request (see `.github/workflows/validate.yml`).

## Safety Rules for Contributions

- Do not add diagnosis, prescription replacement, dosage advice, or medication start/stop/change advice.
- Route medical judgment, urgent, unclear, pregnancy, allergy, child medication, side effect, overdose, and controlled medication cases to pharmacist review.
- Do not log tokens, secrets, raw webhook payloads, chat ids, or full message text.
- Keep uncertain Bale API details in [docs/ASSUMPTIONS_BALE_API.md](docs/ASSUMPTIONS_BALE_API.md).

## Commit Style

Use small, focused commit messages, for example:

```text
docs: clarify VPS readiness checklist
feat: store review status metadata
test: cover pending review listing
fix: handle malformed Bale API base URL
```

## Issues and Pull Requests

Use the existing issue templates for bugs, documentation, features, or clinical/safety gaps. Start with `needs-triage`; maintainers assess scope before assigning implementation readiness. See [triage labels](docs/agents/triage-labels.md) and [tracker workflow](docs/agents/issue-tracker.md).

Use synthetic examples only. Report security or sensitive-data concerns privately as described in [SECURITY.md](SECURITY.md). Keep clinical/safety gap reports available even when no code change is proposed.

For pull requests, preserve the safety checklist, link the relevant issue or milestone gate, and report exact verification commands and results (or why they were not run). A readiness label or passing CI does not replace human review or pharmacy owner approval for real sending or live LLM mode.
