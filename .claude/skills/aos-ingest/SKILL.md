---
name: aos-ingest
description: Ingest one or more raw source files from raw/ into the LLM wiki. Use when the user asks to ingest raw notes, project snapshots, workflow notes, or source material into wiki/.
---

# Ingest Raw Source Into Wiki

Use this skill to ingest one or more files from `raw/` into the LLM-maintained `wiki/`.

The user will provide one or more raw file paths as arguments.

Arguments:

$ARGUMENTS

## Required reading

Before making changes, read:

- `AGENTS.md`
- `wiki/index.md`
- `wiki/log.md`

This file is the canonical ingest procedure. If anything here conflicts with `AGENTS.md`, follow `AGENTS.md`.

## Procedure

1. Read `AGENTS.md`.
2. Read `wiki/index.md`.
3. Read `wiki/log.md`.
4. Read the provided raw source file or files.
5. Identify:
   - durable facts
   - decisions
   - conventions
   - workflows
   - TODOs
   - open questions
   - contradictions with existing wiki pages
6. Find the most relevant existing wiki pages.
7. Create or update `wiki/` pages as needed.
8. Add or update wiki page frontmatter:
   - `tags`
   - `source`
   - `updated`
9. Update `wiki/index.md` if pages were added, renamed, recategorized, or materially changed.
10. Prepend one `ingest` entry to `wiki/log.md`.

## Rules

- Do not edit files in `raw/`.
- Do not invent missing commands, paths, dates, owners, or implementation details.
- Preserve TODOs as open questions unless the source clearly resolves them.
- Preserve uncertainty explicitly.
- Prefer updating existing wiki pages over creating duplicates.
- Create a new page only for durable projects, systems, workflows, concepts, entities, or syntheses.
- Keep the wiki minimal and navigable.
- Do not perform unrelated cleanup.
- Do not store secrets, passwords, API keys, private keys, tokens, or production credentials.
- If a new source contradicts existing wiki content, flag the contradiction explicitly instead of silently overwriting.
- Follow the `wiki/log.md` convention from `AGENTS.md`: new log entries go at the top.

## Raw-dump drift control

When updating an existing wiki page, check whether the new content would turn the page into a near-copy of the raw source.

If the page is already dense:

- Add only synthesized deltas.
- Prefer "known patterns", "important files/classes", "risks", "open questions", and "links to raw sources".
- Avoid exhaustive field/class enumeration unless it is the actual reusable memory.
- If new material belongs to a distinct topic, create a child wiki page and link it from the parent.

See the "Dense wiki pages" section in `AGENTS.md` for the canonical rule.

## Final response

After ingesting, report:

- Raw files ingested
- Wiki pages created
- Wiki pages updated
- Index changes
- Log entry added
- Open questions preserved
- Contradictions found
- Recommended next action