---
name: aos-verify-block
description: Emit the canonical verification block (performed vs. recommended) for the current work, pre-filled only with checks that actually ran. Report-only assistant — it drafts the block, it never invents a performed check and never edits files.
---

# Verify Block Skill

Use this skill after doing work, when the result owes the honesty split: emit
the canonical **verification performed vs. recommended** block. It is a
**report-only assistant**: it drafts the block from what actually happened in
the session; it must never upgrade an unrun check into "performed".

## Canonical contract

The block format, the compact one-liner, the forbidden-claims list, and the
per-mode verification bar live in
`wiki/workflows/verification.md` —
that page wins on any conflict with this skill. `AGENTS.md` wins over both.

## Rules

- **Do not edit any file.** This skill only prints the block for the user/agent
  to paste into the result.
- **Performed = actually ran/read in this session, with the observed result.**
  If you cannot point to the command/file/output in this conversation, it goes
  under *recommended*. When nothing was verified, write "None run in this
  environment." under performed — an empty performed is honest; a fabricated
  one is a `block`-level failure.
- **Never use the forbidden phrasings** ("tests should pass", "looks fine",
  "probably passes") — either state the check + observed result, or list it as
  recommended.
- Pick full vs. compact form by mode: `production-change` and `memory-update`
  always owe the full block; `exploration` and tiny `documentation` edits may
  use the one-liner.

## Workflow

1. Read `wiki/workflows/verification.md`
   (§The canonical block, §Forbidden verification claims, §Required usage by
   task mode).
2. Take the mode (argument or ask) and inventory what was *actually* run or
   read this session.
3. Emit the block, performed lines each carrying the observed result.
4. Flag any forbidden claim you had to strike from the draft — that is part of
   the report.

## Output format

```markdown
Verification performed:
- <command/check/source actually used> — <result actually observed>

Verification recommended:
- <check not run yet / manual review still owed>
```

Compact form (only where the mode allows it):

```markdown
Verification: <what was done>; recommended: <what is still owed>.
```

## Related

- `skills/aos-task-mode/SKILL.md` — tells you which verification bar the
  mode owes.
- `skills/aos-hook/SKILL.md` — `post-edit` / `pre-memory-update` enforce
  this block at the boundary.
