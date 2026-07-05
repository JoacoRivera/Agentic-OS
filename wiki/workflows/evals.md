---
tags: [workflow, evals, evaluation, verification, integrity, task-modes, meta]
updated: 2026-07-04
workflow_kind: eval-suite
---
# Evals

> A lightweight evaluation layer: small, hand-written, reviewable test cases for
> agent behavior, so we can check that skills, workflows, memory ingestion, and
> task-mode outputs hold up over time — without building any automation.

An **eval** is a tiny test case for *how the agent behaves*, not for code. It pins a
scenario, the behavior we expect, and the concrete signals a reviewer checks the
output against. Evals are the verification counterpart to [Task Modes](task-modes.md):
modes set the discipline bar *before* work; evals check *after* whether that bar was
met. The schema in [`AGENTS.md`](../../AGENTS.md) still wins on any conflict.

Evals exist to catch the failure modes the integrity rules warn about — fabricated
facts, skipped required output fields, over-generalized memory, conflating
*verification performed* with *verification recommended*, and research that never
says what **not** to implement. They are deliberately manual: a human picks a case,
runs it, and records pass/fail. No runner, no dependencies, no framework.

## What an eval is (and is not)

- It **is** a scenario + expected behavior + required/forbidden outputs + how to
  verify them, written in Markdown so it is reviewable in a diff.
- It **is** generic to Agentic OS first; project-specific examples are
  fine but should be marked as such and not treated as universal.
