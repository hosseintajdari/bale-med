# Project Plan

## Current Status
The project has a minimal FastAPI webhook app, SQLite message storage, a cautious Bale API client, secure webhook secret-path handling, dry-run reply behavior, basic safe commands for `/start`, `/help`, and `/status`, a safe pharmacy reply layer, review metadata, and a minimal duplicate-delivery guard.

Milestone 7A is done. The next milestone should stay small and continue preparing the MVP for safe deployment or local pharmacist review without changing production infrastructure yet.

## Long-Term Product Vision
Build a safe pharmacy automation assistant for Bale that supports a real pharmacy workflow from first contact through pharmacist review. The assistant should receive messages, collect structured intake information, avoid clinical decision-making, preserve auditability, and route cases to a pharmacist when judgment is needed.

Later milestones may add better logging, pharmacist/admin review tools, VPS deployment, and LLM/AI integration. AI must be introduced only inside pharmacist-approved boundaries and must not diagnose, prescribe, replace a pharmacist, or recommend medication changes.

The vision and milestone order are living project guidance. They may change as requirements, pharmacy workflow details, or Bale API constraints become clearer. Update this plan before making implementation changes that alter the project direction.

## Milestone Map
1. Milestone 1: Done - Project skeleton and local foundation.
2. Milestone 2: Done - Real Bale webhook on local laptop with tunnel and real reply.
3. Milestone 3: Done - Secure webhook with secret path.
4. Milestone 4: Done - Basic bot commands.
5. Milestone 5: Done - Safe pharmacy reply layer.
6. Milestone 6: Done - Better logging and admin review.
7. Milestone 7: Current - VPS deployment preparation.
   - Milestone 7A: Done - Bale webhook duplicate-delivery guard.
8. Milestone 8: Planned - Real VPS deployment.
9. Milestone 9: Planned - LLM/AI integration.

## Completed Milestones

### Milestone 1: Local Webhook Skeleton
Built a small FastAPI service that can receive Bale webhook updates, store incoming message data in SQLite, and prepare a safe reply path without sending medical advice.

### Milestone 2: Real Bale Webhook on Local Laptop
Verified the local app can be exposed through a public tunnel, receive real Bale webhook messages, and use the Bale send path when explicitly enabled.

### Milestone 3: Secure Webhook with Secret Path
Changed the webhook route to `/webhook/bale/{secret}`, added `BALE_WEBHOOK_SECRET`, and made wrong secrets return 404.

### Milestone 4: Basic Bot Commands
Added simple command replies for `/start`, `/help`, and `/status`. These replies are intentionally non-medical: they introduce the bot as a pharmacy message intake assistant, list available commands, and confirm the service is running. `/status` also reports whether sending is ON or OFF without exposing secrets. Unknown text keeps the configured safe acknowledgement behavior.

### Milestone 5: Safe Pharmacy Reply Layer

Added a deterministic safe reply layer that asks for structured intake information for normal pharmacy messages and escalates high-risk, unclear, or medical-judgment messages to pharmacist review without giving medical advice. Tests cover normal intake, escalation, common allergy and pregnancy wording, command behavior, and preserved safety boundaries.

## Completed Milestone: Milestone 6 - Better Logging and Admin Review

### Goal
Add a minimal review-tracking and logging foundation so pharmacist-review cases are visible in stored message metadata and future admin tools can use a reliable audit trail.

### Current State
Incoming messages now store basic review metadata: whether pharmacist review is needed, a simple review reason, and a review status. Escalation-triggering messages are marked pending for pharmacist review; normal intake and command messages are marked not required. A minimal local JSON endpoint lists pending pharmacist-review items without exposing raw webhook payloads. Sanitized audit logs record webhook intake and reply preparation without logging secrets, raw payloads, chat ids, or full message text.

### Scope IN
1. Store whether each incoming message needs pharmacist review.
2. Store a simple review reason for escalation-triggering messages.
3. Store a basic review status that can support later pharmacist/admin tools.
4. Keep logging useful without logging secrets, raw payloads, chat ids, or full message text.
5. Add a minimal local-only pending-review JSON endpoint.
6. Add tests for normal intake, escalation metadata, sanitized logging, command behavior, pending-review listing, and fresh SQLite initialization.
7. Update `README.md`, `docs/PROJECT_PLAN.md`, and `docs/SAFETY_RULES.md` if behavior changes.

### Scope OUT
- No diagnosis.
- No differential diagnosis.
- No prescription replacement.
- No medication start/stop/change advice.
- No dosage recommendation.
- No autonomous triage decision.
- No LLM integration.
- No admin dashboard.
- No VPS deployment changes.

### Safety Rules
- If a message asks for medical judgment, escalate to pharmacist review.
- If a message includes urgent symptoms, serious side effects, pregnancy/breastfeeding, child medication, allergy, overdose, controlled medication, or unclear medication use, escalate to pharmacist review.
- When unsure, escalate by default.
- Replies should collect information and acknowledge receipt; they must not make clinical decisions.
- Review metadata is operational tracking only; it is not a diagnosis, treatment decision, or emergency triage decision.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

