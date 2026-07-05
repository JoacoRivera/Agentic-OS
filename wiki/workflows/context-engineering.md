---
tags: [workflow, context-engineering, static-context, dynamic-context, skills, memory, meta]
updated: 2026-07-04
workflow_kind: policy
---
# Context Engineering (static vs. dynamic context)

> The placement policy: skills, examples, and project memory are **dynamic
> context** loaded only when relevant; `AGENTS.md` holds only **static**,
> invariant behavior. Decide *where a rule/fact/example lives* before writing it.

This page makes one boundary explicit so future agents stop bloating global
instructions. It is the third sibling of [Task Modes](task-modes.md) (how much
discipline a task needs) and [Evals](evals.md) (did it meet the bar): this one
governs **where knowledge belongs**. All three are components in the
[Harness Inventory](harness-inventory.md). The schema in [`AGENTS.md`](../../AGENTS.md)
still wins on any conflict.

## The core principle

- **Global instructions define invariant behavior.** They apply to *every*
  session regardless of task.
- **Skills define task-specific procedure.** They load only when that task comes
  up.
- **Examples live under the relevant skill/workflow**, not in global context.
- **Project memory is retrieved or referenced, not always loaded.**

## Static vs. dynamic context

- **Static context** — what every agent reads at the start of every session:
  `AGENTS.md`. It is invariant, compact, and high-frequency. If a rule does not
  apply to nearly every session, it is not static.
- **Dynamic context** — everything pulled in *on demand* when a task makes it
  relevant: a skill (`skills/aos-<name>/SKILL.md`), a workflow page
  (`wiki/workflows/`), a project page (`wiki/projects/`), an example, a `raw/`
  source, an eval case. The agent loads it when it matters and ignores it
  otherwise.

The whole system already encodes this: `raw/` → `wiki/` → skills is a
load-on-demand pipeline (see [agentic-os-usage](../agentic-os-usage.md)). This
page just names the boundary and says how to keep it.

## Why bloated global context is harmful

- **It is always paid.** Every token in `AGENTS.md` is read in every session, on
  every task, whether relevant or not — cost and attention with no payoff for the
  90% of sessions it does not serve.
