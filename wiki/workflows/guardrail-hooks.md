---
tags: [workflow, guardrail-hooks, hooks, guardrails, lifecycle, integrity, task-modes, evals, ai-code-review, meta]
updated: 2026-07-04
workflow_kind: policy
---
# Guardrail Hooks (manual lifecycle checks)

> Deterministic guardrails at lifecycle boundaries: short, manual checklists run
> *before* and *after* the risky steps of a task. They catch the things the agent
> should never forget but often does — declaring a mode, scoping an edit,
> separating verification performed from recommended, not fabricating memory.
> **Definitions only — no automation, scripts, or git hooks yet.**

A **guardrail hook** is a fixed checklist pinned to a point in a task's lifecycle
(`pre-task`, `pre-edit`, `post-edit`, `pre-memory-update`, `pre-eval-result`,
`pre-commit`). At that point the agent stops, runs the hook's checks, and records a
compact result. Hooks are the *enforcement-shaped* sibling of the discipline already
defined elsewhere: [Task Modes](task-modes.md) say how much discipline a task needs,
[Evals](evals.md) check after the fact whether it was met, [Context
Engineering](context-engineering.md) says where knowledge belongs — hooks are the
**moment-of-action gate** that makes those disciplines fire at the right boundary.
The schema in [`AGENTS.md`](../../AGENTS.md) still wins on any conflict.

## Why guardrail hooks exist

- **Failure clusters at boundaries.** The repeatable mistakes — skipping a mode,
  editing outside scope, claiming a test ran, inventing a memory fact, committing a
  stray file — all happen at a *transition*: starting work, touching a file, writing
  memory, committing. A hook is a checkpoint exactly there.
- **They make the implicit explicit.** The integrity rules in `AGENTS.md` and the
  per-mode output bars in [task-modes](task-modes.md) already say *what* good looks
  like. Hooks say *when to check* — turning standing rules into a momentary gate.
- **They are deterministic.** A hook is a fixed list with a pass/warn/block verdict,
  not a judgment call re-derived each time. Same boundary, same checks, every task.

## Why these are manual definitions for now

Same posture as the deferred observability/model-routing rows in the
[Harness Inventory](harness-inventory.md):
**define the manual process first; automate only once its shape is proven.**
(The `/aos-hook` and `/aos-pre-commit` assistants added 2026-07-03 are report-only
conveniences over this contract, not the deferred *blocking* automation.) We need
stable answers to *what points exist, what each checks, whether it blocks or warns,
what evidence it produces, which modes it applies to, and when bypass is allowed*
before any runner could enforce them. A hook framework built before that would
hard-code the wrong contract. So this page is a checklist contract a human (or the
agent, by hand) walks — not a script.

### Manual hook checklist vs. executable automation

