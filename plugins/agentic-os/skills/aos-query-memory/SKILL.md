---
name: aos-query-memory
description: Query the Agentic OS Markdown wiki for relevant long-term memory before doing work. Use when the user asks what is known about a project, workflow, decision, style, bug, domain rule, or prior example.
---

# Query Memory Skill

Use this skill to search and summarize the Agentic OS Markdown wiki.

## Scope

The memory system lives at:

```text
~/agents/agentic-os
```

Relevant locations:

```text
wiki/index.md
wiki/log.md
wiki/projects/
wiki/workflows/
```

Do not treat skills (`skills/`, or the legacy `skills/` pointer) as memory. Skills are prompt workflows, not long-term factual memory.

## Rules

- Do not edit files.
- Do not read or modify `raw/` unless the user asks for source-level traceability.
- Prefer `wiki/index.md` first to locate relevant pages.
- Use `wiki/log.md` for recent changes and chronology.
- Use specific wiki pages for actual memory content.
- Do not invent missing details.
- If memory is absent or incomplete, say so clearly.
- Distinguish confirmed memory from open questions.
- If there are contradictions, report them.
- If the user asks whether something is remembered, answer from the wiki only.

## Workflow

1. Read `wiki/index.md`.
2. Identify likely relevant wiki pages.
3. Read those pages.
4. Optionally inspect `wiki/log.md` for recent changes.
5. Summarize the relevant memory.
6. Mention missing details or open questions.
7. Suggest whether a new raw snapshot/example should be created.

## Output format

```markdown
## Memory query result

### Relevant wiki pages
-

### What memory says
-

### Open questions / missing details
-

### Conflicts
-

### Suggested next action
-
```
