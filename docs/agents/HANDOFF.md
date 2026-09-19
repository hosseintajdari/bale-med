# Handoff — BaleMed

## Metadata

- **Updated:** 2026-09-20
- **Repository / branch:** `hosseintajdari/bale-med` / `main`
- **Status:** P1 shadow evidence and P2 owner review packet completed; no-live-mode boundary preserved.
- **Execution authority:** GitHub is the temporary operational source of truth
  while Embednet OS / Notion is reviewed and refreshed. See
  [`EMBEDNET-OS.md`](EMBEDNET-OS.md).

## Checkpoint

- **Verified:** Hosted GitHub Actions validation is recorded as passing in the
  repository; the former startup-failure report is historical.
- **Verified:** The LLM remains a shadow-only classification layer. The project
  is a pharmacist-centered intake workflow, not a diagnostic, prescription, or
  autonomous medication-advice service.
- **Current boundary:** Do not enable `BALE_LLM_MODE=live`, alter VPS services,
  deploy code, access private traffic, or change tokens/webhooks as part of
  documentation and coordination work.
- **Coordination:** BaleMed and Bale-Med-Prices have zero runtime coupling.
  Shared context belongs in Embednet OS or explicit linked documentation.

## Decisions and blockers

- **Decision:** Use outcome gates rather than calendar commitments. Historical
  dates remain only as evidence references and do not represent current plans.
- **Blocker:** P2 needs owner-reviewed, diverse shadow annotations before any
  live-mode decision. Existing observations do not authorize a live LLM mode.
- **Blocker:** Notion has not been recently reviewed. Repository documents are
  updated first; the concise Notion sync note in `EMBEDNET-OS.md` is ready for
  the connected Notion agent.

## Handoff

### One next outcome

P2 shadow-review work is finalized in [`docs/OWNER_SHADOW_REVIEW_PACKET.md`](../OWNER_SHADOW_REVIEW_PACKET.md):
synthetic evidence across 30 vectors, failure modes, unresolved drug lexicon dependencies,
and strict no-live-mode prerequisites are documented.

### Current gate map

- **P0 — foundation:** intake safety, duplicate handling, local recovery, and
  repository validation are established.
- **P1 — shadow operation:** classification remains internal/shadow only; no
  patient-facing LLM decision is enabled.
- **P2 — owner review:** completed; documented in `docs/OWNER_SHADOW_REVIEW_PACKET.md`.
  Live mode remains strictly gated behind fuzzy lexicon and owner sign-off.

### Completion criteria

- The P2 review packet identifies evidence, unresolved scenarios, and owner
  decisions without exposing patient content (complete in `docs/OWNER_SHADOW_REVIEW_PACKET.md`).
- Any retained Issue or Pull Request maps to one current gate and has a concise
  scope statement.
- Notion is updated from the merged repository facts when its connection is
  available; learning entries remain title plus short summary.

## History pointers

- [`docs/OWNER_SHADOW_REVIEW_PACKET.md`](../OWNER_SHADOW_REVIEW_PACKET.md)
- [`docs/adr/0002-clinical-trust-requirements-before-live-llm.md`](../adr/0002-clinical-trust-requirements-before-live-llm.md)
- [`docs/adr/0005-ghaza-daru-delivery-boundary.md`](../adr/0005-ghaza-daru-delivery-boundary.md)
- [`docs/agents/EMBEDNET-OS.md`](EMBEDNET-OS.md)
- GitHub Issue #46 for the retained P2 review work.