## Completed Milestone: Milestone 7A - Bale Webhook Duplicate-Delivery Guard

### Goal
Add a minimal idempotency foundation so duplicate webhook deliveries do not create duplicate database rows when a stable external identifier is available.

### Current State
Incoming messages now store a nullable internal `external_event_id`. The app derives this value from top-level `update_id` when present, otherwise from `message.chat.id` plus `message.message_id` when both are present. If no stable identifier can be derived, the message is still stored. Recognized duplicates return the existing stored row id, avoid a second insert, and skip duplicate reply preparation.

### Scope OUT
- No diagnosis.
- No protocol engine.
- No AI or LLM integration.
- No structured intake workflow.
- No admin dashboard.
- No VPS deployment changes.
- No webhook registration.
- No enabling real outgoing sends.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

## Current Milestone: Milestone 7 - VPS Deployment Preparation

### Goal
Prepare a clear, safe VPS deployment checklist and runbook so the project can move to real deployment later without guessing, exposing secrets, or changing production infrastructure too early.

### Current State
The app runs locally, uses environment variables for secrets, keeps outgoing Bale messages disabled by default, stores data in SQLite, and has a minimal VPS runbook in `docs/DEPLOYMENT_VPS.md`. Milestone 7 should improve deployment readiness only. Real VPS setup, DNS, SSL, firewall changes, and webhook registration remain separate approval-gated work.

### Pieces
1. VPS readiness checklist: define the exact prerequisites before deployment, including domain, Ubuntu VPS, deploy user, Python version, HTTPS reverse proxy, firewall plan, backup path, and secret handling.
2. Environment preparation: document production-like `.env` values using placeholders only, keep `BALE_ENABLE_SENDING=false`, and confirm `.env` remains uncommitted.
3. App run strategy: document the local-only uvicorn command, the intended VPS command, and the systemd service shape without installing it yet.
4. HTTPS and reverse proxy plan: document whether Nginx or Caddy will terminate HTTPS, how traffic should forward to `127.0.0.1:8000`, and which checks must pass before exposing the webhook.
5. Webhook setup plan: document the final public webhook URL shape and the Bale API assumptions that must be verified before calling `setWebhook` for production.
6. Storage and backup plan: document the SQLite file location, backup expectation, restore check, and retention question for pharmacy workflow safety.
7. Operations checklist: document restart, status, logs, smoke test, rollback, and what information must never be logged.
8. Deployment decision gate: list the exact checks that must pass before Milestone 8 begins.

### Scope IN
1. Improve deployment documentation and checklists.
2. Keep deployment commands copy-pasteable and beginner-friendly.
3. Add missing safety gates around secrets, logging, backups, HTTPS, and webhook setup.
4. Keep all values in docs as placeholders unless they are safe defaults.
5. Verify the docs-only change with the normal project checks.

### Scope OUT
- No real VPS deployment.
- No DNS, SSL, firewall, Nginx, Caddy, or systemd changes on a server.
- No real webhook registration for production.
- No enabling `BALE_ENABLE_SENDING=true`.
- No real secrets in Git.
- No LLM/AI integration.
- No admin dashboard.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
git status --short
```

### Done When
1. `docs/DEPLOYMENT_VPS.md` has a practical Milestone 7 checklist.
2. `README.md` and this project plan point to Milestone 7 correctly.
3. The normal verification commands pass.
4. No secrets, database files, logs, tunnel output, or production config are committed.
5. Commit message is:
   `docs: define milestone 7 deployment prep`

## Known Assumptions and Open Questions
- Webhook payload shape is treated as Telegram-like for now (`message`, `message.chat.id`, `message.message_id`, `message.text`) with optional top-level `update_id`.
- Duplicate-delivery handling uses `update_id` if present, otherwise `chat_id + message_id`. The exact Bale uniqueness contract still needs official confirmation.
- Bale send-message endpoint, method, headers, and payload contract still need confirmation before production use.
- Webhook authentication/signature mechanism is unknown beyond the current secret path and must be confirmed before public deployment.
- Canonical tracker: `docs/ASSUMPTIONS_BALE_API.md`.

## Readiness Gates Before Enabling Real Use
1. Confirm Bale webhook schema with official documentation and update code/docs accordingly.
2. Confirm Bale outbound send-message contract and test in a non-production environment.
3. Confirm whether Bale supports webhook signature/header authentication beyond secret-path protection.
4. Validate VPS runbook end-to-end, including restart and log inspection.
5. Review SQLite storage path, backup, and retention strategy for operational safety.
6. Keep `BALE_ENABLE_SENDING=false` until the exact Bale behavior is confirmed.
7. Complete Milestone 7 deployment preparation before broad patient-facing use.
