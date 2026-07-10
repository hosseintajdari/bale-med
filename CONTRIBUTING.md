# Contributing

This repository is a pharmacy workflow automation MVP connected to Bale messenger. Changes should stay small, reviewable, and safe for a real pharmacy context.

## Before You Change Code

1. Read [README.md](README.md), [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md), and [docs/SAFETY_RULES.md](docs/SAFETY_RULES.md).
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
cd C:\Users\Maryam-pc\projects\bale
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with local values only. Do not commit `.env`.

## Verification

Run these before committing. On Linux/macOS, prefer `python3`. You can also run `./scripts/verify.sh`.

```bash
python3 -m unittest discover -s tests
python3 -m compileall app tests
git diff --check
```

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
``
