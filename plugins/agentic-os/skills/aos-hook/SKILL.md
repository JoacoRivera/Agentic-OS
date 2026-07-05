---
name: aos-hook
description: Manually run one guardrail lifecycle hook (pre-task, pre-edit, post-edit, pre-memory-update, pre-eval-result, pre-commit) against the current state and produce its result block. Report-only assistant — it reports PASS/WARN/BLOCK, it never enforces or edits.
---

# Hook Skill

Use this skill to run **one named guardrail hook by hand** at its lifecycle
boundary and produce the standard hook-result block. It is a **report-only
assistant**: the hook contract stays a manual checklist; this skill just walks
it consistently and writes the block. Nothing is mechanically prevented.

Invocation: `/aos-hook <point>` where `<point>` is one of `pre-task`, `pre-edit`,
`post-edit`, `pre-memory-update`, `pre-eval-result`, `pre-commit`. Without an
argument, ask which boundary the work is at (or infer it and say so).

## Canonical contract

The six hook points, their checks, the severity model (`block`/`warn`/`note`),
the output block, the mode→hook matrix, and the bypass rules live in
`wiki/workflows/guardrail-hooks.md`
— that page wins on any conflict with this skill. `AGENTS.md` wins over both.

## Rules

- **Do not edit any file.** Inspection only: read-only git commands, reading
  repo files, and (for `pre-commit`) `python3 scripts/wiki-lint.py`.
- Evaluate every check of the chosen point against the **actual current
  state** (the real diff, the real conversation facts) — not against the
  work's own summary of itself. A summary-vs-diff mismatch is itself a finding.
- Severities are fixed by the contract, not re-judged: e.g. a fabricated test
  claim is always `block`; a missing optional `/aos-wiki-lint` before a docs
  commit is `warn`.
- The overall Result is the most severe check: any `block` → `BLOCK`, else any
  `warn` → `WARN`, else `PASS`.
- A `BLOCK` is a report: state what to fix; the bypass rules (explicit,
  on-the-record user approval) are the user's to invoke, never this skill's.

## Workflow

1. Read the chosen point's section in
   `wiki/workflows/guardrail-hooks.md`.
2. Gather the evidence that point needs (diff, changed-file list, the memory
   draft, the eval case + output — whatever the checks reference).
3. Walk each check, assign pass/warn/block per the contract.
4. Emit the block below.

## Output format

```
Hook: <pre-task | pre-edit | post-edit | pre-memory-update | pre-eval-result | pre-commit>
Result: PASS | WARN | BLOCK
Mode: <task mode this applies under>
Checks:
- <check> — pass/warn/block
Issues:
- <what failed or is at risk>  (omit if none)
Action:
- <stop and fix | proceed and record risk | none>
```

## Related

- `skills/aos-pre-commit/SKILL.md` — the specialized walk for the
  `pre-commit` point (richer git workflow); `/aos-hook pre-commit` defers to it.
- `skills/aos-verify-block/SKILL.md` — drafts the verification block the
  `post-edit` / `pre-memory-update` checks require.
