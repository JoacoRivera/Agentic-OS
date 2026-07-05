---
tags: [workflow, ai-code-review, review, code-review, verification, guardrail-hooks, task-modes, integrity, meta]
updated: 2026-07-04
workflow_kind: runbook
---
# AI Code Review (review checklist for agent-written code)

> A reusable review checklist for code an AI agent produced or modified. Run it
> *after* an implementation task and *before* committing. AI diffs are not
> trustworthy just because they parse or "tests should pass" — they must be
> reviewed for scope, fit, real dependencies, domain rules, data safety, and
> whether the explanation matches the diff.

This page is the **review counterpart** to the discipline already defined across the
harness: [Task Modes](task-modes.md) say how much discipline a task needs,
[Verification](verification.md) says how to report what was actually checked,
[Guardrail Hooks](guardrail-hooks.md) gate the risky boundaries, and [Evals](evals.md)
check behavior after the fact. AI code review is the **structured read of the diff
itself** — the thing a human reviewer (or the agent, by hand) walks before the change
is committed. It is **documentation/checklist only — no scripts, runners, or git
hooks.** The schema in [`AGENTS.md`](../../AGENTS.md) still wins on any conflict.

This checklist **complements** normal human engineering judgment and project-specific
review conventions — it does not replace them. It is a floor (the AI-specific failure
modes that are easy to miss), not a ceiling.

## What AI code review is

A fixed checklist applied to a diff that an agent generated or edited. It asks not
only "does it compile / do the tests pass?" but the questions an AI diff is most
likely to get wrong: did it stay in scope, fit the architecture, use *real*
dependencies, preserve domain rules, handle errors, keep data safe, stay
maintainable, avoid leaking secrets — and does the agent's written summary actually
match what the diff does?

## Why AI-generated diffs need a specific checklist

A model produces fluent, plausible code that passes a shallow read while failing in
AI-specific ways a normal review may not look for:

- **Scope creep** — unrelated refactors or files ride along with the change.
- **Hallucinated dependencies/APIs** — imports, methods, or framework behavior that
  do not exist or behave differently than claimed.
