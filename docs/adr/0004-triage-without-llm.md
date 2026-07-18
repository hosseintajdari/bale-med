# ADR-0004: Triage routing without LLM (rules-only)

**Status:** Accepted (design)  
**Date:** 2026-07-18  
**Milestone:** 9+  
**Related:** [0003-triage-with-llm.md](0003-triage-with-llm.md)

## Context

BaleMed must remain safe and auditable when `BALE_ENABLE_LLM=false` or when the LLM layer is removed entirely. This is the **baseline production path** for many pharmacies and matches industry best practice: deterministic triage before any AI layer.

## Decision

### 1. Routing engine

100% rule-based:

```text
incoming message
  → keyword disposition (D0 / D1 / D2)
  → (future) structured intake step machine
  → fixed patient reply by disposition
  → admin notify if D1 or D2
```

Implementation today: [`app/replies.py`](../../app/replies.py) `needs_pharmacist_review()` + `build_safe_reply()`.

### 2. Three disposition levels

| Level | Trigger (examples) | Patient reply | Review |
|-------|-------------------|---------------|--------|
| D0 | General drug question, greeting | SAFE_INTAKE | no |
| D1 | allergy, pregnancy, pediatric, dose, side effect | ESCALATION | yes |
| D2 | chest pain, SOB, overdose, suicide, severe allergy | ER_URGENT (proposed) | yes + emergency |

### 3. Patient replies

- **Never** LLM-generated
- Pharmacist-approved Persian templates only
- D2 must emphasize **115 / ER now** — not only "wait for pharmacist"

### 4. Audit

- `review_reason=pharmacist_review_required` for keyword hits
- Deterministic: same input → same disposition (reproducible for owner review)

### 5. When LLM is added later

ADR-0003 applies on top — rules remain authoritative; LLM unions in live mode only.

## Consequences

- Simplest path for MVP and regulatory narrative ("bot follows fixed rules").
- Keyword list maintenance is owner/pharmacist responsibility — document in HANDOFF taxonomy.
- Gap: D1 and D2 share one template today — implement ER_URGENT_REPLY in a future code milestone.

## Alternatives considered

| Alternative | Rejected because |
|-------------|------------------|
| No keyword list (human reviews all) | Does not scale; defeats automation |
| LLM replaces keywords when enabled | Removes deterministic safety net |
| Single reply for all escalations | Under-emphasizes emergency (D2) |

## References

- [docs/research/triage-referral-design-fa.md](../research/triage-referral-design-fa.md)
- [GitHub: ai-healthcare-assistant](https://github.com/sadiqueamin-1999/ai-healthcare-assistant) — rule engine + optional LLM language layer
