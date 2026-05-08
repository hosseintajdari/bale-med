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
Store incoming messages only for legitimate workflow needs. Do not log secrets, Bale tokens, private keys, raw webhook payloads, chat ids, or full message text. Operational logs may include sanitized audit fields such as stored row id, text presence, text length, review status, and send mode. Keep raw webhook payload storage disabled by default, then revisit retention rules before production.

Review metadata is operational workflow tracking only. It may mark that pharmacist review is needed, but it must not be treated as diagnosis, treatment advice, or emergency triage.

Admin review notifications are for operational awareness only. They may include the stored message id, review reason, and a short sanitized text preview. They must not include raw webhook payloads, secrets, chat ids, or full patient text.

## Data Handling for MVP
- Store only what is required for auditability and workflow continuity.
- Keep credentials in environment variables only.
- Define retention duration and deletion process before production launch.

## Safe Reply Style
Replies should be neutral, operational, and easy to read in Persian mobile chat. Example: "پیام شما دریافت شد. لطفا منتظر بررسی داروساز بمانید." Do not include clinical advice until a pharmacist-approved workflow exists.
