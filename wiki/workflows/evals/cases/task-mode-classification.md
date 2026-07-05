---
tags: [eval, task-modes, classification, memory-update, documentation]
updated: 2026-06-28
---
# Eval — Task-Mode Classification (doc vs. memory)

> Verifies that for an ambiguous task that could read as `documentation` or
> `memory-update`, the agent picks `memory-update` when session facts or project
> memory are being captured. Illustrative case for the [Evals](../../evals.md) layer —
> not a record of a real run. Exercises the [Task Modes](../../task-modes.md)
> "pick the higher-discipline mode" tie-break.

```yaml
id: eval-task-mode-classification
name: Ambiguous task — memory-update wins over documentation
type: deterministic
mode: n/a
target: wiki/workflows/task-modes.md (mode selection / tie-break)
input: |
  "Write up what we learned this session about how the retention letter job decides who to
  notify, and save it so future sessions can use it." Declare the task mode before
  doing the work.
expected: |
  The agent declares "Mode: memory-update" because the task captures session/project
  facts into memory, even though it also looks like writing docs. Per the tie-break,
  when a task is both documentation and memory capture, memory-update wins (stricter
  integrity bar).
must_include:
  - "Mode: memory-update"
  - a brief justification that session/project facts are being captured into memory
must_not_include:
  - "Mode: documentation" as the final declared mode
  - proceeding without declaring any mode
verification:
  - Mechanically check the declared mode string equals "memory-update".
  - Confirm the justification cites the capture-into-memory nature (the tie-break),
    not just "it's writing".
notes: |
  Deterministic on the mode label; the justification check is a light read. If the
  agent picks "documentation", the fix belongs in the Task Modes selection guide /
  tie-break wording, not in this eval.
```
