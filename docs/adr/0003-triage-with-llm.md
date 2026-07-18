# ADR-0003: Triage routing with LLM classification layer

**Status:** Accepted (design)  
**Date:** 2026-07-18  
**Milestone:** 9+  
**Related:** [0001-llm-shadow-mode.md](0001-llm-shadow-mode.md), [0004-triage-without-llm.md](0004-triage-without-llm.md)

## Context

BaleMed routes patient messages to pharmacist review using keyword rules today. Milestone 9 adds an optional LLM layer for internal classification and field extraction. The pharmacy owner needs a clear architecture for **triage disposition** (D0 intake / D1 pharmacist / D2 emergency) when LLM is enabled — without letting the LLM diagnose, dose, or replace emergency judgment.

Industry pattern (NHS 111, hybrid GitHub projects): **deterministic rules first**, LLM optional and never downgrading safety hits.

## Decision

### 1. Layer order (always)

```text
incoming message
  → keyword disposition rules (D0 / D1 / D2)
  → optional LLM classify/extract (if BALE_ENABLE_LLM=true)
  → merge_review_metadata (live mode only)
  → fixed patient reply template (never LLM text)
  → admin notify if needs_review
```

### 2. LLM role (allowed)

- Internal only: `needs_review`, `drug_name`, `main_question_topic`, `risk_flags`, `approximate_age_band`
- Shadow mode: persist fields; **do not change** routing or replies
- Live mode: LLM `needs_review` **unions** with keyword hits; keywords cannot be downgraded

### 3. LLM role (prohibited)

- Patient-facing reply text
- Diagnosis, dosage, interaction decisions, medication start/stop/change advice
- Emergency triage as medical authority (validator blocks banned patterns)

### 4. Fail-safe (live mode)

LLM error, timeout, or validator failure → `needs_review=true`, `review_reason=llm_fail_safe`

### 5. Disposition vs review

| Disposition | Patient reply | Internal |
|-------------|---------------|----------|
| D0 | SAFE_INTAKE | no review |
| D1 | ESCALATION (pharmacist) | needs_review |
| D2 | ER_URGENT (proposed — separate template) | needs_review + emergency flag |

D2 red flags evaluated by **rules only**; LLM cannot downgrade D2 to D0.

### 6. Go-live gate

Unchanged from ADR-0001/0002: shadow batch 20–50, owner sign-off, lexicon/intake mitigation before `BALE_LLM_MODE=live`.

## Consequences

- Operators can run LLM in shadow while calibrating disposition rules independently.
- Live mode adds recall (LLM catches cases keywords miss) at cost of more reviews — monitor escalation rate.
- D2 separate template is **design debt** until implemented in `replies.py`.

## Alternatives considered

| Alternative | Rejected because |
|-------------|------------------|
| LLM-only routing | Non-deterministic; Cureus/WHO caution vs rule-based triage |
| LLM generates patient replies | Violates pharmacy safety boundaries |
| LLM can downgrade keyword hits | Safety regression |
| Skip shadow phase | ADR-0001/0002 reject |

## References

- [docs/research/triage-referral-design-fa.md](../research/triage-referral-design-fa.md)
- [docs/research/triage-patterns-adoption-fa.md](../research/triage-patterns-adoption-fa.md)
- [docs/SAFETY_RULES.md](../SAFETY_RULES.md)
- NHS 111 / Pathways (rule-based disposition, not diagnosis)
