---
name: aos-task-mode
description: Classify a task into a Task Mode and emit the required-output skeleton for that mode. Report-only assistant — it produces the skeleton and classification, it does not perform the task or edit any file.
---

# Task Mode Skill

Use this skill at the start of a non-trivial task to (a) classify it into the
right task mode and (b) emit the mode's required-output skeleton so no field is
forgotten. It is a **report-only assistant**: the classification and skeleton
are advice; the judgment about the work itself stays with the agent/user doing
the task.

## Canonical contract

The mode definitions, the selection guide, and the required output fields live
in `wiki/workflows/task-modes.md` — that
page wins on any conflict with this skill. `AGENTS.md` wins over both.

## Rules

- **Do not edit any file.** This skill only prints.
- **Do not perform the task.** Classify + emit the skeleton, then stop.
- If a mode is passed as the argument (`/aos-task-mode implementation`), validate it
  against the seven modes and emit that mode's skeleton.
- If no mode is passed, walk the selection guide (first match top-down) against
  the user's described task and **state which rule matched**. When two modes
  fit, pick the higher-discipline one and say why.
- If the task description is too thin to classify, ask — do not guess a mode
  for high-risk work (`production-change` triggers: prod behavior, migration,
  schema, security, money/business-critical, broad architecture).

## Workflow

1. Read `wiki/workflows/task-modes.md`
   (§How to choose a mode, §Required output structure per mode).
2. Classify (or validate the passed mode).
3. Emit the output below with the mode's exact field set as an empty skeleton.
4. Note which guardrail hooks the mode requires (per the mode→hook matrix in
   `wiki/workflows/guardrail-hooks.md`) and whether
   AI code review is required.

## Output format

```markdown
## Task-mode classification

- Mode: <one of the seven>
- Matched rule: <which selection-guide line fired, or "user-specified">
- Escalation check: <needs production-change? yes/no + why>

## Required-output skeleton

Mode: <mode>
Goal:
<one line per required field of this mode, left blank to fill>

## Applies

- Guardrail hooks: <which lifecycle hooks this mode requires>
- AI code review: <required / only-if-code / no>
- Verification bar: <this mode's row from verification.md>
```

## Related

- `skills/aos-verify-block/SKILL.md` — emits the verification block the
  skeleton's verification fields point to.
- `skills/aos-hook/SKILL.md` — walks one lifecycle hook checklist.