- **Confident but false verification** — "tests should pass" when nothing ran (a
  [forbidden verification claim](verification.md#forbidden-verification-claims)).
- **Architectural drift** — new abstractions or re-implemented helpers that bypass
  the project's existing services/patterns.
- **Silent domain-rule breakage** — edge cases and project-specific constraints
  dropped while the happy path looks correct.
- **Summary ≠ diff** — the explanation describes something the diff does not do (or
  omits something it does).

These are exactly the failures that compound into bad memory and broken production if
they slip through. The checklist makes the read deterministic instead of vibe-based.

## When AI code review is required

| Task mode | AI code review |
| --- | --- |
| `implementation` | **Required.** |
| `production-change` | **Required, strictest** — plus a human-review gate (see below). |
| `hotfix` | **Required**, focused on the exact fix and its regression risk. |
| `documentation` | **Only when** the docs change includes code, config, or scripts. Pure prose/wiki edits do not need it. |
| `exploration` | Optional — none needed unless code/config is touched. |
| `research` | Optional — none needed unless code/config is touched. |
| `memory-update` | Optional — none needed unless code/config is touched. |

For **`production-change`**, the review is stricter and **must include a human-review
gate**: an agent self-review is necessary but not sufficient: a human must sign off
before commit/merge, mirroring the `production-change` human-review checklist in
[Task Modes](task-modes.md) and the strongest `pre-commit` in
[Guardrail Hooks](guardrail-hooks.md).

## The checklist

Walk each section against the diff (not the summary). A section that does not apply is
marked "n/a", not skipped silently. Each item that fails becomes a **finding** with a
[severity](#finding-severity-levels).

### A. Scope and diff hygiene
- Did the agent modify **only** the relevant files?
- Are there **unrelated refactors** riding along?
- Are **generated/temp files** excluded from the diff?
- Does the **summary match the actual diff** (no described-but-absent or
  present-but-undescribed changes)?

### B. Architecture and conventions
- Does the code follow **existing project patterns**?
- Did the agent introduce **unnecessary abstractions**?
- Did it **bypass existing services/helpers** instead of reusing them?
- Is **naming consistent** with the surrounding code?

### C. Dependencies and APIs
- Are imported **packages/classes/functions real** (not hallucinated)?
- Are **versions compatible** with what the project already uses?
- Did the agent **invent framework behavior** (a method/flag/option that does not
  exist or behaves differently)?
- Are **external APIs used according to existing conventions**?

### D. Business rules and domain behavior
- Does the implementation **preserve existing domain rules**?
- Are **edge cases** handled?
- Are **project-specific constraints** respected?
- Are **stale docs/specs avoided** unless explicitly validated against current code?
- Does the review **distinguish its sources by authority** — current source behavior,
  current project wiki, raw notes, and stale docs are *not* one source (see
  [Memory Quality](memory-quality.md)); for implementation behavior, inspected current
  code beats a stale spec.

### E. Data, migrations, and persistence
- Are **DB writes safe**?
- Are **transactions** needed (and present)?
- Are **migrations/backfills reversible** or at least mitigated?
- Are **null/default/legacy values** considered?
- Is **production data risk** called out explicitly?

### F. Error handling and observability
- Are **errors handled** per project conventions?
- Are **logs useful and not noisy**?
- Are **sensitive details avoided** in user-facing messages?
- Are **failures diagnosable** (enough context to debug)?

### G. Security and privacy
- Any **secrets, tokens, credentials, or personal data** exposed?
- Any **authorization/authentication bypass**?
- Any **injection risks** (SQL/command/template/etc.)?
- Any **unsafe file/network access**?

### H. Tests and verification
- Were **tests/lint/build actually run**? (If not, they are *recommended*, not
  performed — see [Verification](verification.md).)
- Are **missing checks listed under "Verification recommended"**?
- Are there **new/updated tests** where appropriate?
- Are **manual verification steps explicit**?
- Does the verification block follow [`wiki/workflows/verification.md`](verification.md)
  (performed vs. recommended, no [forbidden claims](verification.md#forbidden-verification-claims))?

### I. Maintainability
- Is the code **understandable**?
- Is **complexity justified**?
- Are **comments useful and not noise**?
- Would a **human maintainer know why this change exists**?

### J. Review outcome
Conclude with exactly one outcome:

- **`approve`** — no `block` or `request-changes` findings; any notes/questions are
  resolved or accepted. Safe to commit (subject to the human gate for
  `production-change`).
- **`approve-with-notes`** — no blocking issues; only `note`-level findings remain.
  May commit, but the notes are **recorded** for follow-up.
- **`request-changes`** — one or more `request-changes` findings: the change must be
  fixed and re-reviewed before approval. Not committable as-is.
- **`block`** — one or more `block` findings: stop. The change **must not be
  committed** until the blocking issue is resolved (or explicitly approved, on the
  record, per [Guardrail Hooks bypass](guardrail-hooks.md#bypass)).

## Finding severity levels

Each finding carries one severity. These are **compatible with the
[Guardrail Hooks](guardrail-hooks.md) severity model** and roll up into the
`pre-commit` hook verdict:

- **`block`** — must stop before commit. Maps to a guardrail-hook `block`.
- **`request-changes`** — must be fixed before approval. Does not hard-stop the read,
  but the review cannot conclude `approve`; at `pre-commit` an unresolved
  `request-changes` finding behaves as a `block`.
- **`note`** — acceptable, but **recorded** for awareness/follow-up. Maps to a
  guardrail-hook `warn`/`note`.
- **`question`** — needs clarification before approval. The review cannot conclude
  `approve` while a `question` is open; record it and resolve it.

Fixed severities (not judgment calls):

- **False/vague verification claims** ("tests should pass" with nothing run, "looks
  fine") = **`block`** — same bar as the
  [forbidden verification claims](verification.md#forbidden-verification-claims).
- **Unrelated file edits** outside the declared scope = **`block`** unless
  **explicitly approved** on the record.
- **Production-changing behavior** that was not escalated to `production-change`
  (prod behavior, migration, schema, security, money/business-critical, broad
  architecture) = **`block`** — escalate the mode first.

A review's overall outcome is driven by its most severe finding: any `block` →
`block`; else any `request-changes` (or open `question`) → `request-changes`; else any
`note` → `approve-with-notes`; else `approve`.

## Standard review output format

One compact block per review:

```markdown
AI Code Review:
Mode: <implementation | production-change | hotfix | documentation>
Scope: <one line — what the change is supposed to do>
Changed files reviewed:
- <path>
Result: approve | approve-with-notes | request-changes | block

Findings:
- [block] <finding>
- [request-changes] <finding>
- [note] <finding>
- [question] <finding>

Verification performed:
- <check/command/source actually run this session, with the result observed>

Verification recommended:
- <check/review/source a human still owes>

Human review required:
- <yes/no, reason>
```

`Findings` is omitted when there are none. `Human review required` is **yes** for
every `production-change`. The `Verification performed` / `Verification recommended`
split is the canonical block from [Verification](verification.md) — a review may
**not** list a test/lint/build under "performed" unless it was actually run this
session.

## Integration with the harness

- **[Task Modes](task-modes.md)** — modes set *whether and how strict* a review is:
  required for `implementation`/`hotfix`/`production-change`, code-only for
  `documentation`; strictest (with a human gate) for `production-change`. The review
  reads against the mode's declared scope.
- **[Verification](verification.md)** — review findings separate **performed** from
  **recommended**; a review cannot count tests/lint/build as performed unless actually
  run. False/vague verification claims are `block` findings, matching the
  forbidden-claims list.
- **[Guardrail Hooks](guardrail-hooks.md)** — the moment-of-action gate: `post-edit`
  can **trigger** an AI code review for code/config/script changes; `pre-commit`
  **checks the review was performed** for `implementation`/`production-change`/`hotfix`
  and that no `block` finding is unresolved. Finding severities roll up into the hook
  verdicts.
- **[Evals](evals.md)** — the
  [ai-code-review-checklist](evals/cases/ai-code-review-checklist.md) case checks that
  a flawed mock summary (unrelated edit, invented dependency, vague "tests should
  pass", missing risk section) gets the right severities, not one undifferentiated
  verdict.
- **[Memory Quality](memory-quality.md)** — section D weights sources by authority: a
  **stale spec/doc is not current truth unless validated** against current code, and a
  business-rule check **separates** current source behavior, current project wiki, raw
  notes, and stale docs instead of treating them as equally authoritative.
- **[Context Engineering](context-engineering.md)** — this checklist is **dynamic
  context**: it lives in this workflow page, loaded when reviewing a diff, never copied
  into static `AGENTS.md` (which carries only a compact pointer).
- **[Harness Inventory](harness-inventory.md)** — AI code review is a **defined manual
  workflow** component (a review checklist run by hand); executable automation is
  deferred, same posture as the guardrail-hook and eval runners.
- **[Manual Operations Runbook](manual-operations.md)** — the [code-change
  process](manual-operations.md#code-change-process) is where this review fires in the
  daily flow (when required per mode, what always blocks, the regulated-domain business-rule-drift
  emphasis).

## Open questions (accepted)

- Whether a `/ai-code-review` skill should emit the review output block for a chosen
  mode — still deferred (its sibling report-only assistants `/aos-task-mode`, `/aos-eval`,
  `/aos-hook`, and `/aos-verify-block` were built 2026-07-03; this one waits until the manual
  checklist proves its shape).
- Whether `post-edit` and AI code review should merge into one "after edit" gate in
  practice, since both read the change before commit.
- How much of section D (business rules) is reliably checkable without project memory
  loaded — a candidate for tying the review to `/aos-query-memory` on the relevant project.
