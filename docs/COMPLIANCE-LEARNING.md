# Compliance Learning Guide (Study Notes)

**Purpose:** Self-study map for EU-style privacy, safety, and security — applied to BaleMed.  
**Not legal advice.** Confirm with a lawyer before commercial launch in EU or other regulated markets.  
**Date:** 2026-07-13

---

## How to use this guide

1. Read one section per week (30–60 minutes).
2. After each section, fill the **BaleMed checklist** at the bottom.
3. Link your notes to repo docs: [SAFETY_RULES.md](SAFETY_RULES.md), [SECURITY.md](../SECURITY.md), [ADR-0002](adr/0002-clinical-trust-requirements-before-live-llm.md).
4. For blog posts, use [blog/BLOG-TEMPLATES.md](blog/BLOG-TEMPLATES.md).

---

## 1. Privacy — GDPR and health data

### Why it matters for BaleMed

Patient messages about drugs, symptoms, or pregnancy are **health data** (GDPR special category). Storing them in SQLite triggers privacy duties if you serve people in the EU or process their data from the EU.

### Official sources

| Resource | Link |
| --- | --- |
| GDPR (full text) | [EUR-Lex 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| EDPB — health domain | [edpb.europa.eu — Health and research](https://www.edpb.europa.eu/topics/specific-domains/health-and-research_en) |
| Article 9 (special categories) | [GDPRhub Art. 9](https://gdprhub.eu/Article_9_GDPR) |
| Principles (Art. 5) | [GDPRhub Art. 5](https://gdprhub.eu/index.php?title=Article_5_GDPR) |

### Concepts to learn

| Term | Plain meaning |
| --- | --- |
| **Data controller** | You (pharmacy / project owner) decide why and how data is processed |
| **Purpose limitation** | Collect only for pharmacy workflow — not “maybe useful later” |
| **Data minimization** | No raw webhooks by default; short logs; redacted LLM snippets |
| **Storage limitation** | Retention policy — delete old messages when policy says so |
| **Integrity & confidentiality** | HTTPS, `.env` secrets, access control on VPS |
| **Rights of data subjects** | Access, correction, deletion — plan before scale |

### BaleMed today (good habits already)

- `BALE_STORE_RAW_UPDATES=false` by default
- Logs avoid full message text and chat ids (see handlers)
- Secrets in `.env` only
- Local `/local/*` blocked at Caddy in production

### Gaps to study / plan

- [ ] Written retention policy (how long messages stay in SQLite)
- [ ] Process for patient deletion request
- [ ] Privacy notice text for patients (what the bot stores)
- [ ] DPIA (Data Protection Impact Assessment) if EU scale — template study only

---

## 2. Clinical regulation — Is the bot a “medical device”?

### Why it matters

If software has **medical purpose** (diagnose, treat, monitor disease), EU **MDR** may apply — heavy compliance (CE mark, notified body, etc.). BaleMed is designed as **workflow intake**, not diagnosis.

### Official sources

| Resource | Link |
| --- | --- |
| MDR (medical devices) | [EUR-Lex 2017/745](https://eur-lex.europa.eu/eli/reg/2017/745/oj) |
| Software qualification (MDCG 2019-11) | [EU Commission PDF](https://health.ec.europa.eu/document/download/175502/838259) |
| AI + MDR/IVDR (MDCG 2025-6) | [EU Commission PDF](https://health.ec.europa.eu/document/download/b78a17d7-e3cd-4943-851d-e02a2f22bbb4_en?filename=mdcg_2025-6_en.pdf) |

### Decision questions (from MDCG logic, simplified)

| Question | BaleMed intent |
| --- | --- |
| Is intended purpose medical? | **No** — intake and routing to pharmacist |
| Does it diagnose or treat? | **No** — prohibited in [SAFETY_RULES.md](SAFETY_RULES.md) |
| Does it replace clinical judgment? | **No** — pharmacist reviews escalated cases |
| Could a regulator disagree? | Possible if you add dosing/LLM patient advice — **do not** |

**Study task:** Read MDCG 2019-11 Section on “software without medical purpose” and write one paragraph in your blog: *why BaleMed stays workflow-only.*

---

## 3. AI regulation — EU AI Act

### Why it matters

LLM classification is an **AI system**. Rules depend on risk class: medical device AI = high-risk; general chatbot triage may face transparency and oversight expectations.

### Official sources

| Resource | Link |
| --- | --- |
| EU AI Act (full text) | [EUR-Lex 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) |
| Healthcare overview (readable) | [npj Digital Medicine](https://www.nature.com/articles/s41746-024-01213-6) |

### BaleMed AI posture (aligned with ADR-0001, ADR-0002)

| Practice | Why |
| --- | --- |
| `BALE_ENABLE_LLM=false` by default | Opt-in |
| Shadow before live | Human review batch |
| No LLM text to patients | Avoid unauthorized clinical advice |
| Validator blocks dangerous LLM strings | Fail-safe |
| Document trust gaps | Honest scope |

### Study task

Skim AI Act **Article 6** (high-risk) and **Annex I**. Ask: “If BaleMed never diagnoses, what risk class might apply?” Write notes — discuss with mentor, not Reddit.

---

## 4. Security

### Official sources

| Resource | Link |
| --- | --- |
| ENISA (EU cybersecurity) | [enisa.europa.eu](https://www.enisa.europa.eu/) |
| NIS2 Directive | [EUR-Lex 2022/2555](https://eur-lex.europa.eu/eli/dir/2022/2555) |

### BaleMed checklist (maps to [SECURITY.md](../SECURITY.md))

| Control | Status |
| --- | --- |
| HTTPS (Caddy) | VPS deploy |
| Webhook secret path | `/webhook/bale/{secret}` |
| Sending disabled by default | `BALE_ENABLE_SENDING=false` |
| No secrets in Git | `.gitignore` |
| Backup tested | `create_sqlite_backup` |
| `/local/*` not public | Caddy `respond /local/* 404` |

---

## 5. Pharmacy ethics (your edge — not only EU law)

EU rules do not replace **pharmacist professional duty**. Your 6 years border experience is the grounding:

- Escalate when unclear
- Never dose or diagnose via bot
- Document what software cannot know (typos, no allergy file)
- Shadow LLM before trusting routing

Cross-link: [VISION-AND-ROADMAP.md](VISION-AND-ROADMAP.md), [CAREER-NARRATIVE.md](CAREER-NARRATIVE.md).

---

## 6. Learning path (8 weeks, part-time)

| Week | Topic | Output |
| --- | --- | --- |
| 1 | GDPR Art. 5 + 9 | Fill privacy checklist above |
| 2 | EDPB health page | 5 bullet “what we store / why” for patients |
| 3 | MDCG 2019-11 | One paragraph: not a medical device |
| 4 | EU AI Act skim | Shadow vs live note in ADR style |
| 5 | SECURITY.md audit | VPS re-check `check-env-safe.py` |
| 6 | Retention policy draft | Issue or ADR in repo |
| 7 | Blog post 1 | Safety gap (template in blog/) |
| 8 | Blog post 2 | Compliance note (template in blog/) |

---

## 7. BaleMed master checklist (copy to Notion)

```text
[ ] Intended purpose documented: workflow intake, not diagnosis
[ ] Health data: minimization + retention planned
[ ] LLM: shadow mode until P2 + ADR-0002 gates
[ ] No patient-facing LLM text
[ ] HTTPS + secrets + sanitized logs on VPS
[ ] Clinical gaps tracked as GitHub issues (clinical_safety_gap template)
[ ] Blog/articles: anonymized examples only
[ ] Legal review before EU commercial launch (external counsel)
```

---

## Related repo docs

| Doc | Link |
| --- | --- |
| Safety rules | [SAFETY_RULES.md](SAFETY_RULES.md) |
| Security policy | [SECURITY.md](../SECURITY.md) |
| Shadow LLM ADR | [adr/0001-llm-shadow-mode.md](adr/0001-llm-shadow-mode.md) |
| Clinical trust ADR | [adr/0002-clinical-trust-requirements-before-live-llm.md](adr/0002-clinical-trust-requirements-before-live-llm.md) |
| Blog templates | [blog/BLOG-TEMPLATES.md](blog/BLOG-TEMPLATES.md) |
