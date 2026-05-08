# Project Plan

## Current Status
The project has a minimal FastAPI webhook app, SQLite message storage, a cautious Bale API client, secure webhook secret-path handling, dry-run reply behavior, Persian user-facing replies for `/start`, `/help`, `/status`, and safe pharmacy intake/escalation flows, review metadata, a minimal duplicate-delivery guard, local-only pharmacist review status actions, optional Bale admin review notifications, local SQLite backup and restore helpers, a final deployment readiness checklist, a Milestone 8 VPS deployment execution plan, and repository/issue alignment notes.

Milestone 7A, Milestone 7B, Milestone 7C, Milestone 7D, Milestone 7E, Milestone 7F, Milestone 7G, and Milestone 7I are done. Milestone 8 planning is documented. Milestone 8A has started as VPS readiness and GitHub PR workflow tracking while waiting for confirmed VPS access.

## Long-Term Product Vision
Build a safe pharmacy automation assistant for Bale that supports a real pharmacy workflow from first contact through pharmacist review, especially where pharmacy teams need constrained, auditable tools for rural or border healthcare workflows. The assistant should receive messages, collect structured intake information, avoid clinical decision-making, preserve auditability, and route cases to a pharmacist when judgment is needed.

The project is workflow-based, pharmacist-centered, safety-first, local-first, and AI-optional. Later milestones may add real VPS deployment, stronger pharmacist/admin review tools, and LLM/AI integration. AI must be introduced only inside pharmacist-approved boundaries and must not diagnose, prescribe, replace a pharmacist, or recommend medication changes.

The vision and milestone order are living project guidance. They may change as requirements, pharmacy workflow details, or Bale API constraints become clearer. Update this plan before making implementation changes that alter the project direction.

## Milestone Map
1. Milestone 1: Done - Project skeleton and local foundation.
2. Milestone 2: Done - Real Bale webhook on local laptop with tunnel and real reply.
3. Milestone 3: Done - Secure webhook with secret path.
4. Milestone 4: Done - Basic bot commands.
5. Milestone 5: Done - Safe pharmacy reply layer.
6. Milestone 6: Done - Better logging and admin review.
7. Milestone 7: Done - VPS deployment preparation and repository alignment.
   - Milestone 7A: Done - Bale webhook duplicate-delivery guard.
   - Milestone 7B: Done - Minimal local pharmacist review actions.
   - Milestone 7C: Done - Local SQLite backup and retention safety foundation.
   - Milestone 7D: Done - Final deployment readiness checklist.
   - Milestone 7E: Done - Local SQLite restore rehearsal.
   - Milestone 7F: Done - Persian and RTL-safe user-facing replies.
   - Milestone 7G: Done - Bale admin review notifications.
   - Milestone 7I: Done - Repository context and issue alignment.
8. Milestone 8: Started - Real VPS deployment workflow.
   - Milestone 8A: Started - VPS readiness and GitHub PR workflow; waiting for VPS access.
   - Milestone 8B: Planned - Install Python, Git, venv, and clone repo.
   - Milestone 8C: Planned - Configure `.env` with placeholders and keep sending disabled.
   - Milestone 8D: Planned - Run app manually on `127.0.0.1:8000`.
   - Milestone 8E: Planned - Add systemd service.
   - Milestone 8F: Planned - Add reverse proxy and HTTPS.
   - Milestone 8G: Planned - Run smoke tests.
   - Milestone 8H: Planned - Register Bale webhook with production URL.
   - Milestone 8I: Planned - First monitored dry-run operation.
   - Milestone 8J: Planned - Decide whether to enable real sending later.
9. Milestone 9: Planned - LLM/AI integration.

## Active Milestone: Milestone 8A - VPS Readiness and GitHub PR Workflow

### Goal
Start Milestone 8 with a professional branch, pull request, and merge workflow while waiting for real VPS access.

### Current State
No VPS access has been confirmed yet. Milestone 8A is open only to track readiness and GitHub workflow discipline before server-side work begins.

### Scope IN
1. Use one branch and pull request per Milestone 8 submilestone.
2. Keep the first Milestone 8A change documentation-only.
3. Keep `BALE_ENABLE_SENDING=false` as the first deployment safety default.
4. Wait for confirmed VPS access before server hardening or app deployment.
5. Define the VPS provider details that must be collected before buying or logging in by SSH.

### Scope OUT
- No real VPS deployment.
- No DNS, SSL, firewall, Caddy, Nginx, or systemd changes on a server.
- No production webhook registration.
- No enabling `BALE_ENABLE_SENDING=true`.
- No secrets in Git.
- No app behavior changes.