| | Manual hook (now) | Executable automation (not built) |
| --- | --- | --- |
| Where it lives | This page — a checklist contract | A runner / git hook / Claude Code hook |
| Who runs it | The agent or user, by hand, at the boundary | The harness, on an event |
| Output | A hand-written hook-result block | A machine gate (exit code, blocked commit) |
| On `block` | The agent stops and reports | The action is mechanically prevented |
| Status | **Defined** | **Deferred** — a [note](#severity-levels) candidate, not a commitment |

This page deliberately adds **no** scripts, git hooks, Claude Code hooks, runners, or
dependencies. It changes no repo behavior automatically.

## Lifecycle hook points

Six points, in task order. Each lists its purpose and checks. Not every task hits
every point (see the [matrix](#hook-matrix)).

### A. `pre-task`
**Purpose:** classify the task and select the right context before work begins.
- Task **mode declared** for non-trivial work (`Mode: <name>`).
- **Goal** is clear and stated in one line.
- **Scope** is known, or the missing information is explicitly called out.
- Relevant **workflow / skill / project memory** is identified (or "none applies").
- **High-risk work escalates** to `production-change` (prod behavior, migration,
  schema, security, money/business-critical, broad architecture).

### B. `pre-edit`
**Purpose:** prevent uncontrolled file changes.
- Target **files or directories are identified** before editing.
- **Edit scope matches the task mode** (an `exploration` makes no edits; a `hotfix`
  stays minimal).
- **No unrelated broad refactor** riding along with the change.
- **No edits outside the declared scope** unless explicitly approved.
- **Migration / schema / security / production-behavior** changes are escalated to
  `production-change` before proceeding.

### C. `post-edit`
**Purpose:** verify what actually changed.
- **Changed-file list captured** (what was touched).
- **Changes summarized accurately** against that list.
- **Verification performed vs. recommended** kept separate, per the canonical block
  in [Verification](verification.md) (the `AGENTS.md` / [task-modes](task-modes.md)
  honesty split).
- **No claim that tests / lint / build ran** unless they actually ran — and **no
  [forbidden verification claim](verification.md#forbidden-verification-claims)**
  (false test/source/link/grounding claims) = `block`.
- **Risks / assumptions listed.**
- For **code / config / script changes**, run an [AI Code Review](ai-code-review.md)
  on the diff (scope, dependencies, domain rules, data safety, summary-vs-diff) — an
  unresolved `block` finding is a `block` here.

### D. `pre-memory-update`
**Purpose:** prevent fabricated or over-generalized memory.
- **Memory-quality category declared** (raw / curated-project / curated-workflow /
  approved-example / stale-deprecated / uncertain-open, per
  [Memory Quality](memory-quality.md)) — so the fact is written at the right authority.
- **Source / session grounding exists** (a `raw/` file or this session's facts) —
  recorded under "[verification performed](verification.md)", not assumed.
- **No ungrounded promotion** raw → curated — an unverified raw note must **not** be
  written into `wiki/` as a curated rule (`block`).
- **No invented** facts, paths, commands, tests, or conclusions.
- **Reusable lessons separated** from project-specific facts (do-not-generalize).
- **Stale / conflicting information marked** (status callout) **or opened as a
  question** — not silently kept as current truth or silently resolved.
- **Open questions preserved**, not silently resolved.
- **No duplicate note** if an existing wiki page already covers it (check first).

### E. `pre-eval-result`
**Purpose:** keep eval results honest.
- The eval **input was used verbatim, without coaching** (no hints the real task
  would not contain).
- **Pass / partial / fail justified** against the case's `must_include` /
  `must_not_include` / `verification` criteria.
- **Failures lead to fixing the workflow/skill**, never to weakening the eval.
- The **result file records only actual runs** (no dated result file without a run).

### F. `pre-commit`
**Purpose:** ensure the work is reviewable before commit.
- **`git status` reviewed.**
- **`git diff` reviewed.**
- **Index / log updated** if required (`wiki/index.md`, `wiki/log.md`).
- **Skill mirrors synchronized** (`scripts/sync-skills.py --check`) if `skills/`,
  `.claude/skills/`, or `plugins/agentic-os/skills/` changed.
- **Links checked or `/aos-wiki-lint` recommended** when wiki pages changed.
- **A [verification block](verification.md) is present** on the work — warn if the
  *recommended* half is missing (an all-"performed" claim with no follow-up is a flag).
- **Required [AI Code Review](ai-code-review.md) was performed** for an
  `implementation` / `production-change` / `hotfix` (or a `documentation` change that
  touches code/config/scripts) — **any unresolved `block` review finding blocks the
  commit**; a missing required review is itself a `block`.
- **No accidental generated / temp files** staged.
- **Commit message matches the scope** of the diff.

## Severity levels

A hook check resolves to one of three levels:

- **`block`** — must stop until fixed. The work cannot proceed past the boundary.
- **`warn`** — may proceed, but the risk **must be recorded** in the output.
- **`note`** — informational; no action required, surfaced for awareness.

Examples:
- **Fabricated test claim** (`post-edit` / `pre-memory-update`) = **block**.
- **Skill mirror drift** before commit (`pre-commit`) = **block**.
- **Missing optional `/aos-wiki-lint`** before a docs commit (`pre-commit`) = **warn**.
- **A future-automation candidate** (e.g. "this could be a git hook later") =
  **note**.

A hook's overall **Result** is the most severe level among its checks: any `block`
→ `BLOCK`; else any `warn` → `WARN`; else `PASS`.

## Hook output format

Each manual run produces one compact block:

```
Hook: <pre-task | pre-edit | post-edit | pre-memory-update | pre-eval-result | pre-commit>
Result: PASS | WARN | BLOCK
Mode: <task mode this applies under, or `none` when the hook runs standalone with no active task>
Checks:
- <check> — pass/warn/block
Issues:
- <what failed or is at risk>  (omit if none)
Action:
- <stop and fix | proceed and record risk | none>
```

`Mode:` names the [task mode](task-modes.md) the hook runs under. When a hook is
run **standalone with no active task** — e.g. a manual `/aos-pre-commit` on an
already-clean or already-committed tree — write `Mode: none`. It is a valid,
defined value, not a missing declaration.

`Issues` is omitted when the result is `PASS`. `Action` states the consequence of
the severity (stop on `BLOCK`, record-and-proceed on `WARN`, none on `PASS`).

## Hook matrix

Which hooks apply to which [task modes](task-modes.md), what each blocks vs. warns
on, and the evidence it produces:

| Hook | Applies to modes | Blocks on | Warns on | Evidence produced |
| --- | --- | --- | --- | --- |
| `pre-task` | all (non-trivial) | high-risk work not escalated to `production-change`; no goal | mode undeclared on a borderline-trivial task | declared `Mode:` + goal/scope line |
| `pre-edit` | `implementation`, `production-change`, `hotfix`, `documentation` (when files change) | edit outside declared scope without approval; un-escalated migration/schema/security/prod change | unrelated refactor riding along | identified target file/dir list |
| `post-edit` | `implementation`, `production-change`, `hotfix`, `documentation` (when files change) | claiming tests/lint/build ran when they did not; an unresolved `block` [AI code review](ai-code-review.md) finding on a code/config/script change | changed-file list or risks not captured | changed-file list + performed/recommended split + AI code review (on code changes) |
| `pre-memory-update` | `memory-update` (always); any mode writing memory | invented facts/paths/commands/tests; no source/session grounding; ungrounded raw → curated promotion | possible duplicate of existing wiki; uncertain area unmarked; memory-quality category undeclared | declared [memory-quality category](memory-quality.md) + grounded facts + do-not-generalize + open questions |
| `pre-eval-result` | any mode recording an eval run | result file written for a run that did not happen; eval weakened to force a pass | input may have been coached | PASS/WARN/FAIL justified against the case criteria |
| `pre-commit` | any mode that commits; **strongest for `production-change`** | stray generated/temp files; commit message not matching scope; required [AI code review](ai-code-review.md) missing or with an unresolved `block` finding | `/aos-wiki-lint` not run on a wiki change; index/log not updated | reviewed `git status`/`diff` + updated index/log + AI code review result (on code changes) |

How it ties to [task modes](task-modes.md):
- **`memory-update`** always requires **`pre-memory-update`** (its strictest gate).
- **`implementation`, `production-change`, `hotfix`** require **`pre-edit`** and
  **`post-edit`**.
- **`production-change`** requires the **strongest `pre-commit`** (review + index/log
  + recommended lint as a gate, not an afterthought) and treats every escalation
  check as a `block`.
- **`research`** requires the **source / context checks** of `pre-task`, but **no
  edit hooks** unless it changes docs.
- **`documentation`** requires **link / index / log checks** (`pre-commit`) when
  applicable, and `pre-edit`/`post-edit` when files actually change.
- **`exploration`** typically needs only `pre-task` (it makes no edits).

## Examples

**1. `memory-update` blocked — no source/session grounding.**
```
Hook: pre-memory-update
Result: BLOCK
Mode: memory-update
Checks:
- source/session grounding exists — block
- no invented facts/paths/commands — pass
- no duplicate of existing wiki — pass
Issues:
- The session was cleared; there are no grounded findings to capture. Writing a
  memory page now would fabricate the facts it claims to record.
Action:
- Stop. Do not write the page. Re-run only with a raw source or real session facts.
```

**2. `implementation` warned — tests not run, recommendation explicit.**
```
Hook: post-edit
Result: WARN
Mode: implementation
Checks:
- changed-file list captured — pass
- no claim tests/lint/build ran — pass (none were run)
- verification performed vs. recommended separated — pass
- risks/assumptions listed — pass
Issues:
- No tests were executed in this environment.
Action:
- Proceed and record the risk. Verification performed: code reads correctly on
  inspection. Verification recommended: run the unit suite before merge.
```

**3. `pre-commit` blocked — diff contains unrelated files.**
```
Hook: pre-commit
Result: BLOCK
Mode: implementation
Checks:
- git status reviewed — pass
- git diff reviewed — block
- no accidental generated/temp files — block
- commit message matches scope — warn
Issues:
- The staged diff includes an unrelated edit to a second module and a stray temp
  file outside the declared scope.
Action:
- Stop. Unstage the unrelated file and the temp file; keep the commit to the
  declared scope, then re-run the hook.
```

## Integration with the harness

- **[Task Modes](task-modes.md)** — modes pick *which* hooks apply (see the
  [matrix](#hook-matrix)); hooks make a mode's bar fire at the boundary instead of
  being remembered after.
- **[Verification](verification.md)** — `post-edit` enforces the performed-vs-recommended
  split, `pre-memory-update` requires source/session grounding under "performed",
  `pre-commit` warns when the recommended half is missing, and any forbidden
  verification claim (false test/source/link/grounding claim) is a `block`.
- **[AI Code Review](ai-code-review.md)** — `post-edit` can **trigger** a structured
  review of a code/config/script diff; `pre-commit` checks the required review was
  **performed** for `implementation`/`production-change`/`hotfix` and that no `block`
  review finding is unresolved. Review finding severities (`block`/`request-changes`/
  `note`/`question`) roll up into these hook verdicts.
- **[Evals](evals.md)** — hooks are a future eval *target*: a case can feed an output
  and check the agent assigns the right hook verdicts (see
  [guardrail-hooks-manual](evals/cases/guardrail-hooks-manual.md)). `pre-eval-result`
  also guards the eval layer's own honesty.
- **[Memory Quality](memory-quality.md)** — `pre-memory-update` is where the
  memory-quality policy fires: it **checks the declared category**, **blocks ungrounded
  promotion** from raw to curated, and requires stale/conflicting information to be
  **marked or opened as a question**.
- **[Context Engineering](context-engineering.md)** — hooks are **guardrails, not
  context**: they do not add knowledge the model reads, they gate actions at a
  boundary. They live in this workflow page (dynamic, loaded when relevant), not in
  static `AGENTS.md`.
- **[Harness Inventory](harness-inventory.md)** — the Hooks component moves from *not
  implemented* to **defined manual workflow** (definitions exist; automation
  deferred).
- **[Manual Operations Runbook](manual-operations.md)** — operationalizes these
  hooks: each lifecycle point here maps to a step-by-step checklist in the runbook's
  session flow (session-start → start-of-task → before/after-edit → pre-commit).

## Bypass

A hook may be bypassed only **explicitly and on the record**:
- A `warn` is bypassable by **recording the risk** in the output (that *is* the
  protocol, not an exception).
- A `block` is bypassable only with the **user's explicit approval for that specific
  action**, captured in the output. Approval for one action does not carry to the
  next.
- Bypass is **never silent**. An un-recorded bypass is itself a `block`-level failure
  the `pre-commit` / `pre-eval-result` hooks should catch.

## Open questions (accepted)

- Whether any hook should later become real automation (a git `pre-commit` hook, a
  Claude Code hook) — a `note`-level candidate, deferred until the manual contract is
  proven; the 2026-07-03 report-only assistants do not change this (they report,
  they never gate).
- Whether `pre-edit` and `post-edit` should merge into one "edit" hook in practice,
  since they bracket the same action.
