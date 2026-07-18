# اتوماسیون یادگیری روزانه vibe-coder

کار امروز در Cursor را به یک **صفحه ۳–۴ بخشی** در Notion تبدیل کن — با نقاط کور، لینک و ویدیو.

## Pipeline

```text
Cursor chat/session
  -> hook captures signals (.cursor/learning-queue/YYYY-MM-DD.jsonl)
  -> daily-learning-digest.py builds JSON/markdown
  -> Cursor Automation (21:00) creates Notion page in یادگیری روزانه
```

## Local commands

```powershell
cd C:\Users\hosse\OneDrive\Documents\BaleMed
python deploy/scripts/daily-learning-digest.py --date today --json
python deploy/scripts/daily-learning-digest.py --date today --markdown
```

## Cursor hook (already wired)

File: `.cursor/hooks.json`

- Runs on `stop` and `sessionEnd`
- Script: `.cursor/hooks/capture-learning-signal.py`
- Output: `.cursor/learning-queue/` (local only, gitignored)

Reload Cursor after first setup. Check **Settings → Hooks** if signals do not appear.

## Cursor Automation (daily)

Open **Cursor → Automations → New** and import or paste from:

`docs/agents/daily-vibe-learning-automation.yaml`

| Field | Value |
| --- | --- |
| Name | یادگیری روزانه vibe-coder |
| Trigger | Every day at **21:00** (Asia/Tehran) |
| Repo | `hosseintajdari/bale-med` |
| Tools | Shell, Notion MCP |
| Memory | On |

### Agent instructions (paste into automation)

```text
یک صفحه در database «یادگیری روزانه» در Embednet OS > Knowledge Hub بساز.

۱. اجرا کن: python deploy/scripts/daily-learning-digest.py --date today --json
۲. اگر has_activity برابر false بود، یک صفحه مرور کوتاه (یک موضوع از هفته قبل) بساز.
۳. یک صفحه در database «یادگیری روزانه» بساز با ۴–۵ بخش:
   - امروز چه کار کردیم
   - نقاط کور (چرا مهم است + یک خط توضیح)
   - نکات آموزشی گام‌به‌گام
   - لینک و ویدیو از digest JSON
   - **اصطلاحات امروز** (اگر `english_learning` در blind_spots یا `vocabulary_hints` در JSON)
۴. برای هر واژه در `vocabulary_hints`: جستجو در database «واژه‌نامه برنامه‌نویسی»؛ اگر بود relation بزن؛ اگر نبود پیشنهاد ثبت بده (بدون auto-create)
۵. Properties: عنوان=یادگیری روزانه — [تاریخ]، تاریخ=امروز، وضعیت=آماده، موضوعات از blind_spots، صفحات=۳ یا ۴
۶. اگر کار repo BaleMed بود Project=BaleMed ست کن.

زبان: فارسی ساده. نام ابزار (Notion، FastAPI، Cursor) انگلیسی OK.
هیچ secret، token، یا داده بیماری نگذار.
```

## Notion target

- Workspace hub: [Embednet OS](https://app.notion.com/p/3a0f6d55a67381d89970e238979f201b)
- Section: **Knowledge Hub → یادگیری روزانه** (Daily Learning Log)
- Vocabulary: **Knowledge Hub → [واژه‌نامه vibe-coder](https://app.notion.com/p/3a1f6d55a67381788defe158055d19b2)** (database ID `342d997f-ca98-4776-a8f0-323eec4ea32a`)

## ثبت واژه دستی (هر زمان)

```text
/notion-os — واژه webhook را ثبت کن:
معادل: وب‌هوک
توضیح: URL که Bale وقتی پیام آمد POST می‌زند
مثال: POST /webhook/bale/{secret}
```

## مرور هفتگی

```text
۵ واژه از view «نیاز به مرور» در واژه‌نامه را مرور کن و وضعیت_مرور را به‌روز کن
```

## Manual fallback (no automation yet)

1. Run digest script
2. Ask Agent: *Read digest JSON and create today's Daily Learning page in Notion*

## Sample page

First page created: [یادگیری روزانه — 2026-07-17](https://app.notion.com/p/3a0f6d55a6738137b513d611ca9dac8c)
