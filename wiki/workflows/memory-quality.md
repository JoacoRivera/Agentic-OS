---
tags: [workflow, memory-quality, memory, curation, authority, integrity, context-engineering, task-modes, meta]
updated: 2026-07-04
workflow_kind: policy
---
# Memory Quality (not all memory is equal)

> The authority policy for stored knowledge: raw notes, curated wiki knowledge,
> approved examples, stale/deprecated docs, and uncertain claims are **not equally
> trustworthy**. This page names the categories, sets each one's default authority,
> and says how a fact moves from raw → curated and how to resolve conflicts.

The agent compounds memory over time, so the *quality* of a stored fact matters as
much as its presence. A raw session note, a reviewed project rule, a superseded spec,
and an unverified inference all read as plain Markdown — but treating them as equally
authoritative is how stale specs get presented as current behavior and one project's
quirk gets globalized into a universal rule. This page is the umbrella that makes the
trust boundary explicit. It is a sibling of [Task Modes](task-modes.md) (how much
discipline a task needs), [Context Engineering](context-engineering.md) (where
knowledge belongs), [Verification](verification.md) (what was actually checked), and
[Guardrail Hooks](guardrail-hooks.md) (the moment-of-action gate) — all components in
the [Harness Inventory](harness-inventory.md). The schema in
[`AGENTS.md`](../../AGENTS.md) still wins on any conflict.

## The core principle

**Not all memory is equal.** Five buckets, by descending readiness-to-trust:

1. **Raw memory** — session facts, pasted notes, uncurated observations. Evidence,
   not rule.
2. **Curated knowledge** — reviewed, stable, reusable project facts and workflow
   process. High authority within its scope.
3. **Approved examples** — validated demonstrations attached to a workflow/skill.
   Pattern evidence, not universal rule.
4. **Deprecated / stale knowledge** — superseded specs, contradicted docs, old
   assumptions. Historical only.
5. **Uncertain / open knowledge** — plausible but unverified; an open question.
   Tentative, flagged as such.

This mirrors the three-layer model in [`AGENTS.md`](../../AGENTS.md): `raw/` is
evidence, `wiki/` is synthesis. Memory quality adds the *authority gradient within
and across those layers* — a `wiki/` page can still be stale, a `raw/` note can still
be the most current truth.

## Why memory quality matters

- **Stale specs masquerade as current behavior.** A superseded design doc reads
  identically to a live one; without a status marker the agent cites it as truth.
- **Raw notes get promoted by accident.** An unreviewed one-off finding, treated as a
  curated rule, becomes a fact the next session inherits and never re-checks.
- **Examples get over-generalized.** One approved demonstration becomes a "rule" the
  agent applies far outside the case it actually evidences.
- **Uncertain claims harden into fact.** An inference stated without its hedge loses
  the "open question" flag and is reasoned from as settled.

Each is the same failure the **Global rules** in [`AGENTS.md`](../../AGENTS.md) warn
about ("do not invent facts… mark uncertainty") — here made a category discipline.

## Memory categories

