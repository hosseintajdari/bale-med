---
name: Clinical / safety gap (non-code)
about: Document a logical, clinical, or trust limit — not only a software bug
title: "Safety: "
labels: "domain-gap, needs-triage"
assignees: ''
---

## Summary

What is the gap in plain language? (One paragraph.)

## Clinical / patient impact

Why does this matter for patient safety or pharmacist workload?

## Example (anonymized)

- Patient message (fake or redacted): 
- What the system did: 
- What should happen ideally: 

## Type of gap

- [ ] Drug knowledge (names, typos, formulary)
- [ ] Allergy / history not in message
- [ ] LLM over- or under-escalation
- [ ] Workflow / pharmacist burnout
- [ ] Language / border context
- [ ] Other: 

## Code vs logic

- [ ] Needs code change
- [ ] Needs data / lexicon / integration
- [ ] Needs ADR or policy only
- [ ] Block live LLM until resolved

## Proposed direction (draft)

What mitigation do you suggest? (Lexicon, structured intake, stay in shadow, etc.)

## Links

- Related ADR: 
- Related doc: [VISION-AND-ROADMAP.md](../../docs/VISION-AND-ROADMAP.md)

## Privacy check

- [ ] Examples are synthetic; no patient details, chat ids, raw payloads, secrets, or private webhook URLs are included.
- [ ] Security or sensitive-data concerns are reported privately under [SECURITY.md](../../SECURITY.md), not in this public issue.
