---
name: git-github-scope
description: Boundaries for git commit, push, PR, and GitHub ops vs local Windows workspace vs VPS/web. Use when the user mentions commit, push, PR, babysit PR, GitHub, merge, handoff to GitHub, SSH tunnel, or when the agent is about to git rm/delete files for PR scope cleanup.
---

# Git and GitHub scope boundaries (BaleMed)

## Three environments — never treat as one

| Layer | Where | Purpose | Typical paths / tools |
|-------|--------|---------|------------------------|
| **Windows (local IDE)** | Laptop + Cursor | Fast chat, RTL CSS, rules/skills, drafts | `cursor-rtl.css`, `.cursor/`, local `.env` |
| **Web / phone (runtime)** | VPS + Bale + browser/SSH tunnel | Bot traffic, shadow review UI, SQLite on server | `ssh -L 8000:127.0.0.1:8000 balemed`, `/local/shadow-reviews/ui`, `@embednebot` |
| **GitHub (source of truth)** | Remote repo | App code, tests, deploy docs — merge → deploy | `app/`, `tests/`, `docs/agents/`, `deploy/` |

**Conflict rule:** A change in one layer does not automatically belong in the others. Ask or split work.

Examples:
- Fix Persian in **Windows** `cursor-rtl.css` → local only; **do not** delete or push unless asked.
- P2 review on **web** → use VPS tunnel + `/local/shadow-reviews/ui`; data lives in **server** SQLite.
- **GitHub** PR → only project files for the stated milestone task.

## Default: no Git unless explicit

- **No commit** unless the user explicitly asks.
- **No push** unless the user explicitly asks.
- **No PR create/merge** unless explicitly asked.
- **No `git rm` / delete** to "narrow PR scope" unless the user explicitly lists those paths.

Report scope problems; ask before deleting.

## Windows (local IDE) — hands off in GitHub work

**Do not delete, move, or strip from disk** unless the user explicitly asks:

- `cursor-rtl.css` and other Cursor UI/CSS helpers
- `.cursor/mcp.json`, `.cursor/settings.json`, `.cursor/rules/`, `.cursor/skills/` (project skills that are IDE workflow)
- Local drafts not meant for GitHub

If these appear in a PR diff, **mention** — do not auto-delete locally to fix the PR. Prefer removing them from the **GitHub branch** with `git rm --cached` so local copies stay.

## Web / phone (VPS runtime)

- Shadow P2 UI: `GET /local/shadow-reviews`, `GET /local/shadow-reviews/ui`, `POST /local/shadow-reviews/{id}/annotate` — **localhost on VPS only** (Caddy blocks public `/local/*`).
- Access from laptop: `ssh -L 8000:127.0.0.1:8000 balemed` then browser `http://127.0.0.1:8000/local/shadow-reviews/ui`.
- Bale bot testing = real messages on phone; data lands in **VPS** DB, not Windows SQLite.
- Do not assume Windows local run equals VPS behavior.

## GitHub / PR — minimal project diff only

When commit/push/PR **is** explicitly requested, stage **only** milestone project files, e.g. P2:

- `app/database.py`, `app/main.py`, `app/shadow_review.py`, `app/shadow_review_ui.py`
- `tests/test_shadow_review.py`
- `docs/agents/HANDOFF.md`

**Exclude by default:** `.cursor/*`, `cursor-rtl.css`, blog drafts, unrelated docs from other chats.

**Babysit PR:** fix in-scope code and comments only. No "scope cleanup" by deleting Windows IDE files.

## PR babysit — safe behavior

- Unresolved review comments only.
- Fix CI only when this PR's code caused the failure.
- Do not modify CI workflows to green unrelated failures.
- Repo-wide CI `startup_failure` → report; do not delete local files.

## User phrases (Persian / English)

| User says | Meaning |
|-----------|---------|
| "درست کن" / quick fix | **Windows** workspace only |
| "آپلود نکن" / local only | No GitHub remote ops |
| "handoff / بفرست گیت‌هاب" | GitHub commit/push/PR in scope (minimal diff) |
| Test on phone / VPS | **Web** runtime, not local commit |

## Checklist before any git write

- [ ] Explicit commit/push/PR request?
- [ ] Staged files = project scope only (not Windows IDE tooling)?
- [ ] Not deleting `cursor-rtl.css` or `.cursor/` locally?
- [ ] PR scope cleanup uses `git rm --cached` + ask, not disk delete?
