---
tags: [eval, results, log, verification]
updated: 2026-07-03
---
# Eval Results

> Convention + template for recording eval runs. This file is **never** a run log —
> it holds no results. See [Evals](../../evals.md) for the cases and the manual run
> process.

## Convention

- Record results **only for runs that actually happened** — they are evidence, like
  `raw/` sources. Do not pre-fill outcomes.
- One **dated file per run-day**: `wiki/workflows/evals/results/YYYY-MM-DD.md`. Create
  it the first time you record a run on that date; append later runs from the same day
  to it. Do **not** put run records in this README.
- Do **not** create a dated file speculatively — only when an eval was actually run.
- Each dated file is an **append/prepend-only evidence log**: never rewrite or delete
  past records. Newest record first, mirroring `wiki/log.md`.
- On a **FAIL**, the fix goes into the skill / workflow / instructions under test, not
  into the eval (unless the eval itself was wrong). Note the action taken.
- Link new dated files from [Run logs](#run-logs) below.

## Dated-file template

Each `results/YYYY-MM-DD.md` starts with normal wiki frontmatter (`tags`, `updated`)
and a one-line summary, then one record block per run (newest first):

```markdown
---
tags: [eval, results, log]
updated: YYYY-MM-DD
---
# Eval Results — YYYY-MM-DD

> Evidence log of eval runs on YYYY-MM-DD. Append/prepend-only, newest first.

## eval-<slug> — PASS | FAIL
- target: <skill / workflow / page under test>
- type: deterministic | judgment | mixed
- must_include: met | NOT met (which signals missing)
- must_not_include: clean | VIOLATED (which forbidden signals appeared)
- verification: <what the reviewer checked / read>
- action taken: <root-cause fix to skill/workflow/instructions, or "none — passed">
- notes: <judgment reasoning, caveats>
```

## Run logs

