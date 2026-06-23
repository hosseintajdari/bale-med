# شروع کار با Agent Skills (راهنمای عملی)

این راهنما برای پروژه **bale-med** (ربات داروخانه روی Bale) نوشته شده است.

## آیا در ایجنت جدید قابل استفاده است؟

**بله** — به شرطی که:

1. این ریپو را در Cursor باز کرده باشید (skillها در `.cursor/skills/` سطح **پروژه** هستند).
2. branch حاوی skillها و setup را checkout کرده باشید (فعلاً [PR #29](https://github.com/hosseintajdari/bale-med/pull/29) یا `main` بعد از merge).
3. setup انجام شده باشد (`docs/agents/` موجود باشد — الان انجام شده است).

هر **Chat جدید** یا **Cloud Agent جدید** روی همین workspace، skillها را می‌بیند. نیازی به نصب مجدد در هر session نیست.

### دو نوع skill

| نوع | نحوه فراخوانی | مثال |
|-----|---------------|------|
| **User-invoked** | شما در چت تایپ می‌کنید | `/grill-with-docs`، `/triage`، `/ask-matt` |
| **Model-invoked** | agent خودش در صورت مناسب بودن task انتخاب می‌کند | `tdd`، `diagnosing-bugs`، `domain-modeling` |

برای model-invoked می‌توانید صریح هم بگویید: «با TDD این باگ را درست کن» یا «این باگ را diagnose کن».

---

## نقشه سریع — کدام skill؟

```
نمی‌دانید از کجا شروع کنید     →  /ask-matt
ایده / فیچر جدید (با کدبیس)    →  /grill-with-docs
باگ سخت یا رفتار عجیب           →  diagnosing-bugs (یا بگویید «diagnose کن»)
issue / PR جدید از بیرون        →  /triage
فیچر کوچک در یک session         →  /implement (بعد از grill)
فیچر بزرگ / چند session         →  /grill-with-docs → /to-prd → /to-issues
تست قبل از کد                   →  tdd
نگهداری معماری کدبیس            →  /improve-codebase-architecture
پایان session / ادامه در agent دیگر →  /handoff
```

جریان کامل در `.cursor/skills/ask-matt/SKILL.md` توضیح داده شده است.

---

## پیشنهاد قدم‌های بعدی (برای این پروژه)

| اولویت | کار | skill پیشنهادی |
|--------|-----|----------------|
| 1 | ساخت `CONTEXT.md` — واژگان دامنه داروخانه (مثلاً «نیاز به بررسی داروساز»، «پیام ورودی»، «لایه پاسخ امن») | `/grill-with-docs` |
| 2 | triage کردن issueهای باز GitHub و آماده‌سازی برای agent | `/triage` |
| 3 | شروع Milestone 9 (LLM) با مرزهای ایمنی داروخانه | `/grill-with-docs` سپس `/to-prd` |
| 4 | هر چند روز یک‌بار — بررسی عمق ماژول‌ها | `/improve-codebase-architecture` |

**هنوز لازم نیست:** `/setup-matt-pocock-skills` — یک‌بار انجام شده است.

---

## تمرین‌های عملی (۵ دقیقه‌ای)

هر تمرین را در یک **Chat جدید** در Cursor امتحان کنید. متن زیر را copy-paste کنید.

### تمرین ۱ — مسیریابی (`/ask-matt`)

```
/ask-matt

می‌خواهم برای Milestone 9 (ادغام LLM) برنامه بریزم،
ولی نباید bot تشخیص بدهد یا دوز پیشنهاد کند.
از کدام skill شروع کنم؟
```

**انتظار:** agent مسیر `/grill-with-docs` → `/to-prd` → `/to-issues` را پیشنهاد دهد.

---

### تمرین ۲ — زبان دامنه (`/grill-with-docs`)

```
/grill-with-docs

می‌خواهیم CONTEXT.md بسازیم. سه اصطلاح مهم این پروژه:
- webhook امن Bale
- لایه پاسخ امن (safe reply layer)
- صف بررسی داروساز (pharmacist review queue)

سوالاتت را بپرس تا اصطلاحات را دقیق کنیم.
```

**انتظار:** مصاحبه کوتاه و پیش‌نویس `CONTEXT.md` (یا پیشنهاد ساخت آن).

---

### تمرین ۳ — triage یک issue (`/triage`)

```
/triage

لیست issueهای باز با label needs-triage را ببین
و یکی را برای agent آماده کن (اگر issue مناسبی نیست، بگو).
```

**پیش‌نیاز:** `gh` CLI لاگین باشد (`gh auth status`).

---

### تمرین ۴ — دیباگ با TDD (`tdd`)

```
یک تست unittest برای app/safety.py بنویس:
اگر کاربر بپرسد "چقدر استامینوفن بخورم؟"
bot نباید دوز پیشنهاد دهد و باید به داروساز ارجاع دهد.
با red-green-refactor پیش برو.
```

**انتظار:** agent ابتدا تست fail می‌نویسد، بعد حداقل تغییر در کد.

---

### تمرین ۵ — handoff بین sessionها (`/handoff`)

```
/handoff

خلاصه کن: setup skillها انجام شد، CONTEXT.md هنوز نیست،
قدم بعدی grill-with-docs برای Milestone 9 است.
```

**انتظار:** فایل handoff markdown. در Chat بعدی:

```
این handoff را ادامه بده: [مسیر فایل]
```

---

## نکات مهم برای bale-med

1. **ایمنی داروخانه** — skillها تشخیص یا دوز پیشنهاد نمی‌دهند؛ `/grill-with-docs` برای Milestone 9 مرزها را صریح نگه می‌دارد.
2. **Context window** — grilling + PRD + issues را در **یک session** نگه دارید؛ بعد از `/to-issues` برای هر issue session تازه باز کنید.
3. **فایل‌های مرجع** — `docs/agents/issue-tracker.md`، `triage-labels.md`، `domain.md`
4. **ویرایش بعدی** — `docs/agents/*.md` را مستقیم ویرایش کنید؛ فقط برای عوض کردن issue tracker دوباره setup لازم است.

---

## عیب‌یابی

| مشکل | راه‌حل |
|------|--------|
| `/skill-name` کار نمی‌کند | مطمئن شوید `.cursor/skills/<name>/SKILL.md` وجود دارد و workspace درست است |
| `/triage` خطای `gh` می‌دهد | `gh auth login` و دسترسی به `hosseintajdari/bale-med` |
| agent skill را نمی‌شناسد | نام را دقیق بنویسید یا بگویید: «skill diagnosing-bugs را بخوان و اجرا کن» |
| label در GitHub نیست | agent با `gh label create` می‌سازد (طبق `triage-labels.md`) |

---

## منابع بیشتر

- [mattpocock/skills README](https://github.com/mattpocock/skills)
- `.cursor/skills/ask-matt/SKILL.md` — نقشه کامل جریان‌ها
- `AGENTS.md` → بخش **Agent skills**
