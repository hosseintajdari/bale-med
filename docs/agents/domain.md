# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- `CONTEXT.md` at the repo root, if it exists
- `docs/adr/`, if it exists

If these files or folders do not exist, proceed silently. Do not treat their absence as an error.

## File structure

This repo is configured as a single-context repo. When domain docs are added later, the expected shape is:

```text
/
|-- CONTEXT.md
|-- docs/
|   |-- adr/
|-- app/
|-- tests/
```

## Use the glossary's vocabulary

When a skill names a domain concept, prefer the term defined in `CONTEXT.md`.

## Flag ADR conflicts

If an output contradicts an existing ADR, call that out explicitly instead of silently overriding it.