Six rows (the five buckets, with curated split into **project** and **workflow**
scope). Authority is the *default* — it can be overridden by a higher-authority
source per [conflict resolution](#how-to-choose-between-conflicting-sources).

| Category | Meaning | Default authority | Location | Agent behavior |
| --- | --- | --- | --- | --- |
| **A. Raw memory** | Session notes, pasted content, one-off findings, unreviewed captures | Low until curated | `raw/<topic>/…` (incl. `Status: draft` captures) | Use as source material/evidence, **not** as a stable rule. Promote via [`/aos-ingest`](../../AGENTS.md) only after review. |
| **B. Curated project knowledge** | Reviewed, stable project-specific facts and business rules | High **within that project** unless contradicted | `wiki/projects/<project>/…` | Retrieve when relevant; cite its `source:` internally; **do not globalize** to other projects. |
| **C. Workflow knowledge** | Reusable cross-project process / operating discipline | High for Agentic OS behavior | `wiki/workflows/…` | Follow for the matching task mode / workflow. |
| **D. Approved examples** | Validated examples demonstrating a workflow or skill | Pattern evidence, **not** universal rule | `…/examples/` beside the workflow/skill | Imitate the *structure*; do **not** overgeneralize the specific content. |
| **E. Deprecated / stale knowledge** | Superseded specs, contradicted docs, old assumptions | Low / historical only | Marked in place (status callout) or noted as superseded; never silently deleted if cited | Do **not** use as current truth unless explicitly doing history/comparison; re-verify first. |
| **F. Uncertain / open knowledge** | Plausible but unconfirmed; an open question | Tentative | An `## Open questions` section, or a flagged line on the relevant page | Flag the uncertainty; do **not** present as fact. |

Curated knowledge (B + C) is the only category that is "high authority" by default —
and only **within its scope** (a project rule is authoritative for that project, not
globally; a workflow rule for Agentic OS behavior). Everything else is source
material, pattern evidence, history, or an open question until promoted.

## How raw memory becomes curated knowledge

Promotion (raw → curated) is the [`/aos-ingest`](../../AGENTS.md) step, and it is the
moment authority is granted. Before a raw fact is written into `wiki/` as curated
knowledge it must pass **all** of:

1. **Source / session grounded** — it traces to a `raw/` file or this session's
   actual facts (recorded under *verification performed*, per
   [Verification](verification.md)). No grounding ⇒ no promotion.
2. **Clear project / workflow scope** — it is filed as project knowledge (B,
   `wiki/projects/`) or workflow knowledge (C, `wiki/workflows/`) deliberately, not
   dumped globally.
3. **Fact separated from inference** — observed facts and the agent's interpretation
   are distinguishable; an inference is not promoted as a fact.
4. **Verification performed vs. recommended preserved** — what was actually checked
   travels with the claim; unrun checks stay *recommended*, not silently dropped.
5. **Open questions preserved** — unresolved gaps stay open (category F), not
   silently resolved during write-up.
6. **No over-generalization** — one project's behavior is **not** promoted into a
   global rule; single-instance findings carry a *do-not-generalize* note.
7. **Prior contradictory pages reconciled** — if the new fact supersedes or conflicts
   with an existing page, that page is updated or marked stale (E) and linked, never
   left to silently contradict the new one.

A raw note that fails any of these stays raw (category A) — evidence, not rule. This
is exactly what the [`pre-memory-update`](guardrail-hooks.md#d-pre-memory-update)
guardrail hook checks at the moment of writing.

## How to choose between conflicting sources

When sources disagree, **authority depends on the task**, but the default order is:

1. **Current source code / inspected runtime behavior** — what the system actually
   does now.
2. **Current, verified project wiki** (B) — curated and recently grounded.
3. **Recent session-grounded notes** (A, fresh) — current but unreviewed.
4. **Older curated docs** (B/C, not recently verified).
5. **Raw notes** (A, old) — uncurated evidence.
6. **External / spec docs that may be stale** (E) — lowest, pending re-verification.

Phrase the choice by *what is being decided*, not by the list alone:

- **For implementation behavior** — *inspected current source / runtime beats a stale
  spec.* What the code does now wins over what a doc says it should do.
- **For business intent** — *the current stakeholder/spec may beat existing code*
  (the code may be the bug). Don't "correct" intent from code without confirming.
- **When the conflict is unresolved** — do **not** silently pick a side. Record it as
  an **open question** (category F) and flag both sources, so the next session sees
  the tension instead of inheriting one arbitrary answer.

This is the [`pre-memory-update`](guardrail-hooks.md#d-pre-memory-update) "stale /
conflicting information marked or opened as a question" check in practice.

## Marking stale / deprecated knowledge

The repo has **no `status:` frontmatter field**, and this page does not add one
(per [Context Engineering](context-engineering.md): no invented schema). Use the
existing tools instead — a **visible Markdown status callout** at the top of the
page body, and the page's existing `updated:` frontmatter as the freshness anchor:

```markdown
> **Status: Stale** — retained for historical context; do not use as current
> behavior without re-verification. Superseded by [new page](new-page.md).
> Last verified: 2026-06-28.
```

Conventions:

- Use **Stale** for content that may no longer be accurate (needs re-verification),
  **Deprecated** for content deliberately replaced.
- Always add a **"Superseded by" link** when a replacement exists, so history stays
  navigable.
- Treat the page's `updated:` date as **"last verified"** — don't bump it without an
  actual re-check.
- **Never silently delete** a cited stale page — mark it; deletion loses the history a
  comparison task may need. (Standalone, uncited stale pages may be removed during a
  [lint](../../AGENTS.md); a cited one is marked, not deleted.)
- A stale marker is **not removed unless the content is actually re-verified** — see
  [Verification](verification.md). Removing the callout is itself a verification claim.

## Integration with the harness

- **[Task Modes](task-modes.md) — `memory-update`.** A `memory-update` must **declare
  which category it is writing** (raw / curated-project / curated-workflow /
  approved-example / stale-deprecated / uncertain-open), must **not** duplicate a fact
  the wiki already covers, and must **preserve do-not-generalize notes**. The category
  decision is part of the mode's output, not an afterthought.
- **[Context Engineering](context-engineering.md).** Dynamic retrieval should **prefer
  curated and relevant** knowledge (B/C); raw and stale material is loaded with **lower
  authority**; examples are **pattern evidence, not universal fact**. Memory quality is
  the *authority* axis; context engineering is the *placement* axis — they compose.
- **[Verification](verification.md).** A promotion (raw → curated) **requires source /
  session grounding under "verification performed"**; a stale/deprecated marker is
  **not removed unless the content is re-verified** (removing it is a verification
  claim, subject to the forbidden-claims bar).
- **[Guardrail Hooks](guardrail-hooks.md).** `pre-memory-update` **checks the declared
  category**, **blocks ungrounded promotion** from raw to curated, and requires
  stale/conflicting information to be **marked or opened as a question**.
- **[AI Code Review](ai-code-review.md).** Stale specs/docs are **not used as current
  truth unless validated** against current code; business-rule review **distinguishes**
  current source behavior, current project wiki, raw notes, and stale docs rather than
  treating them as one source.
- **[Evals](evals.md).** The
  [memory-quality-classification](evals/cases/memory-quality-classification.md) case
  feeds mixed inputs (a raw note, a curated project rule, a stale spec, an approved
  example, an unresolved inference) and checks each is classified correctly and used at
  its right authority.
- **[Harness Inventory](harness-inventory.md).** Memory Quality is the **authority /
  curation-discipline** component over the Raw, Project memory, Examples, and
  (new) deprecated/stale rows — a defined manual convention, no automation.
- **[Manual Operations Runbook](manual-operations.md).** The [memory/wiki update
  process](manual-operations.md#memory--wiki-update-process) is where these gates fire
  in the daily flow — declare the category, confirm grounding, don't promote raw →
  curated without passing all gates.

## Open questions (accepted)

- Whether stale marking should eventually become a `status:` frontmatter field once
  enough pages carry callouts — deferred; the visible callout is the convention until
  the need for a queryable field is proven (the formerly deferred `/aos-task-mode`,
  `/aos-eval`, and `/aos-hook` assistants were built 2026-07-03; this one is still not proven).
- Whether `/aos-wiki-lint` should grow a check for stale callouts whose `updated:` date is
  old (a re-verification reminder) — candidate, not built.
- Whether "approved example" authority needs a per-example confidence note when one
  example is the sole evidence for a pattern.
