# Bale API Assumptions Register

This file is the canonical list of Bale API assumptions used by the MVP. Do not enable real outbound messaging until assumptions are verified against official Bale Bot API documentation.

## Current Assumptions in Code
1. Incoming webhook may include top-level `message` object.
2. Incoming chat id may be at `message.chat.id`.
3. Incoming message id may be at `message.message_id`.
4. Incoming text may be at `message.text`.
5. Bale base URL format is `https://tapi.bale.ai/bot<token>/METHOD_NAME`.
6. Requests use `POST` with `application/json`.
7. `sendMessage` currently uses `chat_id`, `text`, and optional `reply_to_message_id`.

## Verification Checklist
1. Confirm exact incoming webhook payload schema and required fields.
2. Confirm update id/event id field for idempotency handling.
3. Confirm sender/user identifiers and chat identifiers.
4. Confirm response schema and error codes for all methods used.
5. Confirm auth mechanism and any required headers beyond token-in-path.
6. Confirm rate limits and retry guidance.
7. Confirm optional fields and constraints for `setWebhook` and `getWebhookInfo`.

## Blocking Items Before Public Deployment
- Unknown webhook authentication/signature validation method.
- Unknown retry policy and duplicate update handling expectations.

## Documentation Sync Rule
When an assumption is verified or changed:
1. Update this file first.
2. Update related code TODO comments.
3. Update `README.md` and `docs/PROJECT_PLAN.md` if behavior or operations changed.
