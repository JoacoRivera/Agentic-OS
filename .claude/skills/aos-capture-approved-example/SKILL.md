---
name: aos-capture-approved-example
description: Capture an approved agent result into raw/ as source material for the Agentic OS memory wiki. Use after the user approves a coding, investigation, SQL, or communication example.
---

# Capture Approved Example Skill

Use this skill when the user says that a result, investigation, code change, SQL workflow, or message is approved and should be captured as memory.

This is the **capture half** of the memory loop. It writes a single raw source
file. The downstream `/aos-ingest` skill (in the Agentic OS repo) later promotes
durable facts from that raw file into `wiki/`.

## Goal

Create a concise raw source file under `raw/` that preserves the approved example without dumping unnecessary transcript noise.

## Rules

- Do not edit `wiki/` directly.
- Do not modify existing `raw/` files.
- Create a new source file under the appropriate `raw/` path.
- Preserve facts exactly.
- Do not invent missing dates, owners, paths, files, or verification results.
- Preserve missing details as open questions.
- Do not promote single-example lessons into general rules.
- The created raw file should be suitable for `/aos-ingest`.
- **Never run `/aos-ingest` yourself.** Ingestion is always a manual, user-driven
  step. After capturing, always prompt the user to run `/aos-ingest` on the new raw
  file themselves — do not promote it into `wiki/` automatically.

## Paths

All `raw/` paths are relative to the Agentic OS memory root: `~/agents/agentic-os`.
Write the file there, **not** into the code repo you are working in.

The general shape is:

`~/agents/agentic-os/raw/<projects|workflows>/<project-or-workflow-slug>/examples/`

### Known destinations

- **Project engineering examples** →
  `raw/projects/<project>/examples/`
- **Workflow examples** →
  `raw/workflows/<workflow>/examples/`

### Choosing the destination

1. If the example clearly belongs to one of the **Known destinations** above
   (e.g. you are in a project repo or capturing a workflow example), use it.
2. Otherwise, try to infer the project/workflow slug from context — the current
   repo, the task, an existing `raw/projects/*` or `raw/workflows/*` folder that
   obviously matches.
3. **If you cannot infer the destination with 100% certainty, stop and ask the
   user** for the exact `raw/` path (the project or workflow slug). Do not guess
   a new folder name, and do not fall back to an unrelated project path.

When in doubt, list the existing `raw/projects/` and `raw/workflows/` folders and
ask the user which one to use (or whether to create a new slug, and what to name
it).

If the chosen `examples/` directory does not exist, create it before writing —
but only once the destination is confirmed.

## File naming

Use lowercase kebab-case:

`<topic>-<example-type>-YYYY-MM-DD.md`

Examples:

- `drgt-player-sync-investigation-2026-06-27.md`
- `sok-visit-counter-sql-verification-2026-06-27.md`
- `ticket-25040-status-message-2026-06-27.md`

Use today's date. If a file with the same name already exists, do not overwrite
it — append a short disambiguating suffix (e.g. `-2`).

## Output file structure

Every capture carries a `Status:` line in its header block set to `Draft`. This
is the signal the Obsidian Dashboard uses to surface captures still needing
review: `Status: Approved` means reviewed and ready to `/aos-ingest`; `Status: Draft`
(or no marker) counts as a draft. **Always write `Status: Draft`** — the flip to
`Approved` happens at triage, either by the user or by `/aos-promote-draft-memory`
under the delegated approval policy (see `AGENTS.md`). Never set `Approved`
from this skill.

For engineering examples, include:

```markdown
# <Title>

Date:
Example type:
Project:
Source:
Status: Draft
Approved by:

## Task

## Context

## Skills/workflows used

## Investigation summary

## Change made

## Verification

## Final response pattern

## Reusable lesson

## Do not generalize

## Open questions
```

For workflow examples, keep the same `Status: Draft` header line and header
block (`Date:`, `Example type:`, `Project:`, `Source:`, `Approved by:`) and adapt
the body sections to:

```markdown
# <Title>

Date:
Example type:
Project:
Source:
Status: Draft
Approved by:

## Task

## Context

## Skills/workflows used

## Original request / situation

## Approved message

## Tone and structure notes

## Reusable lesson

## Do not generalize

## Open questions
```

## Steps

1. Confirm with the user **what** is being captured and that it is approved.
2. Decide project example vs. workflow example and pick the matching `raw/` path.
3. Fill the header block — leave any unknown field blank and record it under
   **Open questions** rather than guessing. Always write `Status: Draft` in the
   header block; never set `Approved`.
4. Summarize the example into the body sections. Keep it concise: preserve the
   facts, decisions, and the reusable pattern; drop transcript noise.
5. Write the new file under the chosen `raw/.../examples/` path.

## Final response

After writing, report:

- Raw file created (full path)
- Example type and project
- Header fields left blank / open questions preserved

Then **always prompt the user to manually ingest the file**, with the exact
command to run:

> Approved example captured. To promote it into the wiki memory, run:
> `/aos-ingest <full-path-to-raw-file>`

Do not run `/aos-ingest` yourself — wait for the user to do it.
