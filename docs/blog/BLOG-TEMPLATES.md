# Blog Templates (Notion-ready)

Minimal, clean blocks — copy one section into Notion (`/` → Markdown or paste).  
Replace `{{placeholders}}`. Remove repo links if repo stays private.

**Style:** short title, one hook, bullets, one diagram optional, links at end.

---

## Notion setup (once)

1. New page → **Blog** database (optional: Status, Tag, Published date).
2. Properties: `Status` (Draft / Review / Published), `Tag` (Safety / Compliance / Build log).
3. Paste a template body below into each new page.
4. Pin [COMPLIANCE-LEARNING.md](../COMPLIANCE-LEARNING.md) as sidebar link.

---

## Template A — Case study (build + clinical lesson)

```markdown
# {{Title: e.g. Why we kept LLM in shadow mode}}

**One line:** {{What you built and what you refused to do.}}

---

## Context

- **Who:** Pharmacist / builder, border healthcare
- **Project:** BaleMed — Bale pharmacy intake bot
- **Problem:** {{Patient problem in plain language}}

## What we shipped

- {{Feature 1}}
- {{Feature 2}}

## What went wrong (honest)

{{e.g. Nonsense text → needs_review true; misspelled drug names not fixed by LLM}}

## What we decided

{{e.g. No live LLM until lexicon or structured intake — ADR-0002}}

## Takeaway for health tech

> {{One sentence recruiters should remember}}

## Links

- Repo ADR: {{link if public}}
- GDPR health data: https://www.edpb.europa.eu/topics/specific-domains/health-and-research_en
- EU AI Act: https://eur-lex.europa.eu/eli/reg/2024/1689/oj

---
*Disclaimer: Workflow support only, not medical advice. Anonymized examples.*
```

---

## Template B — Clinical / safety gap (logic problem)

```markdown
# {{Title: e.g. A bigger model does not fix drug typos}}

**Gap type:** Drug knowledge | Allergy data | LLM escalation | Workflow

---

## The gap

{{2–3 sentences — non-code problem}}

## Example (fake data)

| Patient wrote | System did | Ideal |
| --- | --- | --- |
| {{text}} | {{behavior}} | {{what pharmacist needs}} |

## Why code alone fails

{{Data, regulation, or workflow — not "need GPT-5"}}

## Mitigation we're exploring

1. {{e.g. Persian drug fuzzy lexicon}}
2. {{e.g. structured intake}}
3. {{stay in shadow}}

## For pharmacists in health tech

{{Your clinical insight — this is the resume gold}}

## Links

- MDCG software qualification: https://health.ec.europa.eu/document/download/175502/838259
- Project safety rules: {{link}}

---
*Not legal advice. Personal learning notes.*
```

---

## Template C — Compliance note (EU study, 5 min read)

```markdown
# {{Title: e.g. GDPR Article 9 and pharmacy chatbots}}

**Reading time:** 5 min  
**Studied:** {{date}}

---

## I wanted to know

{{One question}}

## Short answer

{{3–5 lines in your words}}

## How it applies to my bot

| GDPR idea | My project |
| --- | --- |
| Health data | Message text about drugs |
| Minimization | No raw webhook storage default |
| {{…}} | {{…}} |

## Still unclear

- {{question for lawyer or mentor}}

## Sources

- [GDPR Art. 9](https://gdprhub.eu/Article_9_GDPR)
- [EDPB Health](https://www.edpb.europa.eu/topics/specific-domains/health-and-research_en)

---
*Study notes — not legal advice.*
```

---

## Template D — Build log (short, modern)

```markdown
# {{Week / milestone}} — {{one outcome}}

✅ {{done}}  
⏳ {{in progress}}  
🚫 {{blocked — e.g. live LLM until P2}}

**Ship:** {{e.g. git pull on VPS, shadow_ok confirmed}}  
**Learn:** {{one clinical or compliance sentence}}

→ Next: {{single step}}
```

---

## Publishing checklist

- [ ] No real patient text
- [ ] No tokens, domains, API keys
- [ ] Disclaimer line included
- [ ] You read every line (agent draft OK, your approval required)
- [ ] English OK for target audience (EU / remote health tech)

---

## Suggested first three posts

1. **Template B** — Drug typos and LLM limits (your `ایپوبببروفن` / nonsense examples, anonymized).
2. **Template A** — Shadow mode before live (P1 → P2 gate).
3. **Template C** — GDPR Art. 9 and messenger health data.

Copy to Notion → tag `Safety` / `Compliance` → publish to LinkedIn or blog when ready.
