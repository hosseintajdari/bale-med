# Notion placement index — BaleMed pharmacist workflow

**Date:** 2026-07-17  
**Purpose:** Where to paste each block in EmbedNet OS / BaleMed Notion.  
**Repo source files:** links below — copy sections or import `.md` into Notion.

---

## Quick map

| Notion home / page | What goes there | Repo file |
| --- | --- | --- |
| **BaleMed → Clinical workflow → Chat intake** | فیلدهای لازم در چت، مرز ربات vs داروساز | [pharmacist-decision-workflow.md](./pharmacist-decision-workflow.md) §1–2 |
| **BaleMed → Clinical workflow → After intake (داروساز)** | سناریوهای A–E، نقطه تصمیم، پاسخ‌های نمونه | [pharmacist-decision-workflow.md](./pharmacist-decision-workflow.md) §3–5 |
| **BaleMed → Internal → ER consult (همسر)** | درفت سؤالات برای پزشک ER | [er-consult-questions-draft.md](./er-consult-questions-draft.md) |
| **BaleMed → Product backlog** | شاخه‌های جدا (conversation linking، referral tier، …) | [pharmacist-decision-workflow.md](./pharmacist-decision-workflow.md) §6 |
| **BaleMed → Shadow review / P2** | annotation نمونه پرونده atomoxetine | [pharmacist-decision-workflow.md](./pharmacist-decision-workflow.md) §7 |
| **Tasks → Pharmacist (owner)** | تسک فعال: تصمیم بعد از پایان سؤالات بیمار | GitHub issue (see below) |
| **Metrics / P2 gate** | +2 shadow rows reviewed (#43, #44) | HANDOFF table update after annotation |

---

## How to paste into Notion

1. Open the Notion page from the table above.
2. `/markdown` or paste from repo file section.
3. For **Tasks**: create a Notion task linked to GitHub issue URL.
4. Tag pages: `BaleMed`, `Milestone-9`, `Clinical-workflow`, `P2-shadow`.

---

## GitHub task (mirror in Notion Tasks)

Create or link issue:

```text
Title: Pharmacist decision workflow — after patient intake ends
Labels: enhancement, ready-for-human
Body: see docs/agents/pharmacist-decision-workflow.md + er-consult-questions-draft.md
```

Issue number: _fill after `gh issue create`_

---

## Related repo docs

| Doc | Role |
| --- | --- |
| [HANDOFF.md](./HANDOFF.md) | P2 shadow state |
| [SAFETY_RULES.md](../SAFETY_RULES.md) | Boundaries |
| [adr/0002-clinical-trust-requirements-before-live-llm.md](../adr/0002-clinical-trust-requirements-before-live-llm.md) | Live LLM gates |
