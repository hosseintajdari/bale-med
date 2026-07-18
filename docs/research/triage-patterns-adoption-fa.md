# الگوهای جهانی — چه برداریم و چه نه

**تاریخ:** 2026-07-18  
**مرتبط:** [triage-referral-design-fa.md](triage-referral-design-fa.md) · [Notion Reference](https://app.notion.com/p/3a1f6d55a673815aba45fc8e3fb9713d)

---

## اصل مهم (داروخانه ≠ برنامه‌نویسی)

مسیرهایی که **استاندارد جهانی** یا **دستورالعمل بالینی** دارند را دوباره طراحی نکن.  
در پزشکی باید همان الگو را **پیاده** کنی — نه جایگزین خلاقانه.

---

## تأیید: تا اینجا درست آمده‌ایم

| استاندارد | BaleMed امروز |
|-----------|---------------|
| تریاژ = disposition، نه تشخیص | ✅ |
| پاسخ بیمار = template ثابت | ✅ |
| قواعد deterministic اول | ✅ |
| LLM فقط داخلی + shadow | ✅ |
| gate انسانی قبل live | ✅ P2 |
| fail-safe | ✅ |

**خارج از استاندارد جهانی عمل نکرده‌ایم.** گپ‌ها = تکمیل همان الگوها، نه معماری جدید.

---

## هر منبع — روش کوتاه

| منبع | روش (۲–۳ جمله) |
|------|----------------|
| **NHS 111 / Pathways** | سوال‌های rule-based؛ خروجی فقط «قدم بعدی» (self-care، GP، ER). Class 1 medical device — **بدون تشخیص**. |
| **Infermedica** | API با ۵ سطح disposition از self-care تا آمبولانس. الگوی صنعتی «الان چه کار کند؟». |
| **WHO LMM 2024** | human-in-the-loop، audit، LLM جایگزین متخصص نیست. |
| **Cureus 2024** | LLM عمومی برای تریاژ پایدارتر از NHS rule-based نیست. |
| **CAIDRA / chatbot دارویی** | عوارض دارو → فرآیند PV، نه فقط جواب متنی. |
| **ai-healthcare-assistant** | rule engine برای risk؛ LLM فقط زبان/خلاصه. |

---

## الگوهایی که باید برداریم (لیست عملی)

### ۱. NHS 111 — baseline rules-only (الان)

```
keyword → D0/D1/D2 → template ثابت → notify داروساز
```

ADR-0004. **همین را formal کن** — از صفر نساز.

### ۲. Infermedica — map به ۳ سطح (الان)

```
D0 = intake / self-care
D1 = consultation (داروساز)
D2 = emergency (۱۱۵/ER)
```

۵ سطح را فشرده کن — ساختار جدید نساز.

### ۳. WHO — shadow → owner review → live (الان — P2)

```
LLM داخلی → 20–50 shadow review → تأیید owner → live
```

همین مسیر HANDOFF P2.

### ۴. Hybrid LLM — union بعد از live (بعداً)

```
keyword OR llm.needs_review — keyword downgrade نشود
```

ADR-0003. بعد از P2.

### ۵. D2 template جدا (اولویت کد بعدی)

```
red flag → ER_URGENT_REPLY + ۱۱۵
```

تنها گپ مهم نسبت به NHS — **یک template**، نه معماری جدید.

### ۶. CAIDRA / PV (milestone بعد)

```
عارضه دارویی → فرم PV
```

فعلاً D1 + keyword کافی؛ بعداً طبق استاندارد صنعت.

---

## کارهای بعدی (اولویت)

| # | کار | زمان |
|---|-----|------|
| 1 | P2 shadow review (20–50 پیام) | **الان** |
| 2 | `ER_URGENT_REPLY` برای D2 | بعد P2 |
| 3 | formal D0/D1/D2 در `CONTEXT.md` | با #2 |
| 4 | structured intake | بعد live |
| 5 | PV workflow | milestone بعد |

---

## لینک‌ها

- Notion: https://app.notion.com/p/3a1f6d55a673815aba45fc8e3fb9713d
- ADR-0003: [../adr/0003-triage-with-llm.md](../adr/0003-triage-with-llm.md)
- ADR-0004: [../adr/0004-triage-without-llm.md](../adr/0004-triage-without-llm.md)
