# ADR-0001: LLM shadow mode before live escalation

**Status:** Accepted  
**Date:** 2026-07-13  
**Milestone:** 9

## Context

Milestone 9 adds an optional LLM classification layer. The pharmacy bot must never send LLM-generated text to patients or replace pharmacist judgment. We need a safe way to test LLM extraction on real traffic before it can change review routing.

## Decision

1. **Default off:** `BALE_ENABLE_LLM=false` until explicitly enabled on the server.
2. **Shadow first:** New deployments use `BALE_LLM_MODE=shadow`. Shadow mode persists LLM audit and extracted fields on `incoming_messages` but does not change patient replies or downgrade keyword escalation.
3. **Live is gated:** `BALE_LLM_MODE=live` requires pharmacy owner approval and manual review of 20–50 shadow messages (`deploy/scripts/list-shadow-reviews.py`).
4. **Union, not override:** In live mode, LLM `needs_review` unions with keyword hits. Keywords cannot be downgraded by the LLM.
5. **Fail-safe:** LLM errors, timeouts, and validator failures in live mode escalate to pharmacist review.
6. **No patient LLM text:** The LLM never produces outbound Bale messages.

## Consequences

- Operators can compare `llm_extracted` vs pharmacist judgment without patient impact.
- `/local/reviews/pending` may stay empty in shadow mode when only LLM flags review — use shadow listing scripts on VPS.
- External LLM APIs receive minimized, redacted snippets only; full prompts/responses are not stored.
- Admin Bale notifications must not include LLM extracted fields.

## Alternatives considered

- **Live from day one:** Rejected — too risky without real-message calibration.
- **LLM-only routing (no keywords):** Rejected — keywords provide deterministic safety net.
- **Patient-facing LLM replies:** Rejected — violates pharmacy safety boundaries.
