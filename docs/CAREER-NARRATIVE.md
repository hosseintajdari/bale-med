# Career Narrative — Clinical Builder (Portfolio Draft)

**Purpose:** Wording for resume, LinkedIn, and job applications. Update as projects ship.  
**Date:** 2026-07-13  
**Audience:** Health tech recruiters, digital health startups, remote clinical product roles

---

## Identity (one sentence)

PharmD and pharmacy manager (6 years, Iran–Pakistan border) building **safety-first pharmacy automation** — combining real workflow experience with shipped software and documented AI limits.

---

## Why border context matters

- Served patients across **language and culture** boundaries (Persian, regional border communities).
- Saw **access, price, and self-medication** pressures firsthand — not textbook cases.
- Managed pharmacy operations — not only dispensing: staff, stock, patient flow.

This is **underserved population health + operations** — relevant to global health tech, NGOs, and regional digital health.

---

## Project 1: BaleMed (this repository)

**What it is:** Bale messenger bot for pharmacy message intake — secure webhook, SQLite audit trail, pharmacist review routing, optional LLM classification in shadow mode, VPS deployment.

**What I did (clinical + technical):**

- Defined safety boundaries: no diagnosis, dosing, or prescription replacement ([SAFETY_RULES.md](SAFETY_RULES.md)).
- Designed shadow-before-live LLM gate with pharmacist owner review ([ADR-0001](adr/0001-llm-shadow-mode.md), [ADR-0002](adr/0002-clinical-trust-requirements-before-live-llm.md)).
- Deployed dry-run production on Iran VPS; Git pull deploy; CI validation.
- Identified **clinical trust gaps** (drug typos, no allergy EHR) and documented them — did not hide behind “model upgrade.”

**Stack (honest level):** Python, FastAPI, SQLite, Bale API, LLM API (shadow), systemd/Caddy, GitHub Actions.

**GitHub:** `hosseintajdari/bale-med` (private or public when ready)

---

## Project 2: Medicine price bot (planned)

**Problem:** Patients constantly ask price and availability — especially in border areas with supply fluctuation.

**Planned proof:** Fuzzy drug search + price band + clear disclaimer; same safety discipline as BaleMed.

**Resume line (future):** Built medicine price transparency bot for border pharmacy context — access-focused, non-clinical advice.

---

## Project 3: Pharmacy management bot/app (planned)

**Problem:** Manager overhead — stock, handoff, simple reporting.

**Planned proof:** Low-stock alerts, daily ops summary, integration hook to BaleMed pending reviews.

**Resume line (future):** Pharmacy operations assistant from real manager workflow — not generic ERP clone.

---

## Skills matrix (for ATS / recruiters)

| Clinical | Technical | Product / safety |
| --- | --- | --- |
| Medication safety boundaries | Python, FastAPI | Requirements from practice |
| Patient intake workflow | SQLite, REST webhooks | Shadow mode / human-in-the-loop |
| Pharmacist escalation judgment | Linux VPS deploy basics | ADRs and safety documentation |
| Border / multilingual context | Git, GitHub Actions CI | Honest AI limitation analysis |
| Pharmacy management | Bale / messenger integrations | Portfolio-style public docs |

---

## Resume bullets (copy-ready)

Use 3–5 on a one-page resume:

1. PharmD with **6 years** as pharmacist and **pharmacy manager** on the **Iran–Pakistan border**, serving multilingual communities with complex access and self-medication patterns.

2. Built **BaleMed**, a production-oriented pharmacy intake bot (FastAPI, SQLite, VPS) with **pharmacist-in-the-loop** design and **no autonomous clinical advice**.

3. Implemented **shadow LLM classification** with owner go-live gate; documented **clinical trust gaps** (drug name typos, no EHR allergy data) in architecture decision records.

4. Designed escalation using **keyword safety net + optional LLM union**; fail-safe routing when AI output is invalid or ambiguous.

5. *(Future)* Medicine price transparency bot and pharmacy operations tools — **unified portfolio** for regional pharmacy automation.

---

## LinkedIn “About” (short draft)

I am a pharmacist and pharmacy manager turned clinical product builder. After six years on the Iran–Pakistan border, I started building tools that match real pharmacy workflow — safe patient intake on Bale, honest limits on AI, and documentation that treats patient safety as a logic problem, not only a coding problem. I am targeting **healthcare technology** roles where clinical judgment and shipped software both matter.

---

## Interview story (60 seconds)

> “I managed pharmacy workflow in a border region where patients ask about price, access, and medicines in messy, real-world language. I built a Bale bot that receives messages safely and routes hard cases to a pharmacist — never auto-diagnosing. We added LLM in shadow mode first. Testing showed bigger models don’t fix misspelled drug names without a drug list. I documented that and blocked live AI routing until we have lexicon or structured intake. That’s the kind of health tech I want to do: systems that know what they don’t know.”

---

## Location note (Iran)

- Target **remote** health tech, clinical specialist, implementation, and health AI safety roles.
- Portfolio in **English on GitHub** speaks louder than local market incentives alone.
- Some employers have geo restrictions — apply widely; diaspora and regional health orgs are viable channels.

---

## Keep this doc alive

After each milestone:

- Add shipped feature + **what you learned clinically**.
- Add one bullet to resume section.
- Link new ADR or issue when you discover a limit.

Related: [VISION-AND-ROADMAP.md](VISION-AND-ROADMAP.md)
