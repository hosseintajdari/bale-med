# Notion import — Triage reference (Knowledge → Reference)

Cloud agents may not have Notion MCP. Use one of these paths after merging the repo docs.

## Target

| Field | Value |
|-------|-------|
| Database | **Knowledge** (`bde89f17-aae0-48f7-b111-b3494323cd91`) |
| Data source (API) | `642560ff-653b-4ea0-9983-0dd26efea3e8` |
| Category | Reference |
| Status | Draft (→ Stable after owner review) |
| Project | BaleMed |
| Tags | BaleMed, Pharmacy, Safety, LLM |

**Title:** `طراحی تریاژ و ارجاع — بات داروخانه BaleMed (با/بدون LLM)`

**Notion page:** [https://app.notion.com/p/3a1f6d55a673815aba45fc8e3fb9713d](https://app.notion.com/p/3a1f6d55a673815aba45fc8e3fb9713d)

**Summary:** مرجع طراحی تریاژ D0/D1/D2 برای بات BaleMed: ارجاع داروساز، red flags اورژانس، و دو مسیر ADR فنی با/بدون LLM.

## Option A — Script (recommended)

```bash
export NOTION_TOKEN=secret_...
python3 scripts/publish-triage-notion.py --dry-run
python3 scripts/publish-triage-notion.py
```

Then in Notion UI:

1. Set **Project** → BaleMed
2. Relate **واژه_های_فنی** → ADR (فنی), workflow, schema
3. Add one line on [Knowledge Hub](https://app.notion.com/p/3a0f6d55a67381ca8421fc4fa9a81b42) linking the new page

## Option B — Manual paste

1. Open Knowledge database → New → Reference
2. Set properties above
3. Paste body from [`docs/research/triage-referral-design-fa.md`](../research/triage-referral-design-fa.md)
4. Re-add mermaid diagrams via Notion `/code` or screenshot from repo preview

## Option C — Cursor with Notion MCP (Windows desktop)

> **Done (2026-07-18):** Option C completed 2026-07-18 — page created via Notion MCP. Page: [https://app.notion.com/p/3a1f6d55a673815aba45fc8e3fb9713d](https://app.notion.com/p/3a1f6d55a673815aba45fc8e3fb9713d)


```
/notion-os — صفحه Reference در Knowledge بساز:
عنوان: طراحی تریاژ و ارجاع — بات داروخانه BaleMed (با/بدون LLM)
Category: Reference, Project: BaleMed, Tags: BaleMed Pharmacy Safety LLM
محتوا از docs/research/triage-referral-design-fa.md
relation واژه_های_فنی: ADR, workflow, schema
```

## Repo links to cite in Notion

- [`docs/research/triage-referral-design-fa.md`](../research/triage-referral-design-fa.md)
- [`docs/adr/0003-triage-with-llm.md`](../adr/0003-triage-with-llm.md)
- [`docs/adr/0004-triage-without-llm.md`](../adr/0004-triage-without-llm.md)
- [`CONTEXT.md`](../../CONTEXT.md) — D0/D1/D2 glossary
