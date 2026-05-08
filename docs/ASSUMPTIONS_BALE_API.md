# Bale API Assumptions Register

This file is the canonical list of Bale API assumptions used by the MVP. Do not enable real outbound messaging until assumptions are verified against official Bale Bot API documentation.

## Current Code Assumptions
1. Incoming webhook may include top-level `message` object.
2. Incoming webhook may include top-level `update_id`.
3. Incoming chat id may be at `message.chat.id`.
4. Incoming message id may be at `message.message_id`.
5. Incoming text may be at `message.text`.
6. Bale base URL format is `https://tapi.bale.ai/bot<token>/METHOD_NAME`.
7. Requests use `POST` with `application/json`.
8. `sendMessage` currently uses `chat_id`, `text`, and optional `reply_to_message_id`.
9. Optional admin review notifications use the same unverified `sendMessage` assumptions when enabled.

## Current MVP Duplicate-Delivery Behavior
1. If top-level `update_id` is present, the app stores `update:<update_id>` as its internal duplicate guard key.
2. If `update_id` is not present but both `message.chat.id` and `message.message_id` are present, the app stores `message:<chat_id>:<message_id>` as its internal duplicate guard key.
3. If no stable key can be derived, the app still stores the message. It does not drop uncertain messages.
4. When a duplicate key is recognized, the app returns the existing stored row id and does not insert a second row or prepare another reply.

## Not Yet Verified with Official Bale Documentation
- Exact incoming webhook payload schema and required fields.
- Whether top-level `update_id` exists in Bale webhook payloads.
- Whether `message.message_id` is globally unique or only unique inside a chat.
- Bale retry behavior and duplicate delivery expectations.
- Webhook authentication/signature mechanism beyond the current secret path.
- Bale response schema, error codes, rate limits, and retry guidance for API methods.
- Whether using `sendMessage` for admin review notifications needs any different constraints from normal user replies.

## Verification Checklist
1. Confirm exact incoming webhook payload schema and required fields.
2. Confirm update id/event id field for idempotency handling.
3. Confirm sender/user identifiers and chat identifiers.
4. Confirm response schema and error codes for all methods used.
5. Confirm auth mechanism and any required headers beyond token-in-path.
6. Confirm rate limits and retry guidance.
7. Confirm optional fields and constraints for `setWebhook` and `getWebhookInfo`.
8. Confirm that admin review notifications can safely use the same `sendMessage` contract.

## Blocking Items Before Public Deployment
- Unknown webhook authentication/signature validation method.
- Unknown retry policy and duplicate update handling expectations.

## Documentation Sync Rule
When an assumption is verified or changed:
1. Update this file first.
2. Update related code TODO comments.
3. Update `README.md` and `docs/PROJECT_PLAN.md` if behavior or operations changed.
