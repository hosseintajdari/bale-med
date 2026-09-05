# Handoff — BaleMed

## Metadata

- **Updated:** 2026-09-06
- **Repository / branch:** `hosseintajdari/bale-med` / `main`
- **Status:** P1 shadow evidence is recorded; P2 owner review remains open.
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

Turn the retained P2 shadow-review work into a clear owner-review packet: known
evidence, remaining diverse annotations, and the explicit no-live-mode gate.

### Current gate map

- **P0 — foundation:** intake safety, duplicate handling, local recovery, and
  repository validation are established.
- **P1 — shadow operation:** classification remains internal/shadow only; no
  patient-facing LLM decision is enabled.
- **P2 — owner review:** assess diverse shadow evidence, then decide whether a
  separately authorized live-mode proposal is warranted.

### Completion criteria

- The P2 review packet identifies evidence, unresolved scenarios, and owner
  decisions without exposing patient content.
- Any retained Issue or Pull Request maps to one current gate and has a concise
  scope statement.
- Notion is updated from the merged repository facts when its connection is
  available; learning entries remain title plus short summary.

## History pointers

- [`docs/adr/0002-clinical-trust-requirements-before-live-llm.md`](../adr/0002-clinical-trust-requirements-before-live-llm.md)
- [`docs/adr/0005-ghaza-daru-delivery-boundary.md`](../adr/0005-ghaza-daru-delivery-boundary.md)
- [`docs/agents/EMBEDNET-OS.md`](EMBEDNET-OS.md)
- GitHub Issue #46 for the retained P2 review work.
