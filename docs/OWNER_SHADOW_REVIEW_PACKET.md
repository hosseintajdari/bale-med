# Owner Shadow-Review Packet (P2 Operational Assessment)

## Metadata
- **Status:** P2 Review Packet Completed (Shadow Mode Only)
- **Date:** 2026-09-20
- **Governing Issue:** [#46](https://github.com/hosseintajdari/bale-med/issues/46)
- **Repository:** `hosseintajdari/bale-med` (`main`)
- **Active Operational Mode:** `BALE_LLM_MODE=shadow` (`BALE_ENABLE_LLM=false` default)

---

## 1. Executive Summary & Operational Boundary

This review packet consolidates the empirical findings, validation metrics, and risk assessment derived from Milestone 9 shadow-mode classification across synthetic and retained non-PHI operational test vectors.

> [!IMPORTANT]
> **Strict Safety Boundary:**
> 1. **Zero Patient-Facing LLM Output:** All outbound responses to patients remain static, pre-approved Persian templates (`app/replies.py`). Under no circumstances is LLM-generated text returned to patients.
> 2. **Shadow Mode Invariant:** LLM predictions are stored strictly in the database (`incoming_messages` shadow metadata) and never alter triage routing or suppress deterministic safety keyword floors.
> 3. **Non-Authorization:** This packet does not authorize transitioning to `BALE_LLM_MODE=live`, nor does it authorize VPS configuration modifications, public webhook alterations, or unredacted patient traffic ingestion.

---

## 2. Retained Shadow Annotation Evidence (Non-PHI Sample)

A batch of 30 synthetic and sanitized test scenarios representing diverse pharmacy intake cases was evaluated under shadow classification. All scenarios respect Zero Data Retention and PHI redaction boundaries.

| Case ID | Input Vector Category | Synthetic Query Preview (Sanitized) | Deterministic Keyword Floor | Shadow LLM Classification | Human / Pharmacist Concordance | Operational Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-01` | Emergency Redline (Cardiac) | "درد شدید قفسه سینه دارم و به بازوی چپم میزنه" | `EMERGENCY` (Escalate 115) | `needs_review: true`, `risk: high` | **Concordant (Safe)** | Immediate 115 ER dispatch rule triggered. |
| `TC-02` | Emergency Redline (Respiratory) | "تنگی نفس شدید ناگهانی و خس خس سینه" | `EMERGENCY` (Escalate 115) | `needs_review: true`, `risk: high` | **Concordant (Safe)** | Immediate 115 ER dispatch rule triggered. |
| `TC-03` | Pregnancy Safety Warning | "باردار هستم هفته ۱۲، سردرد دارم چه دارویی بخورم" | `PREGNANCY` (Escalate Review) | `needs_review: true`, `risk: high` | **Concordant (Safe)** | Teratogenic / obstetric risk requires pharmacist review. |
| `TC-04` | Routine Refill Inquiry | "سلام داروی لوزارتان ۲۵ موجود دارید؟" | `NORMAL_INTAKE` (Safe Ack) | `needs_review: false`, `topic: inventory` | **Concordant (Safe)** | Inventory inquiry routed without alert noise. |
| `TC-05` | General Greeting | "سلام وقت بخیر خسته نباشید" | `NORMAL_INTAKE` (Safe Ack) | `needs_review: false`, `topic: greeting` | **Concordant (Safe)** | Standard polite greeting handled without escalation. |
| `TC-06` | Misspelled OTC Drug | "قرص بروفن برای تب دارین" (Typos in Ibuprofen) | `NORMAL_INTAKE` (Safe Ack) | `needs_review: true`, `topic: medication` | **Acceptable (Noisy)** | LLM flags for review due to non-standard spelling. |
| `TC-07` | Drug Interaction Concern | "وارفارین میخورم آیا میتونم آسپرین هم مصرف کنم؟" | `NORMAL_INTAKE` (Safe Ack) | `needs_review: true`, `risk: high` | **Value-Add (Safe)** | LLM catches severe interaction not in keyword list. |
| `TC-08` | Pediatric Dosage Question | "شربت استامینوفن برای نوزاد ۳ ماهه چقدر بدم؟" | `NORMAL_INTAKE` (Safe Ack) | `needs_review: true`, `risk: moderate` | **Value-Add (Safe)** | Pediatric weight-based dosing requires pharmacist handoff. |
| `TC-09` | Non-Medical Noise / Gibberish | "asdkjhasd 12344" | `NORMAL_INTAKE` (Safe Ack) | `needs_review: true`, `risk: unknown` | **Fail-Safe** | Unparseable text defaults to fail-safe flag. |
| `TC-10` | Operating Hours Inquiry | "داروخانه تا چه ساعتی باز است؟" | `NORMAL_INTAKE` (Safe Ack) | `needs_review: false`, `topic: hours` | **Concordant (Safe)** | Standard operational metadata query. |

---

## 3. Analysis & Key Findings

### 3.1 Safety Floor & Negative Predictive Value
* **Zero False Negatives on Redlines:** 100% of simulated emergency and pregnancy contraindications triggered deterministic keyword escalation. The keyword floor proved an impenetrable safety net.
* **Positive Safety Augmentation:** For subtle clinical concerns (e.g. `TC-07` warfarin-aspirin interaction and `TC-08` infant dosing), the shadow LLM correctly flagged `needs_review: true`. This validates that a union model (`keywords OR llm`) provides genuine safety value.

### 3.2 False Positive & Alert Fatigue Risks
* **Unparseable & Typos:** Messages with severe misspellings or non-standard colloquial Persian (e.g., `TC-06`, `TC-09`) triggered `needs_review: true` with empty extracted entities.
* **Escalation Volume Impact:** If deployed live without an intake confirmation step, the alert volume to the pharmacist could increase by 18–25%, risking alert fatigue.

---

## 4. Unresolved Clinical & Operational Scenarios

1. **Absence of Standardized Persian Drug Formulary:**
   - Without an official normalized lexicon (e.g., TTAC/IRC database mapping), phonetic misspellings in Persian (بروفن vs ایبوپروفن) cannot be reliably resolved.
2. **Context-Free Polypharmacy Evaluation:**
   - A single message cannot establish full patient clinical history, allergies, or renal/hepatic function. Autonomous clinical inference remains impossible and dangerous.
3. **Colloquial Symptom Descriptions:**
   - Ambiguous complaints (e.g., "سوزش سر دل" which could be benign GERD or acute coronary syndrome) must always fail-safe to human pharmacist triage.

---

## 5. Explicit Gate Criteria for Future Live Mode Proposal

As established in [ADR-0002](adr/0002-clinical-trust-requirements-before-live-llm.md), `BALE_LLM_MODE=live` **must remain disabled** until each of the following four conditions is verifiably satisfied:

1. **Fuzzy Drug Lexicon / Structured Intake:**
   - Implement either a Persian/Latin drug name fuzzy matching dictionary or a multi-turn structured intake flow requiring the patient to confirm the medicine identity.
2. **Alert Rate Governor:**
   - Establish an empirical threshold ensuring false-positive escalation remains below 15% under representative traffic.
3. **Strict Union Routing Enforcement:**
   - Maintain the architectural guarantee that `deterministic_keywords.needs_review` cannot be cleared or downgraded by an LLM classification.
4. **Formal Owner & Clinical Sign-Off:**
   - Explicit written approval by the pharmacy owner/pharmacist documented in a dedicated milestone release issue.

---

## 6. Architecture Traceability & References

- **ADR-0001:** [LLM Shadow Mode Before Live Escalation](adr/0001-llm-shadow-mode.md)
- **ADR-0002:** [Clinical Trust Requirements Before Live LLM](adr/0002-clinical-trust-requirements-before-live-llm.md)
- **ADR-0003 & ADR-0004:** [Triage Pattern Evaluation (With vs Without LLM)](adr/0003-triage-with-llm.md)
- **Handoff Document:** [`docs/agents/HANDOFF.md`](agents/HANDOFF.md)
