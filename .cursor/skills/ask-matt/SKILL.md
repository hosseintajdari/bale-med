---
name: ask-matt
description: Ask which skill or flow fits your situation. A router over the user-invoked skills in this repo.
disable-model-invocation: true
---

# Ask Matt

You do not remember every skill, so ask.

This repo keeps a **lean** skill set for BaleMed (pharmacy bot, Python, VPS deploy). Pick the closest path below.

## Main flows

| Situation | Start here |
|-----------|------------|
| New idea, milestone, or design change | `/grilling` (+ `domain-modeling` for CONTEXT.md) |
| Bug, failing test, or slow behavior | `diagnosing-bugs` |
| Build or fix with tests first | `tdd` or `/tdd` |
| Incoming GitHub issue or external PR | `/triage` |
| Break a plan into GitHub issues | `/to-issues` |
| Merge or rebase conflict | `resolving-merge-conflicts` |
| Module design, seams, testability | `codebase-design` |

## BaleMed defaults

- **Safety first** — never bypass `docs/SAFETY_RULES.md`.
- **Milestone focus** — stay inside `AGENTS.md` scope unless the user changes goal.
- **Deploy** — keep `BALE_ENABLE_SENDING=false` until explicit owner approval (8J).

## User-invoked vs model-invoked

| Type | How to run | Skills in this repo |
|------|------------|---------------------|
| User-invoked | Type `/name` in Agent chat | `/ask-matt`, `/grilling`, `/triage`, `/to-issues` |
| Model-invoked | Agent may auto-apply when relevant | `tdd`, `diagnosing-bugs`, `domain-modeling`, `codebase-design`, `resolving-merge-conflicts` |

## Setup

See `docs/agents/GETTING-STARTED.md`.
