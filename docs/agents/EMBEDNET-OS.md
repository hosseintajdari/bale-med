# Embednet OS coordination

Last reviewed: 2026-09-06

Embednet OS is the Notion map for product direction, milestones, and cross-project coordination:

- [Embednet OS](https://app.notion.com/p/3a0f6d55a67381d89970e238979f201b)
- [BaleMed project](https://app.notion.com/p/3a0f6d55a67381c3b4c2ed6e70c3216f)
- [BaleMedPrices project](https://app.notion.com/p/3a0f6d55a6738159a418c8c365bed618)

## Recovery source-of-truth rules

- This repository owns BaleMed code, safety boundaries, ADRs, and operational documentation.
- GitHub Issues owns small actionable engineering work.
- Embednet OS in Notion remains the portfolio, PKM, goals, milestones, and
  machine-workspace map. It has not been reviewed recently, so it is context,
  not current execution evidence, during this recovery.
- Until the owner reviews and refreshes Notion, precedence is: explicit current
  owner instruction, then verified GitHub repository state and issues, then
  existing Notion content. This is a temporary recovery rule, not a replacement
  for Embednet OS.
- YouTrack is newly installed with demo content only. It is not a project source of truth and nothing should be imported from it.

## Project boundary

BaleMed is the safe pharmacy intake and pharmacist-review bot. Bale-Med-Prices is the separate medicine price, authenticity, drug-information, and rare-drug product.

Keep zero code coupling between them: separate repositories, tokens, webhooks, services, and deployment decisions. Shared context belongs in Notion or explicit ADR links, not shared runtime code.

## Sync rule

When a durable technical fact changes, update the repository document first and then update the linked Notion project page. When a portfolio priority or milestone changes, update Notion and link the related GitHub issue or repository document.

During recovery, use outcome gates rather than delivery dates. Each project
reports its current P0, P1, or P2 gate, one next outcome, evidence, and blocker.
Historical dates may remain only when they identify already-recorded evidence;
they must not imply a current deadline.

## Notion-ready recovery update

- **Title:** Portfolio recovery — GitHub-first execution status
- **Summary:** GitHub is the temporary operational source of truth while the
  linked Notion pages are reviewed. BaleMed remains an independent,
  pharmacist-centered intake workflow; no live-LLM, deployment, token, webhook,
  or runtime change is authorized by this documentation update.
- **Current gate:** P2 owner review. The existing shadow-mode safety boundary
  remains in force.
