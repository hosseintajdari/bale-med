# Embednet OS — راهنمای ساختار Notion

Embednet OS ورک‌اسپیس Notion برای مدیریت پروژه‌ها، اسناد، و یادگیری روزانه است.

## Hub

**Workspace:** Work (Notion app)

[Embednet OS](https://app.notion.com/p/3a0f6d55a67381d89970e238979f201b) — `3a0f6d55a67381d89970e238979f201b`

> اگر Embednet OS duplicate روی اکانت دیگر ساخته شده، فقط همین hub در workspace **Work** canonical است. duplicate را در اکانت دیگر archive کن.

## Sidebar — ۸ بخش

| # | Section | Purpose | Link |
|---|---------|---------|------|
| 1 | Docs | PRD، Spec، ADR — با tag و link به milestone | [Docs](https://app.notion.com/p/3a0f6d55a673810fbe42e6cd0b350206) |
| 2 | Product | Projects، Goals، Milestones | [Product](https://app.notion.com/p/3a0f6d55a673816eb3abf1e063aa2e39) |
| 3 | Alignment & Schedule | Timeline، Critical Path، Weekly Review | [Alignment](https://app.notion.com/p/3a0f6d55a67381fd9c58d228fe5bdde7) |
| 4 | Metrics | KPIs — shadow review، deploy health | [Metrics](https://app.notion.com/p/3a0f6d55a67381f7a425eb635719e1b4) |
| 5 | Releases | Ship log — چه چیزی کی deploy شد | [Releases](https://app.notion.com/p/3a0f6d55a673815d96fffc7956ec087d) |
| 6 | Knowledge Hub | Glossary، decisions، یادگیری روزانه | [Knowledge Hub](https://app.notion.com/p/3a0f6d55a67381ca8421fc4fa9a81b42) |
| 7 | Brainstorm | Ideas قبل از PRD | [Brainstorm](https://app.notion.com/p/3a0f6d55a67381349e5df85e8ad18bd5) |
| 8 | کارهای بعدی | کارهای روزانه و فوری — هر کار به پروژه وصل است | [کارهای بعدی](https://app.notion.com/p/3a0f6d55a67381a9bb71f19ceb293654) |

## Alignment chain

```text
Goal → Project → Milestone → PRD/Spec (در Docs)
```

هر کار باید به یک Project وصل باشد تا پراکنده نشود.

## Databases

| Database | ID | Parent |
|----------|----|--------|
| Docs (PRD/Spec/ADR) | `7576cf0b-1c48-47fd-a5c8-be0bf7165012` | Docs |
| Projects | — | Product |
| Goals | — | Product |
| Milestones & Tasks | `3ebe878d-8a69-488b-aa5a-04ede71d3d78` | Product |
| KPIs | `a3569b7f-1c09-4127-b7aa-309a73219068` | Metrics |
| Ship Log | `8334d9b2-f93c-4bfd-909c-a40775efff8f` | Releases |
| Knowledge | `bde89f17-aae0-48f7-b111-b3494323cd91` | Knowledge Hub |
| Knowledge (data source) | `642560ff-653b-4ea0-9983-0dd26efea3e8` | collection:// |
| یادگیری روزانه (Daily Learning Log) | `a3d4f11a-b597-4e46-80ee-2f0d32dec714` | Knowledge Hub |
| واژه‌نامه برنامه‌نویسی (Dev Vocabulary) | `342d997f-ca98-4776-a8f0-323eec4ea32a` | Knowledge Hub |
| Ideas | — | Brainstorm |
| کارهای بعدی | `8a7af24a1e884b328143ea4d7cc7db71` | Section page (کارهای بعدی) |
| کارهای بعدی (data source) | `50ff599b-53a2-4a54-87e1-695c639031a9` | collection:// |

## کارهای بعدی — فارسی

Database برای کارهای روزانه و فوری.

**Properties:**
- `عنوان` — نام کار
- `اولویت` — P0، P1، P2، P3
- `دسته‌بندی` — نوع کار
- `وضعیت` — شروع نشده، در حال انجام، انجام شد
- `تاریخ` — Due date
- `پروژه` — Relation به Projects

**Views:**
- `امروز` — filter: تاریخ = today، sort: اولویت
- `بر اساس اولویت` — sort by اولویت
- `بورد وضعیت` — board by وضعیت

**Hub linked views:**
- `کارهای بعدی امروز` — P0/P1 filter
- `آخرین یادگیری` — sort by تاریخ descending

## واژه‌نامه برنامه‌نویسی — vibe-coder

رفرنس اصطلاحات انگلیسی فنی برای vibe-coder — جدا از Glossary دامنه (Knowledge).

**Hub page:** [واژه‌نامه vibe-coder](https://app.notion.com/p/3a1f6d55a67381788defe158055d19b2)

**Data source:** `7c365df6-c1d3-4332-b706-6c2603b4e556`

**فرمت هر کارت:** `اصطلاح` → `معادل_فارسی` → `توضیح_کوتاه` → `مثال`

**Properties:**
- `اصطلاح` (title)، `معادل_فارسی`، `توضیح_کوتاه`، `مثال`
- `دسته` — Git، FastAPI، Deploy، Notion، Cursor، Python، General
- `سطح` — جدید / در حال یادگیری / یاد گرفتم
- `وضعیت_مرور` — نیاز به مرور / مرور شد
- `تاریخ_آخرین_مرور`
- `یادگیری_روزانه` (relation → Daily Learning)
- `مرجع_دانش` (relation → Knowledge)
- `Project` (relation → Projects)

**Views:** همه، نیاز به مرور، بر اساس دسته، تازه‌ها، کارت مطالعه

**Workflow ثبت:** در Cursor بگو `/notion-os — واژه webhook را ثبت کن`

## Knowledge — Reference entries

| Entry | Repo source | Notion import |
|-------|-------------|---------------|
| طراحی تریاژ و ارجاع — BaleMed (با/بدون LLM) | [`docs/research/triage-referral-design-fa.md`](../research/triage-referral-design-fa.md) | [`docs/notion-import/README.md`](../notion-import/README.md) |

**Properties (Reference):** Category=Reference, Project=BaleMed, Tags=BaleMed/Pharmacy/Safety/LLM, Status=Draft→Stable

**Relations:** واژه_های_فنی → ADR (فنی), workflow, schema

**Publish script:** `python3 scripts/publish-triage-notion.py` (needs `NOTION_TOKEN`)

**ADR repo:** [`0003-triage-with-llm.md`](../adr/0003-triage-with-llm.md), [`0004-triage-without-llm.md`](../adr/0004-triage-without-llm.md)

## یادگیری روزانه — properties

- `عنوان`، `تاریخ`، `وضعیت` (پیش‌نویس / آماده / بررسی شد)
- `موضوعات`، `صفحات`، `نقاط_کور`، `Project`
- `واژه_های_روز` (relation → واژه‌نامه برنامه‌نویسی)

## یادگیری روزانه — فلو

```text
صبح: کارهای بعدی (P0/P1)
  ↓
کار در Cursor
  ↓
hook captures signals → .cursor/learning-queue/
  ↓
21:00 automation → صفحه یادگیری در Notion
```

**Automation:** [`docs/agents/daily-vibe-learning-automation.yaml`](daily-vibe-learning-automation.yaml)

**Script:** [`deploy/scripts/daily-learning-digest.py`](../../deploy/scripts/daily-learning-digest.py)

**راهنما:** [`docs/agents/DAILY-LEARNING-AUTOMATION.md`](DAILY-LEARNING-AUTOMATION.md)

## قوانین زبان

- **کارهای بعدی**: فارسی کامل
- **یادگیری روزانه**: فارسی ساده؛ نام ابزار (Notion، FastAPI، Cursor) انگلیسی OK
- **بقیه sections**: انگلیسی یا mix قابل قبول

## امنیت

هیچ secret، token، یا داده بیمار به Notion نرود. مطابق با `docs/SAFETY_RULES.md`.

---

Last updated: 2026-07-18 (واژه‌نامه برنامه‌نویسی — Dev Vocabulary DB + hub page)
