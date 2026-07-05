---
tags: [workflow, verification, integrity, honesty, task-modes, guardrail-hooks, evals, ai-code-review, meta]
updated: 2026-07-04
workflow_kind: policy
---
# Verification (performed vs. recommended)

> The honesty convention: every non-trivial result must separate **what was
> actually verified in this run** from **what is still recommended for later**.
> One canonical block, used across all task modes, so a result never claims more
> checking than it did.

This page is the single home for a discipline that was previously scattered across
[Task Modes](task-modes.md) (the per-mode "verification performed vs. recommended"
fields), [Guardrail Hooks](guardrail-hooks.md) (the `post-edit` honesty split), and
[Evals](evals.md) (cases that fail when verification is claimed but not run). It is
the fifth umbrella sibling of those pages plus [Context
Engineering](context-engineering.md), all components in the [Harness
Inventory](harness-inventory.md). The schema in [`AGENTS.md`](../../AGENTS.md) still
wins on any conflict.

## The core principle

Separate two things that are easy to blur:

1. **Verification performed** — checks, commands, or sources the agent *actually*
   ran or read **in this run/session**, with the result it *actually* observed.
2. **Verification recommended** — checks, commands, reviews, or sources that are
   *not yet* done and a human (or a later run) still owes before fully trusting the
   result.

Anything not in column 1 belongs in column 2. The default for an unrun check is
**recommended**, never a soft-worded "performed."

## Why the distinction matters

A result that conflates the two manufactures false confidence — the single most
damaging failure mode for an agent that compounds memory over time:

- **"tests passed"** when tests were never run.
- **"links are valid"** when no link was opened.
- **"source code confirms X"** when only the wiki docs were read.
- **"memory is grounded"** when there is no session or `raw/` source behind it.

