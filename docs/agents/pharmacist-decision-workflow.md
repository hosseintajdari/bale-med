# Workflow داروساز — بعد از پایان سؤالات بیمار در چت

**Owner:** داروساز + توسعه‌دهنده (شما)  
**Milestone:** 9 — shadow LLM؛ پاسخ بیمار **دستی** توسط داروساز مجاز است  
**Notion:** see [notion-placement-index.md](./notion-placement-index.md)

---

## 1. موارد لازم در چat (intake checklist)

جمع‌آوری قبل از تصمیم ارجاع. ربات می‌تواند بخشی را بپرسد؛ **بقیه توسط داروساز** بعد از escalation.

### 1.1 هویت و زمینه

| فیلد | اجباری؟ | مثال case فعلی |
| --- | --- | --- |
| سن | بله | 23 |
| جنس | بله | زن |
| وضعیت بارداری/شیردهی | اگر مؤنث بالغ | پرسیده نشده — **بپرس** |
| شغل/زمینه (اختیاری) | خیر | دانشجو، نوروفیدبک |

### 1.2 دارو

| فیلد | اجباری؟ | مثال |
| --- | --- | --- |
| نام دارو(ها) | بله | atomoxetine، chlordiazepoxide |
| دوز و زمان مصرف | بله | 10 mg شب‌ها؛ صبح atomoxetine |
| مدت مصرف | بله | پرسیده نشده |
| پزشک تجویزکننده | توصیه | پرسیده نشده |

### 1.3 عارضه / علامت

| فیلد | اجباری؟ | مثال |
| --- | --- | --- |
| علامت اصلی | بله | تنگی/مشکل مجاری ادراری |
| زمان شروع | بله | پرسیده نشده |
| شدت (۱–۱۰ یا توصیفی) | بله | پرسیده نشده |
| توانایی ادرار کامل | **بحرانی** | پرسیده نشده |
| red flags (تب، درد شدید، …) | بله | پرسیده نشده |

### 1.4 مرز — ربات vs داروساز

| ربات (خودکار) | داروساز (شما در Bale) |
| --- | --- |
| دریافت پیام + escalation template | سؤالات تکمیلی |
| intake عمومی | سطح ارجاع (با مشاوره ER) |
| **نه** تشخیص / قطع دارو / دوز | پاسخ operational + ارجاع |

---

## 2. نقطه تصمیم (بعد از intake)

```text
پیام بیمار → ربات: escalation / intake
     ↓
داروساز: سؤالات تکمیلی (حداکثر ۳ در هر نوبت)
     ↓
[اختیاری] مشاوره داخلی ER — er-consult-questions-draft.md
     ↓
تصمیم: A | B | C | D | E  (below)
     ↓
پاسخ Bale + ثبت در Notion / annotation
```

---

## 3. سناریوهای داروساز (شاخه A–E)

### A — سؤالات تکمیلی (هنوز تصمیم نگرفته)

**Trigger:** اطلاعات ناکافی  
**Action:** ۲–۳ سؤال؛ بدون توصیه دارویی  

**پاسخ نمونه:**
> لطفاً بگویید از چه زمانی این علامت شروع شد؟ آیا ادرار را کامل انجام می‌دهید یا نه؟ تب یا درد شدید دارید؟

---

### B — ارجاع سرپایی (غیر ER)

**Trigger:** عارضه مزاحم، بدون red flag در چت  
**Action:** ارجاع به پزشک معالج؛ **بدون** قطع/تغییر دارو در چت  

**پاسخ نمونه:**
> با توجه به علامت گزارش‌شده، لطفاً در اولین فرصت با پزشک معالج خود تماس بگیرید. تا زمان بررسی، بدون مشورت پزشک دارو را قطع یا تغییر ندهید.

---

### C — ER / فوری

**Trigger:** red flag (احتباس، درد شدید، تب، بدتر شدن سریع) — **با تأیید مشاوره ER**  
**Action:** توصیه مراجعه فوری  