- It is **not** a code unit test, a benchmark, or a model-specific harness.
- It is **not** a record of a real run — cases are illustrative skeletons (no
  `source:`), like the [task-mode examples](task-modes.md#examples). Real runs are
  recorded under [results/](evals/results/README.md).

## Eval case format

One eval per Markdown page under `wiki/workflows/evals/cases/`. Normal wiki
frontmatter (`tags`, `updated`), a one-line summary, then the whole eval as a single
fenced `yaml` block so it is one copyable, hand-editable record. Fields:

```yaml
id: eval-<slug>          # stable, matches the filename
name: <human-readable name>
type: deterministic | judgment | mixed
#   deterministic — pass/fail is mechanically checkable (a string is present/absent,
#                   a mode label is exactly X).
#   judgment      — pass/fail needs a human reading for quality (no fabrication,
#                   applicability is sound).
#   mixed         — some criteria mechanical, some judgment.
mode: <one Task Mode>    # exploration|implementation|production-change|hotfix|
#                          research|documentation|memory-update — or "n/a"
target: <skill / workflow / page being evaluated>
input: |
  The scenario or prompt handed to the agent. Concrete enough to re-run by hand.
expected: |
  The behavior we expect, in prose. The "ground truth" a reviewer reasons against.
must_include:            # signals the output MUST contain (substrings / properties)
  - <required signal>
must_not_include:        # signals the output MUST NOT contain
  - <forbidden signal>
verification:            # how a reviewer checks each criterion above
  - <check>
notes: |
  Caveats, judgment guidance, do-not-generalize warnings, project-specificity.
```

`must_include` / `must_not_include` are the mechanical backbone; `verification` tells
the reviewer how to confirm the judgment criteria. A deterministic eval leans on the
include/exclude lists; a judgment eval leans on `expected` + `verification`.

## Linkage to Task Modes

Evals are strongest when tied to the mode whose integrity bar they enforce:

- **`production-change`** — the highest bar. Any production-change eval should demand
  explicit success criteria, a real test plan, rollback notes, and a *performed vs.
  recommended* verification split — and should fail if verification is claimed but
  not actually run.
- **`memory-update`** — the strictest *integrity* evals. They must catch fabricated
  facts, claims that tests ran when they did not, failure to separate project-specific
  facts from reusable lessons, and missing open questions. See
  [memory-update-integrity](evals/cases/memory-update-integrity.md).
- **`research`** — evals must require that the output distinguishes **implement** from
  **do not implement**, and grounds applicability in cited sources. See
  [research-applicability](evals/cases/research-applicability.md).
- **`implementation`** — evals require the full field set (affected files, changes,
  verification performed, verification recommended, risks). See
  [implementation-verification](evals/cases/implementation-verification.md).

## Starter cases

- [memory-update-integrity](evals/cases/memory-update-integrity.md) — no fabrication,
  no false "tests ran", project facts vs. reusable lessons, open questions present.
- [implementation-verification](evals/cases/implementation-verification.md) — affected
  files, changes, verification performed vs. recommended, risks/assumptions.
- [research-applicability](evals/cases/research-applicability.md) — sources, summary,
  applicability to Agentic OS / the project, recommendation, and what **not** to
  implement.
- [task-mode-classification](evals/cases/task-mode-classification.md) — an ambiguous
  doc-vs-memory task must classify as `memory-update` when session/project facts are
  being captured.
- [context-placement](evals/cases/context-placement.md) — route mixed rules/facts/
  examples to the right layer; global context stays compact, project facts are not
  promoted globally, examples stay beside their workflow, eval criteria stay out of
  workflow prose. Enforces [Context Engineering](context-engineering.md).
- [harness-inventory-placement](evals/cases/harness-inventory-placement.md) — classify
  a proposed addition into a harness component and its axes (static/dynamic, manual/
  automated, build-now vs. deferred). Enforces the
  [Harness Inventory](harness-inventory.md); complements context-placement (which
  routes to a *layer*; this adds the harness *axes*).
- [guardrail-hooks-manual](evals/cases/guardrail-hooks-manual.md) — given a flawed
  write-up (fabricated test claim, unrelated edit, missing recommendation), assign the
  right lifecycle-hook severities (`block`/`warn`), not one undifferentiated verdict.
  Enforces the [Guardrail Hooks](guardrail-hooks.md) severity model.
- [verification-split](evals/cases/verification-split.md) — given a summary that says
  "tests should pass" and "links look fine" with no evidence, rewrite it so performed
  and recommended verification are separated and the false claims are blocked, not
  reworded. Enforces the [Verification](verification.md) convention.
- [ai-code-review-checklist](evals/cases/ai-code-review-checklist.md) — given a flawed
  AI implementation summary (unrelated edit, invented dependency, vague "tests should
  pass", missing risk section), produce a review with the right per-finding severities
  (`block`/`request-changes`) and a single outcome, not one undifferentiated verdict.
  Enforces the [AI Code Review](ai-code-review.md) checklist.
- [memory-quality-classification](evals/cases/memory-quality-classification.md) — given
  five mixed memory inputs (raw note, curated project rule, stale spec, approved example,
  unresolved inference), classify each into the right memory-quality category and use it
  at its correct authority (raw ≠ stable rule, stale ≠ current truth, example ≠ universal
  rule, inference stays open, project rules stay scoped to their project). Enforces the
  [Memory Quality](memory-quality.md) policy.
- [promote-draft-approval-delegation](evals/cases/promote-draft-approval-delegation.md) —
  four fixture drafts run in a sandbox repo copy: the ingest-worthy ones get the
  delegated approval flip (`Status: Approved` + dated `Approved by:` delegation line,
  nothing else touched), then route by risk — **low-risk auto-runs `/aos-ingest`** (sandbox
  wiki page + log entry must exist), **high-risk blocks** on the review block (strong
  claims / open questions / do-not-generalize / contradictions); the mixed-traits
  fixture must classify high-risk (one high-risk trait beats low-risk framing — a
  low-risk call there is a hard fail); the transient-noise one gets a no-write
  disposition and stays byte-identical. Enforces the delegated-approval carve-out and
  the risk-routed ingest policy in [`AGENTS.md`](../../AGENTS.md) (both 2026-07-03).
  The low-risk auto-ingest *cap* has no fixture yet.

## How to run evals manually

There is no runner. The process is a checklist (the
[Manual Operations Runbook](manual-operations.md#eval-run-process) folds this same
checklist into the daily session flow):

1. **Pick** an eval case from `cases/`.
2. **Feed** its `input` to the agent verbatim, in the relevant context (the skill or
   the mode under test). Do not give hints the real task would not contain.
3. **Compare** the agent's output against the case:
   - every `must_include` signal present?
   - every `must_not_include` signal absent?
   - each `verification` check satisfied (read for the judgment criteria)?
4. **Record** pass/fail and notes in a dated result file under
   [results/](evals/results/README.md) — `results/YYYY-MM-DD.md`, created only when a
   run actually happens. See the results README for the convention and template.
5. **Fix the root cause on failure.** A failing eval means the *skill, workflow, or
   instructions* are underspecified — fix those, not the eval. Only edit the eval if
   the eval itself was wrong (mis-stated expectation, impossible criterion). Re-run
   after the fix.

A pass is not proof of correctness in general — it is evidence for this one scenario.
Add cases when a new failure mode shows up in real work.

## Result recording

Results live under `wiki/workflows/evals/results/`. The
[results README](evals/results/README.md) is **convention + template only** — it never
holds run history. Actual runs go in dated files `results/YYYY-MM-DD.md`, each an
append/prepend-only evidence log (newest first, mirroring `wiki/log.md`). Do **not**
create a dated file unless an eval was actually run (mirroring the `raw/`-evidence
discipline: results are evidence of runs that happened).

A result record applies the [Verification](verification.md) convention to the eval
layer itself: separate **the eval actually run** (which case, against which target),
**the criteria actually checked** (which `must_include`/`must_not_include`/
`verification` lines were confirmed), and **follow-up recommended** (criteria not yet
checked, or a re-run owed after a fix). Do not record a criterion as checked unless it
actually was — the same forbidden-claim bar applies here.

## Open questions (accepted)

- Whether judgment-type evals need a second reviewer to reduce single-rater bias.
- How to keep generic cases generic as project-specific (e.g. ExampleCRM) variants accrete —
  candidate split into `cases/general/` + per-project folders if the count grows.
