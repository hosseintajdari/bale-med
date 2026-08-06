Embednet OS — Notion alignment update

Context
- Last reviewed: 2026-08-04. Embednet OS is the high-level Notion map for portfolio direction and machine-specific workspace maps.

Summary of proposed changes
1. Source-of-truth (SoT) clarity
   - Keep the repository as the canonical owner of code, ADRs, and operational docs.
   - Notion remains portfolio-level SoT for milestones, priorities, and cross-project links.
   - Make YouTrack a local alignment mirror for JetBrains workflows (task tracker only) — Notion remains the single human-facing source for strategy.

2. Notion structure changes (recommended)
   - Add an "Embednet OS > Alignment" page with: purpose, SoT map, GitHub↔Notion sync rules, YouTrack project mapping, and localization notes for JetBrains.
   - Under Embednet OS: a Tasks import table (exportable CSV) summarizing importable items for YouTrack.
   - Add "Skills & Roles" section listing required skills for alignment and maintenance (YouTrack admin, Notion editor, Git/GitHub maintainer, CI/CD knowledge, localization owner, data-migration skills).

3. Skills & training notes
   - YouTrack admin: project setup, issue-type config, workflows, custom fields, import CSV, REST API.
   - Notion editor: page templates, linked databases, exportable tables, page permissions.
   - Git/GitHub: merging rules, ADR maintenance, release tagging.
   - CI/CD & infra: Qodana, deployment pipelines, and environment separation (OneDrive risks).

4. Sync rules and governance (concrete)
   - Durable technical facts (code, ADRs): update repo first, then Notion.
   - Portfolio priorities: update Notion first, then create Linked GitHub issue (small actionable work) and a YouTrack ticket if local JetBrains alignment required.
   - YouTrack project is not a primary source; it is a localized alignment mirror with regular reconciliation from Notion.

5. Migration plan to seed YouTrack (high level)
   - Export a curated set of Notion pages (tasks, migration items) to CSV.
   - Clear demo data in YouTrack (backup first if needed) then import CSV.
   - Establish automation: weekly reconciliation job (script) to detect drift and surface to Notion as issues.

Next steps (ask user quick answers)
- Approve the Notion page update to be committed to docs/ and copied into Notion manually or via Notion API? (reply: "manual" or "api" )
- Approve running the YouTrack import script after I create the CSV? (reply: "run" or "hold")

Produced by: Copilot session
