# Repository Guidelines

We are building a pharmacy automation chatbot connected to Bale messenger. Bale Bot API is similar to Telegram Bot API, but exact fields must be verified before production use.

## Goal
Build a minimal but production-minded MVP for a pharmacy assistant bot.

## Important Context
- The user is a PharmD building pharmacy automation tools.
- The bot is for a real pharmacy workflow, so safety, auditability, and privacy matter.
- Do not create a diagnostic or prescription-replacing bot.
- The bot should collect structured information and route cases to a pharmacist when needed.
- Keep all code simple, documented, and suitable for gradual deployment.

## Tech Stack
- Use Python.
- Use FastAPI for the backend.
- Use SQLite for the first local MVP.
- Use environment variables for secrets.
- Do not hardcode the Bale bot token.
- Prepare the project so it can later be deployed on a VPS.
- Use Git-friendly structure.

## Current Project Status
- Milestone 1: Done - Project skeleton and local foundation.
- Milestone 2: Done - Real Bale webhook on local laptop with tunnel and real reply.
- Milestone 3: Done - Secure webhook with secret path.
- Milestone 4: Done - Basic bot commands.
- Milestone 5: Done - Safe pharmacy reply layer.
- Milestone 6: Done - Better logging and admin review.
- Milestone 7: Done - VPS deployment preparation and repository alignment.
- Milestone 8: Started - Real VPS deployment workflow.
- Milestone 9: Planned - LLM/AI integration.

For the latest milestone breakdown and sub-milestones, see [README.md](README.md).

## Current Milestone: Milestone 8

Goal:
Prepare for real VPS deployment while keeping local development and verification reliable.

Current state:
Milestones 1-7 are complete. Milestone 8A tracks VPS readiness and the branch/PR workflow while waiting for confirmed VPS access. See [README.md](README.md) and [docs/DEPLOYMENT_VPS.md](docs/DEPLOYMENT_VPS.md) for deployment guidance.

Scope IN:
1. VPS readiness documentation and workflow alignment.
2. Agent-friendly local setup and verification docs.
3. Small, safe fixes that improve local bootstrap without changing pharmacy safety boundaries.

Scope OUT:
1. No diagnosis.
2. No prescription replacement.
3. No dosage recommendations.
4. No medication start/stop/change advice.
5. No autonomous triage decision.
6. No LLM integration.
7. No admin dashboard.
8. No production VPS hardening until access is confirmed.

## Milestone Workflow
Use this format for each project milestone:

```text
Milestone X: [name]

Goal:
[one clear goal]

Current state:
[short project state]

Base commit:
[latest commit hash]

Scope IN:
1.
2.
3.

Scope OUT:
1.
2.
3.

Verification:
python -m unittest discover -s tests
python -m compileall app tests
git diff --check

Run command:
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000

Done when:
1. Tests pass.
2. README or docs are updated if needed.
3. `git status` is clean after commit.
4. Commit message is:
   [commit message]

Important:
- Do not commit `.env`.
- Do not expose tokens/secrets.
- Do not commit `*.db`, `*.log`, or tunnel output.
- Do not make unrelated changes.
- If unrelated issues are found, report them but do not fix them in the milestone.
```

## Current Verification Commands
Use `unittest`, not `pytest`, unless the project intentionally changes test frameworks later.

On Linux and macOS, prefer `python3`. On Windows with an activated virtual environment, `python` is usually fine. You can also run `./scripts/verify.sh` from the repo root.

```bash
python3 -m unittest discover -s tests
python3 -m compileall app tests
git diff --check
```

## Current Local Run Command
Run the FastAPI app locally on port 8000:

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

After activating a virtual environment, `uvicorn app.main:app --host 127.0.0.1 --port 8000` also works.

## Commit Rules
- Commit only intended files for the active milestone.
- Do not commit `.env`.
- Do not commit SQLite database files such as `*.db` or `*.sqlite`.
- Do not commit `*.log` files.
- Do not commit tunnel output, public tunnel logs, or generated QR output.
- Do not expose the Bale bot token, webhook secret, or any other credential.
- Before committing, run the current verification commands.
- After committing, confirm `git status` is clean.

## Agent skills

### Issue tracker

GitHub Issues on `hosseintajdari/bale-med` via `gh` CLI; external PRs are a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`); create missing labels in GitHub when needed. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
