# Embednet OS coordination

Last reviewed: 2026-08-04

Embednet OS is the Notion map for product direction, milestones, and cross-project coordination:

- [Embednet OS](https://app.notion.com/p/3a0f6d55a67381d89970e238979f201b)
- [BaleMed project](https://app.notion.com/p/3a0f6d55a67381c3b4c2ed6e70c3216f)
- [BaleMedPrices project](https://app.notion.com/p/3a0f6d55a6738159a418c8c365bed618)

## Source-of-truth rules

- This repository owns BaleMed code, safety boundaries, ADRs, and operational documentation.
- Notion owns portfolio direction, goals, milestones, and the machine-specific workspace map.
- GitHub Issues owns small actionable engineering work.
- YouTrack is newly installed with demo content only. It is not a project source of truth and nothing should be imported from it.

## Project boundary

BaleMed is the safe pharmacy intake and pharmacist-review bot. Bale-Med-Prices is the separate medicine price, authenticity, drug-information, and rare-drug product.

Keep zero code coupling between them: separate repositories, tokens, webhooks, services, and deployment decisions. Shared context belongs in Notion or explicit ADR links, not shared runtime code.

## Sync rule

When a durable technical fact changes, update the repository document first and then update the linked Notion project page. When a portfolio priority or milestone changes, update Notion and link the related GitHub issue or repository document.