### Verification
```powershell
git diff --check
```

For any later Milestone 8 code or config change, also run:

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```

### GitHub Workflow
Each next submilestone should start from synced `main`, use a branch named like `codex/milestone-8x-short-name`, open a draft PR, pass review/checks, merge to `main`, and sync local `main` before the next branch starts.

### Done When
1. The Milestone 8A branch is pushed.
2. A draft PR into `main` is opened.
3. The PR is merged after checks/review.
4. Local `main` is synced after merge.
5. The VPS purchase/access checklist names the exact provider details needed before any server command runs.

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

## Completed Milestone: Milestone 7B - Minimal Local Pharmacist Review Actions

### Goal
Add minimal local-only pharmacist review status update behavior without adding a dashboard, public admin API, diagnosis, treatment recommendations, protocol engine, or AI.

### Current State
Pending pharmacist-review items can be listed through `/local/reviews/pending` and marked reviewed through `POST /local/reviews/{message_id}/mark-reviewed`. The action is local-only, returns 404 for missing items, updates only `pending -> reviewed`, and returns a safe unchanged response when the item is already reviewed or otherwise not pending. Reviewed items no longer appear in the pending review list.

### Scope OUT
- No dashboard.
- No authentication system.
- No public admin API.
- No diagnosis.
- No treatment recommendation.
- No protocol engine.
- No AI or LLM integration.
- No VPS deployment changes.
- No enabling real outgoing sends.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

## Completed Milestone: Milestone 7 - VPS Deployment Preparation

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

## Completed Milestone: Milestone 7C - Data Retention and Backup Safety Foundation

### Goal
Add a minimal local-first SQLite backup and data retention safety foundation before real VPS deployment.

### Current State
The app has a `create_sqlite_backup()` helper that reads the configured `DATABASE_PATH`, creates a local `backups/` directory when needed, and copies the SQLite database file to a timestamped backup filename. The helper copies only the configured database file and does not copy `.env`, secrets, logs, or tunnel output.

The database stores incoming message metadata, message text, duplicate-delivery identifiers, review metadata, timestamps, and raw webhook storage status. Raw webhook payload storage remains disabled by default.

### Scope OUT
- No cloud backup.
- No automated cron.
- No encryption system yet.
- No retention deletion automation.
- No patient dashboard.
- No public admin endpoint.
- No AI or LLM integration.
- No diagnosis.
- No treatment recommendation.
- No protocol engine.
- No real VPS deployment.
- No enabling real outgoing sends.

### Retention Notes
Patient and message data should not be kept forever without a pharmacy-approved retention policy. Automatic deletion and retention scheduling are postponed until the pharmacy workflow, audit needs, and deployment environment are clearer.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

## Completed Milestone: Milestone 7D - Final Deployment Readiness Checklist

### Goal
Finalize a clear go/no-go checklist before starting real VPS deployment.

### Current State
The final deployment readiness checklist is documented in `docs/DEPLOYMENT_VPS.md`. It separates items that are ready for Milestone 8 planning from blockers that must be resolved before public exposure.

### Ready
- Duplicate webhook delivery guard exists.
- Local pharmacist review actions exist.
- SQLite backup helper exists and the manual backup command is documented.
- Webhook secret path is implemented.
- `BALE_ENABLE_SENDING=false` is the required first VPS deployment setting.
- Raw webhook storage is disabled by default.
- Sanitized logging expectations are documented.
- Rollback plan is documented.

### Still Blocked Before Public Exposure
- HTTPS and reverse proxy must be configured and verified.
- Firewall plan must be defined and approved.
- Local-only endpoints must not be publicly exposed.
- Backup command must be tested on the deployment host.
- Restore process must be documented and tested.
- Bale webhook assumptions must be verified with official documentation.
- Bale send-message assumptions must be verified before real sending.
- VPS logs must be checked for secret and patient-data safety.
- Retention duration and deletion process must be approved before long-term real patient data storage.

### Scope OUT
- No code changes.
- No tests changes.
- No real VPS deployment.
- No DNS, SSL, firewall, or reverse-proxy changes.
- No webhook registration.
- No enabling `BALE_ENABLE_SENDING=true`.
- No AI, diagnosis, dashboard, or database schema change.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

## Completed Milestone: Milestone 7E - SQLite Restore Rehearsal

### Goal
Add a minimal local restore rehearsal so SQLite backup files can be tested before real VPS deployment.

### Current State
The app has a `restore_sqlite_backup()` helper that copies an explicit backup file into the configured `DATABASE_PATH`. It creates the target parent directory if missing, raises a controlled error when the backup file is missing, and refuses to overwrite an existing database by default.

The restore command is documented in `README.md` and `docs/DEPLOYMENT_VPS.md`. Deployment-host backup and restore tests are still required before broad patient-facing use.

### Scope OUT
- No cloud backup.
- No automated restore.
- No cron.
- No encryption system yet.
- No retention deletion automation.
- No public restore API.
- No dashboard.
- No real VPS deployment.
- No DNS, SSL, firewall, or reverse-proxy changes.
- No webhook registration.
- No enabling `BALE_ENABLE_SENDING=true`.
- No AI, diagnosis, treatment recommendation, or protocol engine.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

## Completed Milestone: Milestone 7F - Persian and RTL-Safe User-Facing Replies

### Goal
Translate and standardize user-facing bot replies into clear Persian suitable for Bale mobile users.

### Current State
The `/start`, `/help`, `/status`, normal intake, and pharmacist-review escalation replies are Persian, short, line-broken, and avoid complex formatting. English command names remain isolated as `/start`, `/help`, and `/status`. Internal logs and operational metadata remain in English.

The Persian replies keep the safety boundaries explicit: the bot does not diagnose, prescribe, recommend dosage, advise medication changes, or replace pharmacist or physician judgment. Escalation replies direct medical decisions to pharmacist review and tell users with severe or urgent symptoms to seek urgent medical care.

### Scope OUT
- No AI or LLM integration.
- No diagnosis.
- No treatment advice.
- No medication recommendation.
- No protocol engine.
- No dashboard.
- No VPS deployment.
- No webhook registration.
- No enabling `BALE_ENABLE_SENDING=true`.
- No database schema change.
- No workflow redesign.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

## Completed Milestone: Milestone 7G - Bale Admin Review Notifications

### Goal
Send a safe optional Bale admin notification when an incoming message needs pharmacist review.

### Current State
The app can prepare admin notification metadata for messages marked `needs_review=true`. Notifications are disabled by default with `BALE_ENABLE_ADMIN_NOTIFICATIONS=false`. If admin notifications are enabled and `BALE_ENABLE_SENDING=true`, the bot sends the notification to `BALE_ADMIN_CHAT_ID`.

Notification text includes the stored message id, review reason, a short sanitized preview, and an instruction to check `/local/reviews/pending`. It does not include raw webhook payloads, secrets, chat ids, or full patient text. Duplicate webhook deliveries do not prepare or send a second admin notification.

This is operational awareness only. It is not a dashboard, not triage, and not a clinical decision system. Web UI and admin dashboard work remain postponed.

### Scope OUT
- No Web UI.
- No dashboard.
- No login or authentication system.
- No public admin endpoint.
- No AI or LLM integration.
- No diagnosis.
- No treatment recommendation.
- No protocol engine.
- No real VPS deployment.
- No webhook registration.
- No enabling `BALE_ENABLE_SENDING=true` by default.
- No database schema change.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

## Completed Milestone: Milestone 7I - Repository Context and Issue Alignment

### Goal
Align repository documentation, milestone status, and GitHub issue review notes with the actual implementation without marketing exaggeration.

### Current State
The README and project plan now describe the project as a local-first FastAPI pharmacy workflow assistant rather than a bare skeleton. They list the implemented secure webhook, Persian replies, duplicate-delivery guard, pharmacist review workflow, SQLite backup/restore helpers, optional admin notifications, postponed Web UI/AI work, and honest deployment status.

GitHub issue state was reviewed without editing issues in this milestone. The repository is private and has no GitHub repository description or homepage set. Direct GitHub Project board read access was not available through the exposed tools.

### Scope OUT
- No application code changes.
- No feature changes.
- No AI or LLM integration.
- No dashboard.
- No VPS deployment.
- No medical claims.
- No fake impact metrics.
- No automatic GitHub issue changes.

### Verification
```powershell
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

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
5. Verify HTTPS, reverse proxy, and firewall plan before public exposure.
6. Confirm local-only endpoints are not exposed publicly.
7. Review SQLite storage path, backup command, restore command, and retention strategy for operational safety.
8. Keep `BALE_ENABLE_SENDING=false` until the exact Bale behavior is confirmed and real sending is explicitly approved.
9. Complete Milestone 8 deployment execution checks before broad patient-facing use.
