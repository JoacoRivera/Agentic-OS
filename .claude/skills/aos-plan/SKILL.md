---
name: aos-plan
description: "Plan an Agentic OS task without editing: classify the mode, load needed memory context, run the pre-task contract, and produce a concise implementation-ready plan with verification and risk expectations."
---

# Agentic OS Plan

Use this skill when the user wants to plan, scope, or prepare a change before
editing. It wraps the existing Agentic OS contracts so the user does not have to
remember the long prompt.

## Canonical contracts

This skill is an orchestrator over existing contracts; it does not replace them.
Read only the sections needed for the task:

- `AGENTS.md`
- `wiki/workflows/task-modes.md`
- `wiki/workflows/guardrail-hooks.md`
- `wiki/workflows/verification.md`
- `wiki/workflows/manual-operations.md`
- `skills/aos-query-memory/SKILL.md`
- `skills/aos-task-mode/SKILL.md`
- `skills/aos-hook/SKILL.md`

If anything conflicts, `AGENTS.md` wins, then the workflow page, then this skill.

## Rules

- **Do not edit files.** This skill plans only.
- Use the `/aos-task-mode` contract internally: classify the task, state the matched
  rule, and escalate to `production-change` when the contract says so.
- Use `/aos-query-memory` when the task likely depends on existing project/workflow
  memory. If memory is unnecessary, say why.
- Run the `pre-task` checks internally. Do not print a PASS block; print only
  WARN/BLOCK findings.
- Identify whether implementation would require `pre-edit`, `post-edit`, AI code
  review, `pre-memory-update`, or `pre-commit`.
- Do not claim code, tests, links, or memory grounding were verified unless they
  were actually inspected during this planning run.

## Workflow

1. Read `AGENTS.md`.
2. Classify the task with `task-modes.md` / `/aos-task-mode`.
3. Load relevant memory with the `/aos-query-memory` procedure when useful:
   `wiki/index.md` first, then specific pages, then `wiki/log.md` if chronology
   matters.
4. Run the `pre-task` guardrail checks against the actual request.
5. Produce an implementation-ready plan.

## Output format

```markdown
Mode: <mode>
Goal: <one line>
Scope: <in scope / out of scope>

Context loaded:
- <wiki pages or "none needed">

Plan:
- <step>

Expected checks during implementation:
- <hooks / AI review / verification bar>

WARN/BLOCK:
- <only warnings or blockers; omit section if none>

Verification performed:
- <sources actually read in this planning run>

Verification recommended:
- Run `/aos-implement` to execute the plan.
```
