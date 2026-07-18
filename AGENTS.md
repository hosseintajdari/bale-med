# Repository Guidelines

## Agent quick reference

- **Validate:** `make validate`, `./scripts/verify.sh`, or `scripts/verify.ps1`
- **Lint:** `make lint` (ruff check + format check)
- **Run locally:** `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
- **Safety:** No diagnosis, dosage, or prescription replacement — see `docs/SAFETY_RULES.md`
- **Milestone:** 9 — LLM shadow on VPS; P2 shadow review UI done (PR #43); owner review of shadow messages before live mode; details in [docs/agents/HANDOFF.md](docs/agents/HANDOFF.md)

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
- Milestone 9: Started - LLM/AI integration (optional classification layer; shadow default).

For the latest milestone breakdown and sub-milestones, see [README.md](README.md).

## Current Milestone: Milestone 9

Goal:
Run LLM classification in shadow mode on the VPS, then gate live escalation behind pharmacy owner review of real shadow traffic.

Current state:
Milestones 1–8 foundation is complete. VPS dry-run deploy is live at `/opt/bale-bot`. Shadow LLM (P1) confirmed on real traffic. P2 shadow review UI built and merged (PR #43 — `feat/p2-shadow-review-ui`): annotation API and local review interface added. Next: pharmacy owner reviews 20–50 shadow messages before `BALE_LLM_MODE=live`. See [docs/agents/HANDOFF.md](docs/agents/HANDOFF.md).

Scope IN:

1. Shadow LLM verification and owner review tooling (`list-shadow-reviews.py`, HANDOFF checklist).
2. Documentation and repo structure aligned with Milestone 9 state.
3. Safe fixes that do not change pharmacy safety boundaries or patient-facing replies.

Scope OUT:

1. No diagnosis.
2. No prescription replacement.
3. No dosage recommendations.
4. No medication start/stop/change advice.
5. No autonomous triage decision.
6. No patient-facing LLM replies.
7. No `BALE_LLM_MODE=live` without explicit pharmacy owner approval.
8. No admin dashboard.



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

### Getting started

Practical guide and exercises for using skills in a new Cursor agent session. See `docs/agents/GETTING-STARTED.md`.

Project skills (twelve): `ask-matt`, `grilling`, `triage`, `to-issues`, `tdd`, `diagnosing-bugs`, `domain-modeling`, `codebase-design`, `resolving-merge-conflicts`, `devops-agent`, `git-github-scope`, `english-learning-replies`. Auto-routing: `.cursor/rules/auto-skill-routing.mdc`.

Global skills (Windows desktop — always available via lean-engineering-skills rule):
- `smart-coder` — entry point for all coding tasks (Python/FastAPI + TypeScript, HOW/WHY/ARCHITECT/DEBUG/REVIEW workflows)
- pstack: `how`, `why`, `architect`, `blast-radius`, `unslop`, `typescript-best-practices`, `figure-it-out`, `poteto-mode`
- `context7-mcp` — auto-fetches library docs (FastAPI, Pydantic, SQLAlchemy, etc.)
- `review-bugbot`, `review-security`

Recommended Cursor marketplace plugins: `agent-compatibility`, `github`, `context7`, `pstack`.

## User language (agents)

Agents should match the language the user writes in:

- **Persian/Farsi** — reply in simple Persian (user rule `vibe-coder-fa`).
- **English** — reply in simple learning English (project rule `.cursor/rules/english-learning-replies.mdc`): plain words, short answers (about 3–8 lines), learning tone, matched to a non-native level. Put the main meaning in the first sentence.



## Chat focus (agents)

Keep the user on one main goal per chat. See `.cursor/rules/stay-on-task.mdc`:

- Treat the user's first clear request as the session goal.
- No unrelated fixes, feature ideas, or long "you could also…" lists unless asked.
- Unrelated issues: mention briefly; fix only if the user agrees.
- Prefer one clear next step toward the main goal.



## Pin important chats (agents)

See `.cursor/rules/pin-important-chats.mdc`.

- Near the end of a useful session (or before archive), recommend **pinning** once if the chat has lasting value (setup, decisions, hard fixes, reusable checklists).
- Trigger phrases: `pin this` or `/pin-chat` — then give short UI steps to pin in the Agents sidebar.
- Do not nag every message; never block archiving.



## Learned User Preferences

- User writes in Persian (Farsi) in most chats; reply in Persian when they do.
- User prefers concise answers with one clear next step; avoid long option lists.
- User expects `smart-coder` as the primary entry point for all coding tasks in this project.
- User wants `git status` clean; add local-only files (e.g. `cursor-rtl.css`, `.cursor/mcp.json`, `.cursor/settings.json`) to `.gitignore`.
- User runs `/continual-learning` and `/agents-memory-updater` explicitly to maintain AGENTS.md memory.
- User confirms scope (handoff) before pushing to GitHub; never push without user confirmation.
- User prefers CLI scripts over web dashboards for owner-review workflows (shadow mode tooling).

## Learned Workspace Facts

- Shadow LLM (Milestone 9 P1) is confirmed working on real bot traffic on VPS at `/opt/bale-bot`.
- P2 milestone gate: pharmacy owner must review 20–50 shadow messages before `BALE_LLM_MODE=live`.
- Drug name validation rules and message classification standards for the LLM layer are planned for Milestone 9 P2.
- Two new skills created today: `.cursor/skills/english-learning-replies/` and `.cursor/skills/git-github-scope/`.
- `agent-skills-bale-med.mdc` and `auto-skill-routing.mdc` have local edits not yet committed to GitHub.
- `cursor-rtl.css` is a local Cursor IDE RTL styling fix; add to `.gitignore` — do not commit to repo.
- `smart-coder` (`C:\Users\hosse\.cursor\skills-cursor\smart-coder\SKILL.md`) is the comprehensive Windows skill combining HOW, WHY, ARCHITECT, BLAST-RADIUS, TDD, DEBUG, and REVIEW workflows.
- BaleMed has no UI frontend; shadow message review is CLI-only via `list-shadow-reviews.py`.
- Cursor has no built-in TODO panel (VS Code base); use Agent plan mode or extensions like TodoTree.

