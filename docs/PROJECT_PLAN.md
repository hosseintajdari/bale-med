# Project Plan

## Current Status
The project has a minimal FastAPI webhook app, SQLite message storage, a cautious Bale API client, and dry-run reply behavior. Local `.env` loading and basic regression tests are now in place so development can continue with less manual setup.

## Long-Term Product Vision
Build a safe pharmacy automation assistant for Bale that supports a real pharmacy workflow from first contact through pharmacist review. The assistant should receive messages, collect structured intake information, avoid clinical decision-making, preserve auditability, and route cases to a pharmacist when judgment is needed.

Later milestones may add basic bot commands, safer reply layers, admin review tools, VPS deployment, and LLM/AI integration. AI must be introduced only inside pharmacist-approved boundaries and must not diagnose, prescribe, replace a pharmacist, or recommend medication changes.

The vision and milestone order are living project guidance. They may change as requirements, pharmacy workflow details, or Bale API constraints become clearer. Update this plan before making implementation changes that alter the project direction.

## Milestone Map
1. Milestone 1: Done - Project skeleton and local foundation.
2. Milestone 2: Done - Real Bale webhook on local laptop with tunnel and real reply.
3. Milestone 3: Done - Secure webhook with secret path.
4. Milestone 4: Done - Basic bot commands.
5. Milestone 5: Safe pharmacy reply layer.
6. Milestone 6: Better logging and admin review.
7. Milestone 7: VPS deployment preparation.
8. Milestone 8: Real VPS deployment.
9. Milestone 9: LLM/AI integration.

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

## Milestone 4: Basic Bot Commands
Add simple command replies for `/start`, `/help`, and `/status`. These replies are intentionally non-medical: they introduce the bot as a pharmacy message intake assistant, list available commands, and confirm the service is running. Unknown text keeps the configured safe acknowledgement behavior.

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
