---
tags: [eval, cold-start, skill-discovery, skills, harness, memory-update]
workflow_kind: eval-suite
updated: 2026-07-03
---
# Eval — Cold Skill Discovery (fresh agent picks the right skill uncoached)

> Verifies that a **cold** agent, given a task in plain
> language with **no skill named**, *discovers and chooses* the correct `aos-*`
> skill from the available set — not just that a named skill emits its block. The
> This proves the right skill gets called, not only that a named skill can run.
> Complements [cold-start-handoff](cold-start-handoff.md) (which tests the
> `CLAUDE.md`→`AGENTS.md` contract, not skill selection).

```yaml
id: eval-cold-skill-discovery
name: Fresh session routes plain-language tasks to the right aos-* skill
type: judgment
mode: n/a (the agent must classify/route itself)
target: skill discovery — the `aos-*` skill descriptions + the available-skills surface
input: |
  Given to a fresh agent session in the repo root, one probe at a time, verbatim,
  with NO skill named and NO hint that a skill exists. For each probe the agent
  states which skill (if any) it would use and why, and does NOT execute it:
    P1: "The user just approved a SQL investigation I finished. I want it to become
         part of the project's long-term memory — what's the right first step?"
    P2: "Before I touch the check-in guest search code, what does this project
         already know about that seam?"
    P3: "I think I'm ready to commit this wiki change. Walk me through the checks
         I should run first — but don't commit anything."
expected: |
  P1 → /aos-capture-approved-example (capture the approved result into raw/ as a
       Draft), with /aos-ingest named as the later promotion step — NOT a direct
       wiki write, NOT a second memory store.
  P2 → /aos-query-memory (read the wiki index/tags first), NOT jumping straight
       into reading code or editing.
  P3 → /aos-pre-commit (walk the checklist, report the hook block), explicitly
       advisory — it must not offer to run the commit itself.
must_include:
  - each probe routed to the correct skill by its function, chosen from the
    available skills without being named in the prompt
  - P1 keeps capture (raw/Draft) separate from ingest (promotion), in that order
  - the report-only skills are described as advisory (P3 does not commit)
must_not_include:
  - inventing a skill name that does not exist in skills/aos-*
  - P1 writing wiki/ directly or proposing memory/ or MEMORY.md
  - executing any skill's side effects during a discovery/routing answer
  - coaching in the prompt (the run is void if the operator names a skill)
verification:
  - Read the three answers against the aos-* skill descriptions; each pick matches
    the skill whose description covers that task.
  - Confirm no files were created/changed during the routing answers (git status).
notes: |
  Run with a genuinely cold agent (subagent or cleared session). The probes map to
  aos-capture-approved-example / aos-query-memory / aos-pre-commit on purpose —
  these are DISTINCT from any skills a paired invocation test names
  (aos-verify-block / aos-hook / aos-eval), so discovery and invocation can share
  one cold agent without the invocation half leaking the discovery answers. A FAIL
  is a fix to the skill descriptions / available-skills surface, not to this eval.
  First created 2026-07-03 to close the long-standing "no discovery eval" gap noted
  in [harness-inventory](../../harness-inventory.md).
```
