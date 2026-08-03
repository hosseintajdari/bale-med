# Junie project guidance

Read and follow the repository `AGENTS.md` before planning or making changes. It is the
authoritative source for pharmacy-safety boundaries, scope, verification commands, and
commit rules.

## Working style

- Keep each task narrow and explain the intended change before broad refactoring.
- Prefer small, reviewable edits and preserve unrelated working-tree changes.
- Use `unittest` for tests. Run the relevant verification commands from `AGENTS.md` after changes.
- Never expose secrets or commit `.env`, database, log, or tunnel-output files.

## Safety boundary

- Do not add diagnosis, dosage, prescription replacement, or medication-change advice.
- Keep LLM behavior in shadow mode unless the pharmacy owner has explicitly approved live mode.
- Ask before deployments, external communication, or changes outside this repository.