Each is a lie the next session inherits as fact. Keeping performed and recommended
separate makes the result's trust boundary explicit: a reader knows exactly what is
evidence and what is still an open check. This is the operational form of the
**Global rules** in [`AGENTS.md`](../../AGENTS.md) ("do not invent facts… mark
uncertainty") and the **Universal integrity rule** in [task-modes](task-modes.md).

## When the full block is required

Use the full two-part block for any task that **changed something or made a claim a
later reader will rely on**: `implementation`, `production-change`, `hotfix`,
`research`, `documentation`, and `memory-update` results. It is required wherever the
[`post-edit`](guardrail-hooks.md#c-post-edit) or
[`pre-memory-update`](guardrail-hooks.md#d-pre-memory-update) guardrail hooks fire.

### The canonical block

```markdown
Verification performed:
- <Command/check/source actually used>
- <Result actually observed>

Verification recommended:
- <Command/check/source not run yet>
- <Manual review or follow-up needed>
```

If nothing was verified, say so explicitly — an empty "performed" is honest; a
fabricated one is a `block`-level failure:

```markdown
Verification performed:
- None run in this environment.

Verification recommended:
- <the checks a human still owes>
```

### When a compact version is acceptable

For very small tasks (a one-line doc edit, a trivial exploration) a single line is
enough, as long as it still names what was and was not done:

```markdown
Verification: Not run; recommended: review diff and run /aos-wiki-lint.
```

The compact form is a shrink of the same two parts onto one line — never an excuse
to drop the "recommended" half. `exploration` and a tiny `documentation` edit may use
it; `production-change` and `memory-update` may **not** (they always owe the full
block).

## Forbidden verification claims

These are **`block`-level** under the guardrail hooks — a result containing one must
stop and be rewritten, not merely warned:

- **Do not claim tests, lint, or build ran** unless they were actually executed in
  this run. No tests run ⇒ "run the suite" is *recommended*, not performed.
- **Do not claim source code was inspected** unless the file was actually opened and
  read. Reading a wiki page about code is not reading the code — say which you did.
- **Do not claim links resolve** unless each was actually checked (opened or linted).
- **Do not claim memory facts are session/source-grounded** unless the `raw/` source
  or this session's facts are actually present to ground them.
- **Do not convert "recommended" into "performed"** — restating an unrun check in the
  past tense ("verified the boundary case") is fabrication.
- **Do not hide missing verification behind vague wording** — "should work", "looks
  fine", "probably passes", "tests should pass" are not verification. Either it was
  checked (state the check and result) or it is recommended (say so plainly).

## Required usage by task mode

Each [task mode](task-modes.md) owes a verification posture matched to its risk. This
table is the per-mode contract; the modes reference it rather than re-stating it.

| Mode | Verification requirement |
| --- | --- |
| `exploration` | List inspected files/sources + unresolved questions. Makes no changes, so no change-verification — but findings must trace to what was actually read. Compact form OK. |
| `implementation` | **Full block required.** Performed = what was actually run/observed on the change; recommended = checks still owed (build/lint/tests not run here). |
| `production-change` | **Full block required**, plus an explicit **test plan** and a **human-review gate**. Recommended must be explicit; an empty "recommended" on a prod change is itself suspect. |
| `hotfix` | **Full block required**, focused on the exact fix and its **regression risk** — what was confirmed about the fix vs. what regression checks are still owed. |
| `research` | Sources inspected listed, with **confidence/applicability limits**. "Performed" = sources actually read; "recommended" = validation/PoC not done. State what *not* to implement. |
| `documentation` | **Source grounding** (which source/page each claim rests on) + **link/index/log checks** when applicable. Performed = what was checked (e.g. `/aos-wiki-lint` run?); recommended = the rest. |
| `memory-update` | **Strictest.** Source/session grounding is **required under "performed"** — a memory page with no `raw/`/session evidence is blocked, not warned. No invention, no over-generalization. |

## Integration with the harness

- **[Task Modes](task-modes.md)** — modes set *which* posture above applies and carry
  "verification performed vs. recommended" as a required output field; this page is
  the canonical definition those fields point to.
- **[Guardrail Hooks](guardrail-hooks.md)** — hooks are the moment-of-action gate:
  `post-edit` requires the performed/recommended split, `pre-memory-update` requires
  source/session grounding under "performed", `pre-commit` warns when a recommended
  section is missing, and any **forbidden claim above is `block`**.
- **[Evals](evals.md)** — the [verification-split](evals/cases/verification-split.md)
  case checks that a write-up with "tests should pass / links look fine" is rewritten
  so performed and recommended are separated and the false claims are blocked.
- **[AI Code Review](ai-code-review.md)** — a review's findings carry this same split:
  the review **may not** list a test/lint/build under "performed" unless it actually
  ran this session, and a false/vague verification claim ("tests should pass") is a
  `block` review finding, matching the forbidden-claims list above.
- **[Memory Quality](memory-quality.md)** — promoting a fact from raw to curated
  **requires source/session grounding under "performed"** (an ungrounded promotion is
  blocked, not warned); and a **stale/deprecated marker is not removed unless the
  content is re-verified** — removing the callout is itself a verification claim, held
  to the forbidden-claims bar above.
- **[Context Engineering](context-engineering.md)** — verification *criteria* are
  dynamic context: they live in this workflow page and the eval layer, not in static
  `AGENTS.md` (which carries only a compact pointer).
- **[Harness Inventory](harness-inventory.md)** — this is the "Verification
  conventions" component: an **active manual convention** (honesty discipline checked
  by review, hooks, and evals), not an automated gate.
- **[Manual Operations Runbook](manual-operations.md)** — step 5 of the daily flow:
  the runbook tells you *when* in a session to write this block (`post-edit`,
  `pre-memory-update`, `pre-commit`).

## Open questions (accepted)

- Whether `documentation` link-checking should become a named sub-check of
  `/aos-wiki-lint` rather than a free-text "recommended" line.
