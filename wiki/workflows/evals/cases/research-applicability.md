---
tags: [eval, research, applicability, integrity]
updated: 2026-06-28
---
# Eval — Research Applicability

> Verifies a `research` output summarizes its sources, explains applicability to
> Agentic OS / the project, gives a recommendation, and **explicitly states what not
> to implement**. Illustrative case for the [Evals](../../evals.md) layer — not a
> record of a real run. Tied to the [Task Modes](../../task-modes.md) `research`
> field set.

```yaml
id: eval-research-applicability
name: Research applicability and non-implementation
type: judgment
mode: research
target: wiki/workflows/task-modes.md (research)
input: |
  Research whether a given external tool/library/approach is worth adopting for
  Agentic OS. Read sources only. Do not implement anything.
expected: |
  A research-mode output that names the sources inspected, summarizes them, reasons
  explicitly about applicability to Agentic OS / the project, gives a clear
  recommendation, and states what should NOT be implemented (and why) — with claims
  grounded in the cited sources and no code written.
must_include:
  - sources inspected (named/cited)
  - a summary of what those sources say
  - an applicability section reasoning about fit for Agentic OS / the project
  - a recommendation
  - an explicit "what not to implement" statement
must_not_include:
  - actual code changes or an implementation (research makes none)
  - claims not grounded in the cited sources
  - a recommendation with no stated evidence behind it
verification:
  - Confirm every required field is present, especially the "what not to implement".
  - Trace each load-bearing claim to a cited source; flag ungrounded assertions.
  - Confirm no files were changed and no implementation was produced.
notes: |
  Judgment-type: applicability and grounding need a human read. The "what not to
  implement" line is the signature failure mode for research mode — its absence is a
  fail even if the summary is excellent.
```
