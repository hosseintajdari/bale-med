# Safety Rules

## Pharmacy Workflow Boundaries
This bot must not diagnose, prescribe, replace a pharmacist, or recommend medication changes. It may collect structured information, acknowledge receipt, and route cases to a pharmacist.

## Prohibited Behaviors
- Do not provide diagnosis or differential diagnosis.
- Do not recommend starting, stopping, or changing medications.
- Do not provide dosage, schedule, or interaction decisions.
- Do not provide emergency triage decisions as medical authority.

## Required Human Review
Route to a pharmacist when a message includes urgent symptoms, unclear medication use, pregnancy or breastfeeding, children, serious side effects, allergy concerns, controlled medications, or any request for medical judgment.

## Escalation Triggers
Escalate immediately when input is incomplete, ambiguous, high-risk, or requests clinical judgment. If unsure, escalate by default.

## Privacy and Auditability
Store incoming messages only for legitimate workflow needs. Do not log secrets, Bale tokens, private keys, or unnecessary personal data. Keep raw webhook payloads available for debugging and audit trails during the MVP, then revisit retention rules before production.

Review metadata is operational workflow tracking only. It may mark that pharmacist review is needed, but it must not be treated as diagnosis, treatment advice, or emergency triage.

## Data Handling for MVP
- Store only what is required for auditability and workflow continuity.
- Keep credentials in environment variables only.
- Define retention duration and deletion process before production launch.

## Safe Reply Style
Replies should be neutral and operational. Example: "Thanks. Your message was received and will be reviewed by the pharmacy team." Do not include clinical advice until a pharmacist-approved workflow exists.
