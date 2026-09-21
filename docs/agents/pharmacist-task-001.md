# Task PHARM-001 — تصمیم داروساز بعد از پایان سؤالات بیمار

**Status:** open  
**Owner:** داروساز (شما)  
**Labels (when creating in GitHub):** `enhancement`, `ready-for-human`  
**Case شروع:** VPS DB#43 + #44

---

## هدف

از بستر Bale + Notion + مشاوره داخلی ER برای **تصمیم بعد از intake** استفاده کنید — اولین بار روی پرونده atomoxetine / chlordiazepoxide / علامت ادراری.

---

## Checklist

- [ ] **A** — سؤالات تکمیلی را در Bale بفرستید (۴ سؤال در [pharmacist-decision-workflow.md](./pharmacist-decision-workflow.md) §5)
- [ ] **ER** — [er-consult-questions-draft.md](./er-consult-questions-draft.md) را با همسر پر کنید (Notion: Internal → ER consult)
- [ ] **تصمیم** — B (سرپایی) / C (ER) / D (حضور داروخانه)
- [ ] **پاسخ نهایی** — در Bale به بیمار
- [ ] **Shadow** — annotate #43 و #44 روی VPS
- [ ] **Backlog** — ایده‌های §6 را در Notion Product backlog
- [ ] **Policy** — اگر red-flag list از ER آمد → پیش‌نویس به SAFETY_RULES یا ADR

---

## لینک docها

| Doc | نقش |
| --- | --- |
| [pharmacist-decision-workflow.md](./pharmacist-decision-workflow.md) | workflow اصلی |
| [er-consult-questions-draft.md](./er-consult-questions-draft.md) | سؤالات همسر |
| [notion-placement-index.md](./notion-placement-index.md) | کجا در Notion paste شود |

---

## ساخت issue در GitHub (دستی)

```bash
gh issue create --title "Pharmacist task: decision workflow after patient intake ends" \
  --label "enhancement,ready-for-human" \
  --body-file docs/agents/pharmacist-task-001.md
```

---

## Notion task

در **Tasks → Pharmacist (owner)** یک task بسازید:

- Title: `PHARM-001 — تصمیم بعد از intake (case #43+#44)`
- Link: این فایل + Notion ER consult page
