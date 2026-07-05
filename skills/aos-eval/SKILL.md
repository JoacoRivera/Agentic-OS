---
name: aos-eval
description: Load an eval case, hand its input over verbatim, compare the output-under-test against the case criteria, and help record the result. Report-only assistant for judgment — it drafts verdicts but never "passes" a judgment-type eval on its own; the user confirms before any result file is written.
---

# Eval Skill

Use this skill to run one hand-written eval case from
`wiki/workflows/evals/cases/`. It assists the manual run checklist: load the
case, present the `input` verbatim (uncoached), compare the output-under-test
against the criteria, draft the verdict and the result record. **For
`judgment` and `mixed` cases the skill's verdict is a draft** — the user
confirms or overrides it before anything is recorded. Deterministic criteria
(`must_include` / `must_not_include` substrings) it may check mechanically and
state as checked.

Invocation: `/aos-eval <case-slug>` (e.g. `/aos-eval verification-split`). Without an
argument, list the available cases with their `type` and `mode` and ask.

## Canonical contract

The case format, the manual run checklist, and the result-recording convention
live in `wiki/workflows/evals.md` and
`wiki/workflows/evals/results/README.md` — those win on any conflict with this
skill. `AGENTS.md` wins over both. The `pre-eval-result` guardrail
(`wiki/workflows/guardrail-hooks.md#e-pre-eval-result`)
applies to every recording.

## Rules

- **Input verbatim, no coaching.** Hand over the case's `input` exactly; never
  add hints the real task would not contain. If the run needs a cold context,
  say so and let the user run it in a fresh session/subagent — do not simulate
  the answer yourself and grade your own simulation.
- **Judgment stays human.** For `type: judgment`/`mixed`, present the evidence
  per criterion and a *proposed* PASS/PARTIAL/FAIL; the user's confirmation is
  the verdict. Never record a judgment verdict the user has not confirmed.
- **Results are evidence of real runs.** Write (or append to) the dated
  `wiki/workflows/evals/results/YYYY-MM-DD.md` **only** after an actual run,
  and only with the user's go-ahead. Never create a result file for a run that
  did not happen; never record a criterion as checked unless it was.
- **On failure, fix the target, not the eval.** Recommend fixing the
  skill/workflow/instructions under test; propose editing the case only when
  the case itself is wrong, and say why.
- Touch nothing else: no edits to cases, `wiki/` pages, or `raw/` (the dated
  result file, on confirmation, is the single allowed write).

## Workflow

1. Read the case page; restate `type`, `mode`, `target`.
2. Present the `input` verbatim for the run (or take the already-produced
   output-under-test from the user).
3. Compare: each `must_include` present? each `must_not_include` absent? each
   `verification` line — checked how, with what evidence?
4. Draft the verdict (mechanical parts asserted, judgment parts proposed) and
   the result record per the results README template.
5. On the user's confirmation of a real run, write/prepend the dated result
   file; otherwise stop at the draft.

## Output format

```markdown
## Eval run: <case id>

- Case: <path> (type: …, mode: …, target: …)
- Run context: <cold subagent / this session / user-run — how the input was fed>

### Criteria
- must_include "<signal>" — present/absent (evidence)
- must_not_include "<signal>" — absent/PRESENT (evidence)
- verification: <line> — checked how / not checked

### Verdict
- Proposed: PASS | PARTIAL | FAIL — <justification against the criteria>
- Judgment criteria awaiting user confirmation: <list or "none">

### Recording
- <not recorded (draft only) | recorded in results/YYYY-MM-DD.md after user confirmation>

### On failure
- <root-cause fix recommended in the target, not the eval>
```

## Related

- `skills/aos-hook/SKILL.md` — `/aos-hook pre-eval-result` guards the
  recording step.
- `wiki/workflows/evals/results/README.md`
  — the result-file template this skill fills in.
