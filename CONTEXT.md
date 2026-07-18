# Domain Glossary — BaleMed

Ubiquitous language for issues, PRs, code, and agent chats. When a term is defined here, use it consistently.

## People and roles

| Term | Meaning |
| --- | --- |
| **Patient** | Person who sends a message to the Bale bot. Not a clinical record in this MVP. |
| **Pharmacist** | Licensed human who reviews escalated cases. Final judgment stays with the pharmacist. |
| **Pharmacy owner** | Person who approves production changes (real sending, LLM live mode). |
| **Admin** | Operator who receives optional Bale review notifications (`BALE_ADMIN_CHAT_ID`). |

## Messages and workflow

| Term | Meaning |
| --- | --- |
| **Incoming message** | Patient text received via Bale webhook and stored in SQLite (`incoming_messages`). |
| **Safe reply** | Fixed, pharmacist-approved Persian template sent to the patient. Never LLM-generated. |
| **Pharmacist review** | Human review step when a message is marked `needs_review`. |
| **Review reason** | Short internal label explaining why review was requested (keyword, LLM, fail-safe). |
| **Pending review** | Message with review status `pending` — waiting for pharmacist action. |
| **Mark reviewed** | Local-only action that sets status to `reviewed` after pharmacist handling. |

## Safety and routing

| Term | Meaning |
| --- | --- |
| **Escalation** | Route a case to pharmacist review instead of automated clinical handling. |
| **Keyword escalation** | Rule-based `needs_review` from message text (urgent, pregnancy, allergy, etc.). |
| **Fail-safe** | On LLM error or invalid output in live mode, treat as `needs_review`. |
| **Dry-run** | `BALE_ENABLE_SENDING=false` — process webhooks without calling Bale `sendMessage`. |

## Triage disposition (design — D0 / D1 / D2)

Disposition = **next step for the patient**, not diagnosis. See [docs/research/triage-referral-design-fa.md](docs/research/triage-referral-design-fa.md).

| Level | Meaning | Patient reply (template) | Review |
| --- | --- | --- | --- |
| **D0** | Normal intake — general drug question, no red flag | `SAFE_INTAKE_REPLY` | no |
| **D1** | Pharmacist review — allergy, pregnancy, dose, side effect, … | `ESCALATION_REPLY` | yes |
| **D2** | Emergency red flag — chest pain, SOB, overdose, suicide, … | `ER_URGENT_REPLY` (proposed; not in code yet) | yes + emergency |

**Current gap:** D1 and D2 both use `ESCALATION_REPLY` today. D2 needs a separate template emphasizing **115 / ER now**.

## LLM (Milestone 9)

| Term | Meaning |
| --- | --- |
| **Shadow mode** | `BALE_LLM_MODE=shadow` — persist LLM fields only; no change to patient replies or keyword routing. |
| **Live mode** | `BALE_LLM_MODE=live` — LLM `needs_review` unions with keywords; never downgrades keyword hits. |
| **LLM extracted fields** | Structured internal fields (e.g. drug mention, risk flags). Local review only — not in admin Bale notifications. |
| **Shadow batch review** | Owner compares 20–50 `shadow_ok` rows before approving live mode. |

## Technical

| Term | Meaning |
| --- | --- |
| **Webhook secret** | Path segment in `/webhook/bale/{secret}`; not a Bale signature. |
| **Duplicate delivery** | Bale retries the same `update_id` or chat+message_id; stored once, no second reply. |
| **Local-only endpoint** | Routes under `/local/*` — loopback only; blocked at Caddy in production. |

## Related docs

- Safety boundaries: [docs/SAFETY_RULES.md](docs/SAFETY_RULES.md)
- LLM shadow decision: [docs/adr/0001-llm-shadow-mode.md](docs/adr/0001-llm-shadow-mode.md)
- Clinical trust before live: [docs/adr/0002-clinical-trust-requirements-before-live-llm.md](docs/adr/0002-clinical-trust-requirements-before-live-llm.md)
- Triage with LLM: [docs/adr/0003-triage-with-llm.md](docs/adr/0003-triage-with-llm.md)
- Triage without LLM: [docs/adr/0004-triage-without-llm.md](docs/adr/0004-triage-without-llm.md)
- Triage design (Persian reference): [docs/research/triage-referral-design-fa.md](docs/research/triage-referral-design-fa.md)
- Vision and future projects: [docs/VISION-AND-ROADMAP.md](docs/VISION-AND-ROADMAP.md)
- Current milestone: [docs/agents/HANDOFF.md](docs/agents/HANDOFF.md)
