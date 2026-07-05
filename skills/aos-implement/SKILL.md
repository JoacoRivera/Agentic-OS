---
name: aos-implement
description: "Implement an Agentic OS change end-to-end: classify mode, load memory context, apply the required hooks and verification internally, edit files, review the diff, and close with risks plus recommended pre-commit and capture steps."
---

# Agentic OS Implement

Use this skill when the user asks to implement, fix, update, or edit code/docs in
the Agentic OS workflow. It replaces the long "remember the whole harness"
prompt: the agent must apply the existing contracts internally and only surface
material WARN/BLOCK findings.

## Canonical contracts

This skill orchestrates existing skills and workflow pages; it is not a new
policy source. Read only the sections needed for the task:

- `AGENTS.md`
- `wiki/workflows/task-modes.md`
- `wiki/workflows/guardrail-hooks.md`
- `wiki/workflows/verification.md`
- `wiki/workflows/ai-code-review.md`
- `wiki/workflows/manual-operations.md`
- `skills/aos-query-memory/SKILL.md`
- `skills/aos-task-mode/SKILL.md`
- `skills/aos-hook/SKILL.md`
- `skills/aos-verify-block/SKILL.md`

If anything conflicts, `AGENTS.md` wins, then the workflow page, then this skill.

## Rules

- **This skill edits files.** If the user wants no edits, use `/aos-plan`.
- Classify the task mode internally using `/aos-task-mode`. State the mode in the
  final response; do not require the user to provide it.
- Load relevant memory using the `/aos-query-memory` procedure when project/workflow
  context could affect the implementation. Skip only when genuinely irrelevant,
  and say so.
- Apply required hooks internally:
  - `pre-task` for non-trivial work.
  - `pre-edit` before edits.
  - `post-edit` after edits.
  - `pre-memory-update` if writing memory.
- Do not print trivial PASS hook blocks. Surface only WARN/BLOCK findings and the
  action taken.
- Use `/aos-verify-block` internally for the final verification split. Performed
  means commands/files/sources actually run or read in this session.
- For code/config/script changes under `implementation`, `hotfix`, or
  `production-change`, run the AI code review checklist from
  `wiki/workflows/ai-code-review.md` before finalizing.
- Never run `git commit`, `git add`, `git reset`, or destructive commands.
- End by recommending `/aos-pre-commit` before any commit and
  `/aos-capture-approved-example` if the result should become memory.

## Workflow

1. Read `AGENTS.md`.
2. Classify mode and expected output fields with `task-modes.md` / `/aos-task-mode`.
3. Load relevant context with the `/aos-query-memory` procedure when useful.
4. Run `pre-task` internally; stop or ask if a BLOCK requires user input.
5. Identify intended files/directories and run `pre-edit` internally.
6. Implement the change, keeping scope narrow.
7. Inspect the actual changed-file list and diff.
8. Run `post-edit` internally and AI code review if required.
9. Run relevant tests/lint/build when feasible; if not run, list them under
   recommended verification.
10. Finalize with the output below.

## Output format

```markdown
Mode: <mode>
Goal: <one line>
Changes made:
- <files and concise summary>

WARN/BLOCK:
- <only material warnings/blockers surfaced by hooks/review; omit if none>

Verification performed:
- <command/check/source actually used> — <observed result>

Verification recommended:
- Run `/aos-pre-commit` before committing.
- Run `/aos-capture-approved-example` if this result should be preserved as memory.
- <tests/build/manual checks not run yet>

Risks / assumptions:
- <risk or "none identified">
```
