---
name: aos-pre-commit
description: Walk the pre-commit checklist (git status/diff, scope, review, index/log, skill mirror sync, lint, strays) and report the hook result block. Report-only assistant — it never blocks, stages, unstages, or commits; the commit decision stays with the user.
---

# Pre-Commit Skill

Use this skill before a commit to walk the `pre-commit` guardrail checklist and
produce its hook-result block. It is a **report-only assistant**: it inspects
and reports (`PASS` / `WARN` / `BLOCK` as a *verdict in text*), but it never
mechanically prevents anything — no git hooks, no staging changes, no commit.
The standing rule stays: commits are deliberate and user-driven.

## Canonical contract

The checklist and severities live in
`wiki/workflows/guardrail-hooks.md`
§F `pre-commit`, operationalized in
`wiki/workflows/manual-operations.md`
§Pre-commit process — those pages win on any conflict with this skill.
`AGENTS.md` wins over both.

## Rules

- **Advisory only.** A `BLOCK` verdict is a report the user acts on, not a
  mechanical stop. Never run `git commit`, `git add`, `git reset`, or modify
  any file.
- Allowed commands: read-only git (`git status`, `git diff`, `git diff --stat`,
  `git log`), `python3 scripts/sync-skills.py --check`, and
  `python3 scripts/wiki-lint.py` (itself report-only).
- Run `python3 scripts/sync-skills.py --check` when `skills/`, `.claude/skills/`,
  or `plugins/agentic-os/skills/` changed. Treat drift as a `block` finding because
  the derived Claude/Codex skill surfaces would not match the canonical source.
- Run the deterministic lint **only when** a wiki page, capture, or the log
  changed; otherwise note it as not applicable. Never claim the lint (or the
  judgment `/aos-wiki-lint` pass) ran when it did not.
- The verdict rolls up as the most severe check: any `block` → `BLOCK`, else
  any `warn` → `WARN`, else `PASS`.

## Workflow

1. `git status` and `git diff` (plus `--stat`) — read the actual change.
2. Walk the checks: scope match, no unresolved AI-code-review `block` (and a
   required review actually performed for code/config/script changes),
   index/log updated for wiki changes, skill mirror sync checked if applicable,
   deterministic lint run if applicable, no temp/generated/stray files, verification block present (warn if the
   *recommended* half is missing), commit message (if proposed) matches scope.
3. Emit the hook block below. On `BLOCK`, state exactly what to fix and offer
   to re-walk after the user fixes it.

## Output format

```
Hook: pre-commit
Result: PASS | WARN | BLOCK
Mode: <task mode this commit belongs to>
Checks:
- <check> — pass/warn/block
Issues:
- <what failed or is at risk>  (omit if none)
Action:
- <stop and fix | proceed and record risk | none>
```

## Related

- `skills/aos-hook/SKILL.md` — the generic runner for any lifecycle hook;
  this skill is the specialized `pre-commit` walk.
- `skills/aos-wiki-lint/SKILL.md` — the full lint (deterministic +
  judgment) this checklist may invoke.
