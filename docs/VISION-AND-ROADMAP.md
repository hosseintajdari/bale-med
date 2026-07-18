# Vision and Roadmap — Pharmacy Automation (Border Healthcare)

**Author context:** PharmD, 6 years pharmacist and pharmacy manager, Iran–Pakistan border.  
**Status:** Living document — update when direction changes.  
**Date:** 2026-07-13

---

## North star

Build **safe, practical pharmacy automation** for underserved border communities — where language, culture, drug access, and self-medication are real constraints — without replacing the pharmacist.

Software should:

1. **Collect** structured information.
2. **Route** unclear or high-risk cases to a human.
3. **Never** diagnose, dose, or pretend to know what it does not know.
4. **Document** limits honestly (for patients, for pharmacists, for future employers).

This is health **workflow** technology, not autonomous clinical AI.

---

## Portfolio arc (three projects, one career story)

| Phase | Project | Problem it solves | Status |
| --- | --- | --- | --- |
| **1** | **BaleMed** (this repo) | Safe patient message intake on Bale; pharmacist review; optional LLM hints in shadow | Active — Milestone 9 shadow; P2 owner review |
| **2** | **Medicine price bot** (`Bale-Med-Prices`) | Price, authenticity, drug info, rare drug — Ghaza Daru delivery | **Active** — parallel sprint until 5 Shahrivar 1405 |
| **3** | **Pharmacy management bot/app** (planned) | Inventory, staff workflow, manager ops — from real pharmacy manager experience | Not started — after price bot MVP scope is clear |

**Resume one-liner:**

> Clinical builder for border pharmacy automation: safe patient intake (BaleMed), medicine price access, and pharmacy operations — pharmacist stays accountable.

---

## Principles (do not break)

1. **Pharmacist-in-the-loop** — AI assists; human approves live behavior and clinical judgment.
2. **Shadow before live** — any AI routing change must pass real-message review batch.
3. **Fail-safe escalation** — if unclear, escalate; never silently ignore.
4. **No fake clinical knowledge** — no drug database = no claim of drug verification.
5. **Document non-code gaps** — safety and logic limits belong in GitHub (issues, ADRs), not only in chat.
6. **Regional fit** — Persian/Pashto/Urdu context, border access, mobile-first (Bale).

---

## BaleMed — current phase map

| Milestone | Focus | Gate |
| --- | --- | --- |
| 8 | VPS dry-run deploy | Done (operational) |
| 9 P1 | Shadow LLM on real traffic | Done (`shadow_ok` confirmed) |
| 9 P2 | Owner review 20–50 shadow messages | **Now** — before `BALE_LLM_MODE=live` |
| 9 P3 | Live LLM escalation (optional) | Only after P2 + ADR-0002 requirements met |
| 10+ | Drug lexicon / structured intake | See ADR-0002 |

See [agents/HANDOFF.md](agents/HANDOFF.md) for operational next steps.

---

## Known clinical trust gaps (not “just coding”)

These are **logical** product limits discovered in production shadow testing:

| Gap | Why it matters | Mitigation (planned) |
| --- | --- | --- |
| Misspelled drug names | Wrong or missed drug → unsafe advice path | Persian/Latin fuzzy drug lexicon |
| No patient allergy history | Allergy only if patient writes it | Structured intake; future pharmacy system link |
| LLM over-escalation | Pharmacist reviews everything → burnout | Tune thresholds; live only after batch review |
| Generic LLM ≠ formulary | Model guesses; no verified Iran/Pakistan formulary | Rules + lexicon over bigger model |
| Border language mix | Code-switching, typos, local names | Region-specific training data / glossary |

Full decision record: [adr/0002-clinical-trust-requirements-before-live-llm.md](adr/0002-clinical-trust-requirements-before-live-llm.md).

---

## Medicine price bot (draft scope)

**User problem:** “How much is X? Is it available?” — daily border pharmacy question.

**In scope (draft):**

- Search by drug name (with fuzzy match).
- Show last-known price band or “ask pharmacist” — no guaranteed live ERP sync in MVP.
- Clear disclaimer: prices change; confirm in pharmacy.

**Out of scope:**

- Clinical advice.
- Replacing pharmacist consultation on *whether* to take a drug.

**Reuse from BaleMed:** safety reply style, deploy patterns, SQLite audit, GitHub workflow.

---

## Pharmacy management bot/app (draft scope)

**User problem:** Manager workflow — stock alerts, shift handoff, simple reports.

**In scope (draft):**

- Low-stock reminders.
- Daily summary for manager (counts, pending patient messages from BaleMed).
- Staff checklist (open/close pharmacy).

**Out of scope:**

- Full ERP replacement in v1.
- Autonomous purchasing decisions.

**Reuse from BaleMed:** auth/secrets discipline, VPS deploy, documentation habits.

---

## Career alignment (health tech, not only pharmacy)

This repository is **portfolio evidence**, not only a local tool.

What it proves to employers:

- Clinical workflow understanding from 6 years floor + manager work.
- Ability to ship (code, VPS, tests, CI).
- Safety literacy: shadow mode, fail-safe, documented limits.
- Honesty about AI — rare and valuable in health tech hiring.

Short narrative for LinkedIn / resume: [CAREER-NARRATIVE.md](CAREER-NARRATIVE.md).

---

## How to use this doc

1. Before a new feature — check **Principles** and **Known gaps**.
2. Before `BALE_LLM_MODE=live` — complete P2 + read ADR-0002.
3. Before starting project 2 or 3 — add a row to the portfolio table and link a new repo or monorepo plan.
4. When you learn something important — update this file or add an ADR (same PR or follow-up).

---

## Related docs

| Doc | Purpose |
| --- | --- |
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | Milestone tasks |
| [SAFETY_RULES.md](SAFETY_RULES.md) | Hard safety boundaries |
| [CONTEXT.md](../CONTEXT.md) | Domain glossary |
| [CAREER-NARRATIVE.md](CAREER-NARRATIVE.md) | Resume / portfolio wording |
| [adr/](adr/) | Architecture and safety decisions |