- **It drowns the invariant rules.** Safety rules ("do not store secrets", "do not
  invent facts") must be impossible to miss. A long procedure or a project detail
  next to them dilutes the signal.
- **It goes stale silently.** Procedures and project facts change; when they live
  in global context, every edit risks the schema, and stale copies contradict the
  live skill/page.
- **It duplicates.** A procedure copied into `AGENTS.md` *and* a skill drifts —
  two sources of truth, and the agent cannot tell which is current.

Keep `AGENTS.md` to short, invariant, high-frequency rules and **pointers** to
where the dynamic detail lives.

## What belongs where

- **`AGENTS.md` / global instructions** — invariant conventions and safety rules
  that apply across sessions: the three-layer model, page/naming conventions,
  global integrity rules, and *compact pointers* to the workflow/skill pages that
  hold the detail. No procedures-in-full, no project specifics.
- **`skills/aos-*`** — model-agnostic task-specific procedure: the steps, inputs,
  destination paths, and output format for a repeated operation (ingest, query,
  lint). `.claude/skills/aos-*` and `plugins/agentic-os/skills/aos-*` are mirrors.
  Loads only when that operation runs.
- **`wiki/workflows/`** — reusable, cross-task procedures and operating
  discipline that are not a single skill invocation (task-modes, evals, this page,
  german-technical-emails). A workflow page may be backed by a skill.
- **`wiki/projects/`** — stable, project-specific facts, business rules, and
  architecture (e.g. ExampleCRM VETO status values). Retrieved via `/aos-query-memory`, not
  loaded globally.
- **Examples** — concrete approved instances, in an `examples/` folder *next to*
  the skill or workflow they demonstrate (e.g.
  `wiki/workflows/task-modes/examples/`). Never in global context.
- **`raw/`** — immutable source material and not-yet-curated captures (including
  `Status: draft` notes). Evidence, read on demand, never edited.
- **Evals** — criteria for *whether behavior is correct*, under
  `wiki/workflows/evals/cases/`. Not mixed into normal workflow prose.

## Decision table

| Context item | Where it belongs | Why | Example |
| --- | --- | --- | --- |
| Invariant safety rule | `AGENTS.md` (Global rules) | Applies to every session; must never be missed | "Do not store secrets / do not invent facts" |
| Task-specific procedure | `skills/aos-<name>/SKILL.md` (or a `wiki/workflows/` page) | Only relevant when that task runs; load on demand | The `/aos-ingest` step list |
| Project-specific business rule | `wiki/projects/<project>/…` | Stable but project-scoped; retrieved, not global | Tenant-specific status values for an example project |
| Reusable workflow | `wiki/workflows/<name>.md` | Cross-task procedure/discipline, not a one-shot skill | [task-modes](task-modes.md), [evals](evals.md) |
| Approved example | `…/examples/` next to its skill/workflow | Demonstrates one procedure; belongs beside it | a scrubbed implementation example beside the workflow |
| Raw session note | `raw/<topic>/<slug>-YYYY-MM-DD.md` | Immutable evidence, curated later via `/aos-ingest` | A project-specific capture |
| Eval case | `wiki/workflows/evals/cases/<slug>.md` | Correctness criteria, kept out of workflow prose | [task-mode-classification](evals/cases/task-mode-classification.md) |
| Verification criteria | [`wiki/workflows/verification.md`](verification.md) + eval cases | Dynamic discipline, loaded when verifying; `AGENTS.md` keeps only a compact pointer | The performed-vs-recommended canonical block |
| Command / checklist skeleton | `skills/aos-<name>/SKILL.md` | Procedure detail loads with the task, not globally | The fixed Output/Note block in a `SKILL.md` |
| Temporary investigation finding | `raw/` (draft) / an `exploration` task output | Unproven; not promoted until reviewed | A hypothesis from reading code |
| Deprecated / stale knowledge | Marked with a status callout (or flagged as an open question); never silently kept as current | Must not linger as current truth; lower authority ([memory-quality](memory-quality.md)) | A superseded migration step |

## Placement rules

1. Put **only short, invariant, high-frequency rules** in `AGENTS.md`.
2. Put **procedural task behavior** in `skills/aos-*` or a `wiki/workflows/`
   page.
3. Put **stable project facts** in `wiki/projects/`.
4. Put **examples near the workflow or skill they demonstrate** (an `examples/`
   folder beside it).
5. Put **raw, not-yet-curated facts** in `raw/` (as drafts where appropriate).
6. Put **eval criteria under the eval layer** (`wiki/workflows/evals/cases/`).
7. **Do not copy entire workflow details into `AGENTS.md`** — link to the page.
8. **Do not duplicate project-specific facts into global instructions.**
9. **Do not promote one-off findings into reusable memory without review** (use
   [`/aos-promote-draft-memory`](../../AGENTS.md)).
10. When a rule could live in two places, prefer the **more dynamic** one and
    leave a pointer — never two copies.
11. **Retrieve by authority, not just relevance.** Prefer **curated and relevant**
    knowledge (`wiki/projects/`, `wiki/workflows/`); load raw and stale material with
    **lower authority**; treat examples as **pattern evidence, not universal fact**.
    Placement (this page) and authority ([Memory Quality](memory-quality.md)) compose.

## What a good Agentic OS skill contains

A skill (`skills/aos-<name>/SKILL.md`) is dynamic procedure, loaded only when
its task runs. `skills/` is the model-agnostic source; `.claude/skills/` and
`plugins/agentic-os/skills/` are generated mirrors. A good one has:

- **Frontmatter** with `name` and `description` — the `description` is what makes
  the skill discoverable (it states *when to use it*).
- **When to use it** — the trigger condition, near the top.
- **Required inputs** — arguments/paths it expects (e.g. `$ARGUMENTS`).
- **Procedure** — numbered, deterministic steps; cite `AGENTS.md` as canonical on
  conflict.
- **Output shape** — a literal, fenced format block for what it produces and where
  it writes (the destination path).
- **Verification expectations** — what to check before declaring done; keep
  *performed* vs. *recommended* honest (mirrors [task-modes](task-modes.md)).
- **Links to examples or evals** when they exist, instead of inlining them.

This is a checklist for *new or revised* skills, not a mandate to rewrite the
existing ones. The current `skills/aos-*/SKILL.md` files follow this shape
(`name`+`description` frontmatter, required reading, numbered procedure, a literal
output block) and use the `aos-` namespace across Claude and Codex.

## Integration with Task Modes and Evals

- **Task Modes** route *how much discipline* a task needs; this page routes *where
  the resulting knowledge lives*. An `exploration` finding stays in `raw/`/the task
  output until reviewed; a `memory-update` files project facts into
  `wiki/projects/`; a `documentation` task may add a workflow page. See
  [task-modes](task-modes.md).
- **Evals** can test placement itself: whether global context stayed compact,
  whether project facts were wrongly promoted, whether examples stayed beside their
  workflow, and whether eval criteria leaked into workflow prose. See the
  [context-placement](evals/cases/context-placement.md) case.
- **Guardrail hooks are guardrails, not context.** They gate *actions* at a lifecycle
  boundary; they do not add knowledge the model reads. Their definitions live in the
  [Guardrail Hooks](guardrail-hooks.md) workflow page (dynamic, loaded when relevant),
  never copied into static `AGENTS.md`.
- **Verification criteria are dynamic too.** The performed-vs-recommended convention
  lives in [Verification](verification.md) and the eval layer; `AGENTS.md` carries only
  a compact pointer, never the canonical block or the forbidden-claims list.
- **Review checklists are dynamic too.** The [AI Code Review](ai-code-review.md)
  checklist loads when reviewing a code diff; it stays in its workflow page, never
  copied into static `AGENTS.md` (only a compact pointer there).
- **Authority is a second axis on retrieval.** This page routes *where* knowledge
  lives; [Memory Quality](memory-quality.md) sets *how much to trust* what is
  retrieved — curated over raw, current over stale, example as pattern not rule. Pull
  in the relevant context, then weight it by its category.
- **The runbook is where this fires in a session.** The
  [Manual Operations Runbook](manual-operations.md) makes "load only the relevant
  dynamic context — don't preload every workflow page" step 2 of the daily flow, at
  both session-start and start-of-task.

## Open questions (accepted)

- Whether a future, explicit context-loading mechanism (auto-selecting which
  project/workflow pages to load per task) is worth building — deferred; no
  automation until the manual discipline proves its shape (the `/aos-task-mode` and
  `/aos-eval` assistants graduated from this posture 2026-07-03; this one has not).
- Whether Codex plugin installation should become a dedicated workflow page or stay
  as operational detail in the usage guide until the plugin is exercised in a fresh
  Codex session.

