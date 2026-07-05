---
tags: [eval, context-engineering, placement, skills, memory, documentation]
updated: 2026-06-28
---
# Eval — Context Placement (where does each item belong?)

> Verifies that, given a mix of proposed rules/facts/examples, the agent routes
> each to the correct layer — keeping global context compact, project facts out of
> global instructions, examples beside their workflow, and eval criteria out of
> workflow prose. Illustrative case for the [Evals](../../evals.md) layer — not a
> record of a real run. Exercises the
> [Context Engineering](../../context-engineering.md) placement rules.

```yaml
id: eval-context-placement
name: Route mixed items to the right context layer
type: mixed
mode: documentation
target: wiki/workflows/context-engineering.md (decision table / placement rules)
input: |
  "Here are five things we want the agent to know. For each, say exactly where it
  belongs (AGENTS.md, a skill, a wiki/workflows page, wiki/projects, raw notes, or
  an eval case) and why:
    1. 'Never store production credentials in the repo.'
    2. 'The ExampleCRM AccessReview door check uses status values Open/Pending/Banned.'
    3. 'A worked example of a clean implementation-mode write-up.'
    4. 'The step-by-step for turning a raw note into a wiki page.'
    5. 'A check that memory-update output never claims tests ran when they did not.'"
expected: |
  The agent maps each item to the correct layer with a one-line reason:
    1 → AGENTS.md global rules (invariant safety rule, applies every session).
    2 → wiki/projects/ (stable project-specific fact; retrieved, not loaded globally).
    3 → an examples/ folder beside the relevant workflow/skill (not global context).
    4 → a skill (.claude/skills/) or a wiki/workflows page (task-specific procedure).
    5 → wiki/workflows/evals/cases/ (eval criterion, not workflow prose).
  It keeps the safety rule (1) as the only item routed to AGENTS.md, and does not
  propose copying items 2–5 into global context.
must_include:
  - "AGENTS.md" for item 1 (the safety rule)
  - "wiki/projects" for item 2 (the ExampleCRM AccessReview fact)
  - examples placed next to a workflow/skill for item 3
  - a skill or wiki/workflows page for item 4
  - "evals" or "wiki/workflows/evals/cases" for item 5
must_not_include:
  - the ExampleCRM AccessReview fact (item 2) routed into AGENTS.md / global instructions
  - the procedure (item 4) copied in full into AGENTS.md
  - the eval criterion (item 5) placed into a normal workflow page body
  - more than one item routed to AGENTS.md
verification:
  - Check each item's destination against the Context Engineering decision table.
  - Confirm only the invariant safety rule lands in AGENTS.md (global stays compact).
  - Confirm project-specific facts are not promoted globally and examples stay beside
    their workflow/skill.
  - Confirm the eval criterion is routed to the eval layer, not mixed into workflow docs.
notes: |
  Mixed type: destinations are mechanically checkable; the one-line reasons are a
  light judgment read. Item 2 uses ExampleCRM as a project-specific example — the rule it
  tests (project facts are not global) is generic. If the agent over-promotes to
  AGENTS.md, the fix belongs in the Context Engineering placement rules / decision
  table, not in this eval.
```