**پاسخ نمونه:**
> این علامت می‌تواند جدی باشد. لطفاً امروز به اورژانس مراجعه کنید. در صورت بدتر شدن با ۱۱۵ تماس بگیرید.

---

### D — مراجعه حضوری داروخانه

**Trigger:** نیاز به مصاحبه حضوری، هماهنگی نسخه  
**Action:** وقت مشخص + چک‌لیست اسناد  

---

### E — بستن پرونده (follow-up)

**Trigger:** بیمار گزارش کرد مراجعه کرد / تماس گرفت  
**Action:** ثبت نتیجه؛ بدون توصیه دارویی جدید در چت  

---

## 4. کانال مشاوره ER (همسر) — internal only

- ورودی: خلاصه anonymized از §1  
- خروجی: سطح ارجاع + red flags + قالب جمله (optional)  
- **Notion page:** Internal → ER consult  
- **Draft questions:** [er-consult-questions-draft.md](./er-consult-questions-draft.md)

---

## 5. Case فعلی (#43 + #44) — وضعیت

| DB id | متن کوتاه | LLM | annotation پیشنهادی |
| --- | --- | --- | --- |
| 43 | atomoxetine + chlordiazepoxide + مشکل ادرار | needs_review=true | needs_review **yes**؛ drug_name **no** → `atomoxetine, chlordiazepoxide` |
| 44 | 23F دانشجو نوروفیدبک | needs_review=false | needs_review **yes** (context) یا **no** (standalone) — owner: **no** OK |

**تصمیم داروساز:** نیاز به مراجعه — مسیر **A** (سؤالات) سپس **B** یا **C** بسته به red flags.

**سؤالات فوری برای بیمار (A):**
1. از چه زمانی مشکل ادرار دارید؟
2. آیا اصلاً نمی‌توانید ادرار کنید یا فقط سخت است؟
3. تب، لرز، یا درد شدید پهلو/شکم دارید؟
4. احتمال بارداری؟

---

## 6. شاخه‌های جدا — product backlog (Notion + GitHub)

| ID | Feature | Why separate |
| --- | --- | --- |
| P1 | **Conversation linking** (same chat_id) | پیام ۱+۲ = یک پرونده |
| P2 | **Referral tier** enum in DB | self_care / outpatient / urgent / ER |
| P3 | **Internal ER consult log** | audit مشاوره همسر |
| P4 | **Pharmacist manual reply** flag | تمایز پاسخ owner vs bot template |
| P5 | **Case closure** status | ارجاع داده شد / بسته |
| P6 | **Controlled med flag** | benzodiazepine → always needs_review |

---

## 7. Shadow annotation (VPS — when ready)

```bash
ssh balemed
cd /opt/bale-bot && . .venv/bin/activate

python3 deploy/scripts/annotate-shadow-review.py 43 \
  --needs-review-ok yes \
  --drug-name-ok no \
  --corrected-drug-name "atomoxetine, chlordiazepoxide" \
  --owner-notes "side_effect urinary; referral needed; see pharmacist-decision-workflow.md"

python3 deploy/scripts/annotate-shadow-review.py 44 \
  --needs-review-ok yes \
  --owner-notes "intake context 23F; pairs with #43"
```

---

## 8. تسک داروساز (اولین: بعد از پایان سؤالات)

**Goal:** از همین بستر (Bale + Notion + ER consult) برای تصمیم استفاده کنید.

**Checklist:**
- [ ] سؤالات §5 را در Bale بفرستید (شاخه A)
- [ ] پاسخ همسر را در Notion ER consult پر کنید
- [ ] تصمیم B/C/D را بگیرید و پاسخ نهایی بفرستید
- [ ] annotation #43 و #44 روی VPS
- [ ] ایده‌های backlog §6 را در Notion Product backlog ثبت کنید
- [ ] اگر red flag policy از ER آمد → draft به `SAFETY_RULES` یا ADR

**GitHub issue:** linked from Notion Tasks (created by agent).
