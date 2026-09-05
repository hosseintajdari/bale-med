# Handoff — BaleMed (new Agent chat)

**Date:** 2026-07-19  
**Branch:** `main`  
**Milestone:** 9 — **P1 done** → **P2 owner review (accelerated)** → Ghaza Daru delivery 5 Shahrivar 1405

Copy this file into a new chat, or say: *Read `docs/agents/HANDOFF.md` and continue.*

---

## Paste this in new Agent chat

```text
Read docs/agents/HANDOFF.md.

Continue P2 shadow review. Compare LLM vs pharmacist judgment; save annotations.
Do NOT enable BALE_LLM_MODE=live without explicit owner approval.
Triage reference: docs/research/triage-referral-design-fa.md
Patterns to adopt: docs/research/triage-patterns-adoption-fa.md
Notion: https://app.notion.com/p/3a1f6d55a673815aba45fc8e3fb9713d
```

---

## Current status (2026-07-18)

### GitHub Actions repair (verified 2026-09-05)

- The retired Qodana workflow and configuration were removed.
- `validate` now uses a standard GitHub-hosted runner, pinned GitHub-owned
  actions, read-only repository permission, concurrency cancellation, and a
  manual dispatch option.
- Hosted run `33993938097` completed successfully with the repository's
  unittest, compile, and ruff checks. Earlier synthetic `BuildFailed`
  startup-failure records are historical and no longer reproduce.

| Item | Status |
|------|--------|
| P1 shadow_ok on real `@embednebot` traffic | ✅ |
| P2 code on VPS (UI, annotate API) | ✅ via scp |
| `BALE_LLM_MODE=shadow` on VPS | ✅ |
| Owner annotations saved | **4** (#20, #31, #32, #41) |
| P2 gate target | **20–50 diverse** reviewed messages |
| Triage research + ADR-0003/0004 on GitHub | ✅ 2026-07-18 |
| Notion Knowledge Reference page | ✅ [link](https://app.notion.com/p/3a1f6d55a673815aba45fc8e3fb9713d) |
| Global alignment check (NHS/WHO/Infermedica) | ✅ on standard path — see adoption doc |

**VPS deploy:** no working `git pull` — use **scp**, then `sudo systemctl restart bale-bot`.

---

## Ghaza Daru delivery (2026-07-19)

**Deadline:** 5 Shahrivar 1405 (~2026-08-27)

| Item | Rule |
|------|------|
| BaleMed role | Patient intake demo on existing VPS bot |
| Bale-Med-Prices role | Price + authenticity + drug info + rare drug |
| Coupling | **Zero** — no shared webhook, no proxy, no price logic in `handlers.py` |
| P2 gate | Still 20–50 annotations before `BALE_LLM_MODE=live` |
| ADR | [0005-ghaza-daru-delivery-boundary.md](../adr/0005-ghaza-daru-delivery-boundary.md) |
| Notion Goal | https://app.notion.com/p/3a1f6d55a673812b9137cdde5233795a |

**Accreditation demo:** evaluators message `@embednebot` directly. Working safe replies = success.

---

## Triage design (2026-07-18 session)

**We are aligned with global standards** (disposition not diagnosis, rules first, shadow before live, fixed templates).

| Doc | Purpose |
|-----|---------|
| [triage-referral-design-fa.md](../research/triage-referral-design-fa.md) | Full reference for pharmacist + agent |
| [triage-patterns-adoption-fa.md](../research/triage-patterns-adoption-fa.md) | What to adopt — no reinventing wheels |
| [ADR-0003](../adr/0003-triage-with-llm.md) | With LLM (shadow → live) |
| [ADR-0004](../adr/0004-triage-without-llm.md) | Rules-only baseline |
| [notion-import/README.md](../notion-import/README.md) | Notion publish notes |

**Main code gap (next after P2):** separate `ER_URGENT_REPLY` template for D2 red flags (today D1 and D2 share `ESCALATION_REPLY`).

**Owner principle:** paths with existing clinical/industry standards must be **implemented**, not redesigned.

---

## P2 progress — owner decisions so far

| DB id | Scenario | LLM `needs_review` | Owner: correct? |
|-------|----------|-------------------|-----------------|
| 20 | «قرص مسکن می‌خواهم» | true | **yes** |
| 31 | S01 موجودی ibuprofen | false | **yes** |
| 32 | S02 موجودی ایبوپروفن | false | **yes** |
| 41 | S11 تمدید نسخه ساده | false | **yes** |
| 21–30 | Gibberish tests | true | **skipped** |
| 33–40, 42 | S03–S10, S12 | mixed | **pending** |

### Owner workflow rules

1. **موجودی / قیمت:** `needs_review=false` — sales/promotions are future side projects.
2. **تمدید نسخه ساده:** `needs_review=false`.
3. **MVP gate:** 20–50 **diverse** messages; gibberish does not count.

### Open review items

| DB id | Issue |
|-------|-------|
| 33 (S03) | حساسیت پنی‌سیلین — `drug_name=null` |
| 42 (S12) | «سردرد شدید» — `urgent_symptoms=true` (too sensitive?) |
| 34–40 | pregnancy, pediatric, dose, etc. — pending |

---

## P2 — Commands

### Save annotation (preferred)

```bash
python3 deploy/scripts/annotate-shadow-review.py <message_id> \
  --needs-review-ok yes|no|skip \
  --drug-name-ok yes|no|skip \
  --owner-notes "short note"
```

### Web UI (laptop + SSH tunnel)

```bash
ssh -L 8000:127.0.0.1:8000 balemed
# browser: http://127.0.0.1:8000/local/shadow-reviews/ui
```

### Post more scenarios

```bash
python3 deploy/scripts/post-common-scenarios.py
```

### Live mode (ONLY after owner sign-off)

```env
BALE_LLM_MODE=live
```

---

## Next steps (priority order)

1. **P2:** Owner reviews 7+ more diverse pharmacy questions → target 20 annotated.
2. **Code:** `ER_URGENT_REPLY` for D2 (after P2 gate).
3. **CONTEXT:** D0/D1/D2 already in glossary — keep in sync with `replies.py`.
4. **Notion:** Set triage Reference Status → Stable after owner reads page.
5. **Do not** set `BALE_LLM_MODE=live` until 20–50 diverse reviews + explicit owner OK.

---

## VPS helpers

| Script | Purpose |
|--------|---------|
| `annotate-shadow-review.py` | Save one P2 annotation |
| `post-common-scenarios.py` | Post 12 loopback shadow scenarios |
| `list-shadow-reviews.py` | CLI list shadow_ok rows |
| `vps-quick-check.py` | Health + recent LLM status |
| `test-llm-provider.py` | LLM API smoke test |
| `publish-triage-notion.py` | Re-publish triage doc to Notion (optional) |

---

## Key files

| Purpose | Path |
|---------|------|
| Shadow review | `app/shadow_review.py`, `app/shadow_review_ui.py` |
| Keywords / replies | `app/replies.py` |
| LLM | `app/llm/service.py` |
| Safety | `docs/SAFETY_RULES.md` |
| Live gate ADR | `docs/adr/0002-clinical-trust-requirements-before-live-llm.md` |
| Embednet OS (Notion map) | `docs/agents/EMBEDNET-OS.md` |

**Pin chats:** P2 review (2026-07-16) + triage/Notion session (2026-07-18).
