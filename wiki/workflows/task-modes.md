---
tags: [workflow, task-modes, operating-discipline, verification, review, ai-code-review, meta]
updated: 2026-07-04
workflow_kind: policy
---
# Task Modes

> A lightweight routing layer: classify each task into a mode *before* executing,
> so the right amount of structure, verification, and review is applied — no more,
> no less.

Task modes are **not bureaucracy**. They are a fast classification step that tells
the agent how much discipline a task needs. A one-line lookup ("this is a hotfix")
sets the expected scope, the verification bar, and the output shape for the rest of
the work. The schema in [`AGENTS.md`](../../AGENTS.md) still wins on any conflict.

## How to choose a mode

Pick the *first* mode that matches, top to bottom:

1. **Urgent, narrow fix to stop active pain?** → `hotfix`.
2. **Touches production behavior, data migration, security, money/business-critical
   logic, or broad architecture?** → `production-change`.
3. **Capturing notes, lessons, or ingesting source into memory?** → `memory-update`.
4. **Writing/updating docs, wiki pages, examples, workflows?** → `documentation`.
5. **Studying papers, docs, APIs, libraries, or external options?** → `research`.
6. **Normal feature work or bug fix in an established codebase?** → `implementation`.
7. **Reading code, investigating, forming a hypothesis, no changes yet?** →
   `exploration`.

When two modes seem to fit, pick the **higher-discipline** one (a change that is
*both* a feature and security-sensitive is `production-change`, not
`implementation`; wiki ingestion that is *both* documentation and memory is
`memory-update`, not `documentation`, because its integrity bar is stricter). It is
fine to start in `exploration` or `research` and then re-declare a new mode once the
work is understood.

## Modes at a glance

| Mode | Use for | Code changes | Verification bar | Review |
| --- | --- | --- | --- | --- |
| `exploration` | investigation, codebase reading, hypothesis | none | findings traceable to inspected sources | low |
| `implementation` | normal feature work / bug fix | yes | run/observe what you changed | normal |
| `production-change` | prod behavior, migrations, security, business-critical, broad architecture | yes | explicit test plan + human review | high |
| `hotfix` | urgent, narrow fix | minimal | confirm the fix; note regression risk | fast, focused |
| `research` | papers, docs, APIs, libraries, options | none | claims grounded in cited sources | low |
| `documentation` | docs, wiki, examples, workflows | docs only | source-grounded; flag stale areas | normal |
| `memory-update` | raw notes, project memory, ingestion | memory only | facts grounded; no invention | normal |

## Required output structure per mode

Each mode declares its goal up front, then covers the fields below. Omit a field
only by explicitly stating it does not apply. Wherever a field below names
*verification performed* / *verification recommended*, it uses the canonical block and
per-mode bar defined in [Verification](verification.md) — that page is the single
source for the split, not each mode here.

### `exploration`
Goal · inspected files/sources · findings · open questions · recommended next step.
Does **not** require or make code changes.

### `implementation`
Goal · scope · affected files · implementation plan · changes made · verification
performed · verification recommended · risks/assumptions.

### `production-change`
Explicit success criteria · affected files · rollback/mitigation notes · test plan ·
verification performed · verification recommended · risks · human-review checklist ·
memory-update candidate (what, if anything, should be captured afterward).

### `hotfix`
Incident/problem statement · minimal scope · root cause · exact fix · verification
performed · regression risk · follow-up cleanup (if any).

### `research`
Question · sources inspected · summary · applicability to Agentic OS / the project ·
recommendation · what *not* to implement.

### `documentation`
Purpose · target audience · files changed · source grounding · stale/uncertain areas.

### `memory-update`
Source/session grounding · **memory-quality category being written** (raw /
curated-project / curated-workflow / approved-example / stale-deprecated /
uncertain-open, per [Memory Quality](memory-quality.md)) · facts captured · reusable
lessons · project-specific constraints · do-not-generalize notes · verification
performed vs. recommended · open questions. Do **not** duplicate a fact the wiki
already covers; do **not** promote raw → curated without grounding.

## Universal integrity rule

