# Repository Guidelines

We are starting a new project: a pharmacy automation chatbot connected to Bale messenger. Bale Bot API is similar to Telegram Bot API.

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

## First Task
1. Inspect the current folder.
2. Create a clear project plan before coding.
3. Create these files:
   - `README.md`
   - `AGENTS.md`
   - `.gitignore`
   - `.env.example`
   - `requirements.txt`
   - `app/main.py`
   - `app/config.py`
   - `app/bale_client.py`
   - `app/handlers.py`
   - `app/models.py`
   - `app/database.py`
   - `docs/PROJECT_PLAN.md`
   - `docs/SAFETY_RULES.md`
4. Implement only a minimal working skeleton:
   - FastAPI app
   - health check endpoint
   - webhook endpoint for Bale updates
   - basic message router
   - simple SQLite storage for incoming messages
   - placeholder function for sending messages back to Bale
5. Add clear TODO comments where Bale API details must be filled after checking the exact Bale documentation.
6. Do not invent unknown Bale API fields. Use safe placeholders and document assumptions.
7. Add run instructions for Windows PowerShell.
8. After creating files, show:
   - file tree
   - what was created
   - how to run locally
   - what to do next

## Guardrails
- Do not overwrite existing files without asking.
- Do not add unnecessary frameworks.
- Do not build a complex architecture yet.
- Do not create medical advice logic yet.
- First milestone is: receive a message, store it, and prepare a safe reply path.

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
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001

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

## Current Milestone Status
- Milestone 1: Done - Project skeleton and local foundation.
- Milestone 2: Done - Real Bale webhook on local laptop with tunnel and real reply.
- Milestone 3: Next - Secure webhook with secret path.
- Milestone 4: Basic bot commands.
- Milestone 5: Safe pharmacy reply layer.
- Milestone 6: Better logging and admin review.
- Milestone 7: VPS deployment preparation.
- Milestone 8: Real VPS deployment.
- Milestone 9: LLM/AI integration.

## Current Verification Commands
Use `unittest`, not `pytest`, unless the project intentionally changes test frameworks later.

```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

## Current Local Run Command
Run the FastAPI app locally on port 8001:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

## Commit Rules
- Commit only intended files for the active milestone.
- Do not commit `.env`.
- Do not commit SQLite database files such as `*.db` or `*.sqlite`.
- Do not commit `*.log` files.
- Do not commit tunnel output, public tunnel logs, or generated QR output.
- Do not expose the Bale bot token, webhook secret, or any other credential.
- Before committing, run the current verification commands.
- After committing, confirm `git status` is clean.
