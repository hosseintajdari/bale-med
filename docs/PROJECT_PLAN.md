# Project Plan

## Current Status
The project has a minimal FastAPI webhook app, SQLite message storage, a cautious Bale API client, and dry-run reply behavior. Local `.env` loading and basic regression tests are now in place so development can continue with less manual setup.

## Milestone 1: Local Webhook Skeleton
Build a small FastAPI service that can receive Bale webhook updates, store the raw incoming message data in SQLite, and prepare a safe reply path without sending medical advice.

## MVP Scope
- Provide `GET /health` for service checks.
- Provide `POST /webhook/bale` for incoming Bale updates.
- Store every incoming webhook payload for auditability.
- Extract optional message fields only when they are present.
- Keep outbound Bale replies as a placeholder until the exact Bale Bot API documentation is checked.

## Out of Scope for Milestone 1
- Diagnosis, prescription changes, dosage recommendations, or clinical decision-making.
- User authentication, admin dashboards, or production deployment automation.
- Complex conversation state machines.

## Known Assumptions and Open Questions
- Webhook payload shape is treated as Telegram-like for now (`message`, `message.chat.id`, `message.message_id`, `message.text`).
- Bale send-message endpoint, method, headers, and payload contract are unknown and must be confirmed.
- Webhook authentication/signature mechanism is unknown and must be confirmed before public deployment.
- Canonical tracker: `docs/ASSUMPTIONS_BALE_API.md`.

## Readiness Gates Before Enabling Real Use
1. Confirm Bale webhook schema with official documentation and update code/docs accordingly.
2. Confirm Bale outbound send-message contract and test in a non-production environment.
3. Select and document webhook authentication strategy.
4. Validate VPS runbook end-to-end, including restart and log inspection.
5. Review SQLite storage path, backup, and retention strategy for operational safety.
6. Keep `BALE_ENABLE_SENDING=false` until the exact Bale behavior is confirmed.

## Next Milestones
1. Confirm exact Bale Bot API webhook and send-message fields.
2. Add webhook authentication or a secret path/token before public exposure.
3. Add pharmacist handoff workflow and structured intake questions.
4. Add patient-safe conversation state for intake only, not medical advice.
5. Add privacy-minded logging and retention rules for stored messages.