In **every** mode, and most strictly in `memory-update`:

- Do **not** fabricate facts, file paths, commands, or outputs.
- Do **not** claim a test, build, or command was run unless it actually was —
  separate *verification performed* from *verification recommended* per the canonical
  block in [Verification](verification.md), which also lists the forbidden
  (`block`-level) false claims and the per-mode verification bar.
- Do **not** over-generalize from a single case; mark single-instance findings as
  such and add do-not-generalize notes.
- Mark uncertainty explicitly and cite the `raw/` source when a claim depends on
  one. This mirrors the **Global rules** in [`AGENTS.md`](../../AGENTS.md).

## How to declare a mode

State the mode in the first line of the work, then cover that mode's fields. Minimal
form:

```markdown
Mode: implementation
Goal: <one line>
Scope: <one line>
...
```

For `exploration`, a `Mode:` line plus the goal and findings is enough — it is
deliberately light. `research` is light on *process* but still owes its full field
set — question, sources inspected, summary, applicability to Agentic OS / the
project, recommendation, and what *not* to implement — because a recommendation is
only trustworthy with its evidence. For `production-change`, treat the human-review
checklist as a gate, not an afterthought.

## Examples

Public examples can be added under `wiki/workflows/task-modes/examples/` once they are scrubbed of private project data.

## Evaluating mode behavior

Modes set the discipline bar *before* work; **evals** check *after* whether it was
met. The [Evals](evals.md) layer holds hand-written test cases tied to these modes —
strictest for `memory-update` (integrity), and requiring `research` to state what
*not* to implement and `production-change` to keep verification performed vs.
recommended honest. When a mode's output bar is repeatedly missed, add or tighten an
eval, then fix the mode wording — not the eval.

## AI code review per mode

Code an agent wrote or modified gets a structured review *before commit*, not just a
"tests pass" check. [AI Code Review](ai-code-review.md) is **required** for
`implementation`, `hotfix`, and `production-change`; for `documentation` only when the
change touches code/config/scripts; and is optional for `exploration`, `research`, and
`memory-update` unless they touch code/config. `production-change` gets the **strictest**
review **plus a human-review gate** (an agent self-review is necessary but not
sufficient). The checklist sections, finding severities (`block`/`request-changes`/
`note`/`question`), review outcomes, and output block live in
[AI Code Review](ai-code-review.md), not here.

## Guardrail hooks per mode

Modes also pick *which lifecycle guardrails* fire: `memory-update` always runs
`pre-memory-update`; `implementation`/`production-change`/`hotfix` run `pre-edit` and
`post-edit`; `production-change` runs the strongest `pre-commit`. The hook points,
checks, severity (`block`/`warn`/`note`), output block, and the full mode→hook matrix
live in [Guardrail Hooks](guardrail-hooks.md), not here.

## Memory quality per mode

`memory-update` (and any mode that writes memory) must declare *what kind* of memory it
is creating — raw, curated project/workflow, approved example, stale/deprecated, or
uncertain/open — because those carry different authority. [Memory Quality](memory-quality.md)
holds the categories, the raw → curated promotion rules, conflict resolution, and the
stale-marking convention; this page only requires the category be declared and that raw
is not promoted to curated without grounding.

## Where the resulting knowledge lives

Modes set *how much discipline* a task needs; [Context Engineering](context-engineering.md)
sets *where the knowledge it produces belongs*. An `exploration` finding stays in
`raw/` or the task output until reviewed; a `memory-update` files project facts into
`wiki/projects/`; a `documentation` task may add a `wiki/workflows/` page or an
example beside its skill. Keep `AGENTS.md` to invariant rules and pointers — never a
dumping ground for per-mode procedure. Task Modes are one component of the broader
[Harness Inventory](harness-inventory.md) (the full machinery around the model). For
*how* declaring a mode fits a real session — and the minimum per-mode checklist — see
the [Manual Operations Runbook](manual-operations.md) (it carries a per-mode quick
reference that operationalizes the modes above).

## Open questions (accepted)

- Whether `documentation` and `memory-update` should merge in practice, since wiki
  ingestion is both.
