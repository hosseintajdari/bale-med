# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

If a label from this table does not yet exist in GitHub, create it with `gh label create "<name>" --description "..."` before applying it.

## Categories and colors

Keep existing names; do not rename or delete labels to enforce a new taxonomy.
Colors help scanning but never carry meaning without the label text.

| Category | Existing labels | Color convention |
| --- | --- | --- |
| Area | `area: security`, `area: foundation`, `area: webhook`, `area: commands`, `area: safety`, `area: admin-review`, `area: deployment`, `area: ai` | Blue `1D76DB` |
| Priority | `priority: P1`, `priority: P2`, `priority: P3` | Red `B60205`, amber `FBCA04`, pale yellow `FEF2C0` |
| Delivery status | `status: planned`, `status: in progress`, `status: done` | Gray `CFD3D7`, yellow `FBCA04`, green `0E8A16` |
| Work kind | `type: milestone`, `architecture`, `integration`, `rfc`, `domain-gap` | Purple `5319E7` |
| Safety review | `safety-critical` | Red `B60205` |
| Triage readiness | `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix` | Gray, amber, green, green, white respectively |

Standard GitHub labels (`bug`, `documentation`, `enhancement`, `duplicate`,
`good first issue`, `help wanted`, `invalid`, `question`) retain their existing
colors and descriptions. `domain-gap` supports the clinical/safety issue form;
use `area: safety` for the affected area rather than creating a competing `safety` label.

## Human-led triage

1. New template-based issues start with `needs-triage` plus their work-kind label.
2. A maintainer checks scope, synthetic reproduction details, and safety/privacy.
   Use `needs-info` when safe information is missing. Never request patient data.
3. Use `ready-for-agent` only for bounded, specified work with acceptance criteria;
   use `ready-for-human` for work requiring human judgment or implementation.
   These are readiness states, not permission to deploy or change clinical rules.
4. Keep at most one current triage-role label and one delivery-status label when
   a maintainer updates a ticket. Area and work-kind labels may coexist.
5. Priority is engineering work order (P1 high, P2 normal, P3 low), not patient
   acuity. `safety-critical` calls for explicit human safety review, not automatic action.
6. Mark `status: done` only with verified completion evidence. `wontfix` records
   a maintainer decision and reason; applying it does not itself close a ticket.

External pull requests use the same roles. Labels and passing CI never replace
review, merge authorization, or pharmacy owner approval for real sending/live LLM.
