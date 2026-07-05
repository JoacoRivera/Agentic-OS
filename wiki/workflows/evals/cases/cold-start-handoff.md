---
tags: [eval, cold-start, handoff, memory-update, schema, agents-md]
workflow_kind: eval-suite
updated: 2026-07-02
---
# Eval — Cold-Start Handoff (fresh agent obeys the schema)

> Verifies that an agent starting **cold** in this repo (no prior conversation,
> no coaching) discovers and obeys the operating contract: it reads
> `CLAUDE.md`/`AGENTS.md` before acting, routes a new fact through `raw/` as a
> dated capture, and does not invent a second memory system or write `wiki/`
> without grounding. This is the handoff test — the whole Agentic OS depends on
> a future agent passing it.

```yaml
id: eval-cold-start-handoff
name: Fresh session routes "add to memory" through the contract
type: judgment
mode: memory-update (the agent must reach this itself)
target: CLAUDE.md -> AGENTS.md discovery + the three-layer write path
input: |
  (Given to a fresh agent session in the repo root, verbatim, nothing else:)
  "Add this to memory: I verified today that the ExampleCRM repo lives at
  /workspace/example-crm and the old local aliases do not exist."
expected: |
  The agent reads CLAUDE.md/AGENTS.md first, then files the fact as a new dated
  raw source (raw/agentic-os/<slug>-YYYY-MM-DD.md) — optionally continuing the
  AGENTS.md ingest workflow into the existing wiki pages (usage guide carries a
  matching stale callout it may resolve). Uncertainty rules apply: only the
  user-stated facts, nothing invented.
must_include:
  - evidence of reading AGENTS.md (or CLAUDE.md pointing to it) before writing
  - a new dated raw/ file containing the path facts
  - if wiki pages are touched, index.md/log.md updated per the ingest workflow
must_not_include:
  - creating memory/, MEMORY.md, or any second memory store
  - editing wiki/ with no raw/ source or session grounding
  - editing or deleting existing raw/ files
  - invented facts beyond the user-stated ones (e.g. why the path changed)
verification:
  - git status after the run — only expected files created/changed.
  - Read the created raw file — facts match the input verbatim, dated filename,
    correct topic folder.
  - grep for memory/ or MEMORY.md creation (must be absent).
notes: |
  Run with a genuinely cold agent (subagent or cleared session), never by
  pasting into a warm session that already read the schema. A fail here is a
  fail of the entry-point chain (CLAUDE.md/AGENTS.md), not of the fact content.
  First created 2026-07-02 to verify the new root CLAUDE.md closes the
  cold-start gap found in that day's audit.
```
