# ADR-0002: Clinical trust requirements before live LLM escalation

**Status:** Accepted  
**Date:** 2026-07-13  
**Author context:** Owner review after Milestone 9 shadow testing (P1 complete, P2 in progress)

## Context

Shadow LLM on real Bale traffic works technically (`shadow_ok`). Owner testing showed:

- Nonsense or typo messages may get `needs_review: true` with empty extracted fields — **safe but noisy**.
- Misspelled drug names (e.g. garbled ibuprofen) are **not reliably** resolved — there is no drug lexicon.
- Allergy and risk flags depend on **what the patient types**, not pharmacy records or EHR.
- A frontier LLM alone does not fix these; they are **data and workflow** problems.

Owner goal: health technology career portfolio with **honest safety engineering**, not “AI replaces pharmacist.”

## Decision

### 1. Do not enable `BALE_LLM_MODE=live` until ALL of:

1. **P2 shadow batch review** — owner reviews 20–50 `shadow_ok` rows; documents false positives/negatives.
2. **Escalation rate acceptable** — live mode must not route every message to pharmacist review (burnout risk).
3. **At least one mitigation for drug-name ambiguity** is implemented OR explicitly accepted as known risk:
   - **Preferred:** Persian/Latin fuzzy drug lexicon (common border drugs + typos), OR
   - **Minimum:** structured intake flow that asks patient to confirm drug name before escalation logic uses LLM `drug_name`.

### 2. Bigger model is not a substitute

Upgrading to a newer general model (e.g. newer GPT/Claude class) is **optional tuning**, not a gate for live mode. Gates are:

- Lexicon / structured intake
- Shadow metrics
- Pharmacist owner sign-off

### 3. Document non-code gaps on GitHub

Clinical and logical limits must be tracked as:

- ADRs (this file)
- GitHub issues with label `safety` or `domain-gap` (see issue template)
- Updates to [VISION-AND-ROADMAP.md](../VISION-AND-ROADMAP.md)

“Design problem” and “logic problem” are **first-class** for this project.

### 4. Patient-facing behavior unchanged

Live LLM may only affect **internal routing** (`needs_review`, review_reason). Patient replies remain fixed templates — never LLM-generated.

## Consequences

- Live mode may stay off for months while lexicon/intake is built — **acceptable**.
- Resume/portfolio value increases from documented judgment, not from flipping `live` early.
- Future projects (price bot, pharmacy management) reuse the same trust principles.

## Alternatives considered

| Alternative | Rejected because |
| --- | --- |
| Go live now with DeepSeek only | Typos and false escalation rate unknown; no drug ground truth |
| Wait for GPT-5 / Claude “frontier” | General intelligence ≠ verified formulary; cost and Iran access vary |
| Pharmacist reviews every message manually | Does not scale; defeats automation purpose |
| Remove LLM entirely | Loses useful hints for triage after trust layer is added |

## Follow-up issues (create when ready)

- `feat: Persian drug name lexicon with fuzzy match`
- `feat: structured intake — confirm drug name step`
- `docs: P2 shadow review outcome log` (anonymized examples)
