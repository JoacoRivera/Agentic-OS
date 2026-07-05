---
tags: [eval, harness, harness-inventory, placement, static-dynamic, automation]
updated: 2026-06-28
---
# Eval — Harness Inventory Placement (which component, and what kind?)

> Verifies that, given a proposed new rule/tool/workflow/log, the agent names which
> **harness component** it belongs to and classifies it on the inventory's axes —
> static vs. dynamic, manual vs. automated, and whether it should be deferred.
> Illustrative case for the [Evals](../../evals.md) layer — not a record of a real
> run. Exercises the [Harness Inventory](../../harness-inventory.md) map.

```yaml
id: eval-harness-inventory-placement
name: Classify a new item into a harness component and its axes
type: mixed
mode: documentation
target: wiki/workflows/harness-inventory.md (component table / maturity)
input: |
  "For each proposed addition, say which harness component it belongs to, whether it
  is static or dynamic context, whether it is manual or automated today, and whether
  it should be built now or deferred:
    1. 'A new check that an implementation write-up split verification performed vs.
       recommended.'
    2. 'A post-commit hook that auto-runs wiki-lint.'
    3. 'A page documenting how Davos check-in alerts fire.'
    4. 'A rule that the agent must never auto-build the ExampleCRM solution.'"
expected: |
  The agent maps each to a harness component with the right axis classification:
    1 → Eval cases component; dynamic; manual (no runner); build now (fits the layer).
    2 → Hooks component; not implemented; automated *if built*; defer (no automation
        until the manual process proves its shape).
    3 → Project memory (wiki/projects/); dynamic; manual retrieval; build now.
    4 → Guardrails / integrity rules (a static AGENTS.md / project rule); static;
        manual, eval-checkable; build now.
  It treats the hook (2) as a deferred, not-yet-implemented component rather than
  routing it into an existing active component, and does not call any item "automated"
  that is manual today.
must_include:
  - "eval" component for item 1 (a behavioral check)
  - "hook" identified for item 2 and marked deferred / not implemented
  - "wiki/projects" or project-memory component for item 3
  - guardrail / integrity (static rule) for item 4
must_not_include:
  - item 2 routed into an existing active component as if already built
  - item 1 or item 3 described as automated
  - the ExampleCRM build rule (item 4) treated as dynamic/per-task rather than a static guardrail
verification:
  - Check each item against the Harness Inventory component table and maturity tiers.
  - Confirm the hook is classified as deferred / not-implemented, not active.
  - Confirm static vs. dynamic and manual vs. automated are assigned per the table.
notes: |
  Mixed type: the component name is mechanically checkable; the axis classification is
  a light judgment read. Complements (does not duplicate)
  [context-placement](context-placement.md): that case routes items to a storage
  *layer* (AGENTS.md / skill / workflow / projects / raw / eval); this one adds the
  harness axes — which *component*, static/dynamic, manual/automated, and defer-or-build.
  If the agent mis-classifies, fix the Harness Inventory table/maturity wording, not
  this eval. Item 4 uses ExampleCRM as a project-specific example; the rule it tests
  (static guardrails are not per-task) is generic.
```
