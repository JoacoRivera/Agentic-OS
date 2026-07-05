---
name: aos-promote-draft-memory
description: Triage a draft raw capture — decide whether it is worth remembering, suggest edits, and recommend ingest / keep-as-draft / delete / merge. Use to review a draft capture before it enters the wiki.
---

# Promote Draft Memory Skill

Use this skill to review a **draft capture** (a raw example file that has not yet
been approved) and decide what should happen to it next. This is the **triage
half** of the memory loop — it sits between capture and ingest:

```text
capture (draft) → /aos-promote-draft-memory (this) → /aos-ingest → review log + index → /aos-wiki-lint → git commit
```

The user provides the path to a draft capture as an argument.

Arguments:

$ARGUMENTS

## What a draft is

A capture is a raw example file under `raw/<projects|workflows>/<slug>/examples/`.
It carries a `Status:` line in its header block — the review signal:

- `Status: Approved` — already reviewed and ready to `/aos-ingest`.
- `Status: Draft`, or no marker — a **draft still needing review**.

This skill operates on drafts. The Obsidian Dashboard's "Review queue" surfaces
the same set, with the matching detection in `dashboards/aos-hud.js`.

If no path is given, list the current drafts (raw example files whose status is
not `approved`) and ask the user which one to triage.

## Risk classification

Every draft is classified **low-risk** or **high-risk** before triage. The
classification decides how deep the review must go and whether ingest can be
auto-executed.

**Low-risk raw** — any of:

- format examples
- internal workflows
- small operational lessons
- captures without strong claims

→ A lightweight review is enough (promote + ingest without reading everything
is fine). If the verdict is ingest, **auto-execute `/aos-ingest`** after the
approval flip.

**High-risk raw** — any of:

- business rules
- production / data / SQL / migrations
- architecture
- security
- memory that contradicts existing wiki content
- anything a future agent will use to act

→ Review the raw in full (or at minimum have the user review the promote
summary before ingest). If the verdict is ingest, do **not** run `/aos-ingest`:
produce the high-risk review block (strong claims, open questions,
do-not-generalize items, contradictions) and **require the user to resolve it
before ingesting**.

One high-risk trait outweighs any number of low-risk traits — when in doubt,
classify high-risk.

**Low-risk auto-ingest cap.** Auto-ingest is for small syntheses only: at most
**one new wiki page** and at most **two existing pages modified** (`index.md`
and `log.md` do not count). If the triage foresees a larger footprint, do not
auto-ingest even though the draft is low-risk: perform the approval flip, list
the planned wiki changes in the output, and leave `/aos-ingest` to the user
(report `Ingest action: blocked by the auto-ingest cap — <planned footprint>`).

## Required reading

Before deciding, read:

- `AGENTS.md` — the wiki schema and the immutability rules.
- `wiki/index.md` — to locate overlapping existing memory.
- `wiki/log.md` — recent activity and chronology.
- The draft capture file itself.

If anything here conflicts with `AGENTS.md`, follow `AGENTS.md`.

## Rules

- **`raw/` is evidence — near-read-only.** The **delegated approval flip** below
  is the only write this skill ever performs on a raw file. Editing draft
  content, deleting, and merging remain **user actions you recommend**, never
  perform.
- **Delegated approval flip (the one permitted write).** When your verdict is
  that the draft is worth remembering and the recommended disposition is
  **ingest**, flip the marker yourself:
  - Change the `Status: Draft` line to the canonical inline `Status: Approved`
    (the file must keep **exactly one** `Status:` line — `aos-wiki-lint` enforces
    this).
  - Record the delegation in the header's `Approved by:` field:
    `Approved by: delegated skill policy — /aos-promote-draft-memory (YYYY-MM-DD)`
    with today's date. If the header lacks an `Approved by:` line, add it
    directly below `Status:`.
  - These two header lines are the **entire** permitted edit — never touch the
    body or any other header field.
  - Any other disposition (keep as draft / delete / merge) → **no write at all**.
- **`/aos-ingest` execution depends on the risk classification.** For a
  **low-risk** draft whose disposition is ingest, run `/aos-ingest <path>` yourself
  immediately after the approval flip — unless the **auto-ingest cap** applies
  (see Risk classification), in which case flip but leave `/aos-ingest` to the
  user. For a **high-risk** draft, never run `/aos-ingest` — ingestion stays
  user-driven and is blocked until the user resolves the high-risk review
  block.
- Do not invent missing facts, dates, paths, owners, or verification results.
- Preserve open questions; do not silently resolve them.
- Do not promote a single example into a general rule.
- Always compare against existing memory before recommending — a near-duplicate
  should usually merge, not ingest as a new note.
- One draft, one recommended disposition. Pick exactly one.

## Procedure

1. Read the required reading above.
2. Confirm the target is a draft (status not `approved`). If the path is missing
   or ambiguous, or multiple drafts match, list candidates and ask.
3. **Classify the risk** (low-risk / high-risk) per the classification above.
   For low-risk drafts a lightweight read is enough; for high-risk drafts read
   the raw in full.
4. **Assess whether it is worth remembering**, against the criteria below.
5. **Check for overlap** — query `wiki/index.md` and existing `raw/` notes for the
   same project/workflow/topic to find ingest-vs-merge candidates.
6. **Suggest concrete edits** to the draft (show the improved text inline).
7. **Recommend exactly one disposition** with rationale and the exact next steps
   the user should run.
8. **If the disposition is ingest, perform the delegated approval flip** (see
   Rules): set `Status: Approved` and write the `Approved by:` delegation line
   with today's date. Report the flip in the output. For any other disposition,
   write nothing.
9. **Branch on risk when the disposition is ingest**:
   - **Low-risk** → run `/aos-ingest <path>` yourself and report the result.
   - **High-risk** → do not ingest. Emit the **high-risk review block**:
     - **Strong claims** — every assertion a future agent could act on
       (rules, thresholds, invariants, causal statements).
     - **Open questions** — unresolved items that would change the synthesis.
     - **Do-not-generalize** — single examples or site-/case-specific facts
       that must not become general rules.
     - **Contradictions** — conflicts with `wiki/` pages or other raw notes,
       each with the conflicting source named.
     Then **ask the user to resolve the block** (confirm claims, answer or
     defer questions, settle contradictions) before running `/aos-ingest`.

## Is it worth remembering?

Weigh:

- **Durable** — true beyond this one session; not transient chatter.
- **Reusable** — a future agent would act differently for having read it.
- **Novel** — not already captured in `wiki/` or another raw note.
- **Specific** — concrete files, decisions, verification — not vague.
- **Complete enough** — facts and the reusable lesson are present, not just a stub.

If it fails durability/reusability/novelty, it likely should be **deleted** or
**merged**, not ingested.

## Suggesting edits

Propose edits as suggestions the user applies (you do not edit `raw/`):

- Tighten the capture: drop transcript noise, keep facts + the reusable pattern.
- Fill blank header fields from session facts, or move unknowns to **Open questions**.
- Ensure the header block is intact and its `Status:` line is the canonical
  inline form `Status: Draft` (not YAML frontmatter, not a list item below the
  label).
- Flag anything that looks like a secret, credential, or token to strip.
- Do not add claims the source does not support.

## Disposition criteria

- **Ingest** — durable, reusable, specific, complete, and not a duplicate.
  - This skill performs the delegated approval flip itself (`Status: Approved` +
    `Approved by:` delegation line — see Rules).
  - **Low-risk**: this skill then runs `/aos-ingest <path>` itself and reports the
    result — unless the auto-ingest cap applies (footprint larger than one new
    page + two modified pages), in which case flip, list the planned wiki
    changes, and hand `/aos-ingest` to the user. (If suggested edits are
    substantive, surface them first; trivial polish should not block the
    auto-ingest.)
  - **High-risk**: no auto-ingest. Next steps for the user: resolve the
    high-risk review block → apply the suggested edits (if any) →
    run `/aos-ingest <path>`.
- **Keep as draft** — worth remembering but not ready: missing facts, unverified,
  or open questions block synthesis.
  - Next steps: list exactly what is missing; leave `Status: Draft` so it stays in
    the review queue.
- **Delete** — transient, noise, superseded, or no reusable memory.
  - Next steps: recommend removal (e.g. show the `rm` command). **You do not delete
    `raw/` files** — the user does.
- **Merge** — substantially overlaps an existing raw note or another draft and is
  better consolidated.
  - Next steps: name the target note; describe what to fold in and what to drop;
    the user performs the merge and removes the redundant draft.

## Output format

```markdown
## Draft triage — <draft file path>

### Risk classification
- **low-risk / high-risk** — <which trait(s) triggered the classification>

### Worth remembering?
- Verdict: yes / partially / no
- Why: durable / reusable / novel / specific / complete — note which hold and which don't

### Suggested edits
- <concrete edit, with the improved text>

### Overlap with existing memory
- <wiki pages or raw notes on the same topic, or "none found">

### Recommended disposition
- **<ingest | keep as draft | delete | merge>**

### Approval action
- <"Status flipped to Approved by delegated skill policy (YYYY-MM-DD)" |
  "no write performed — disposition is not ingest">

### Ingest action
- <low-risk ingest: "/aos-ingest executed — <result summary>" |
  low-risk over the cap: "blocked by the auto-ingest cap — <planned footprint>" |
  high-risk ingest: "blocked pending resolution of the high-risk review block" |
  other dispositions: "n/a">

### High-risk review block  <!-- only when high-risk AND disposition is ingest -->
- **Strong claims:** <each actionable assertion, one per line>
- **Open questions:** <unresolved items, or "none">
- **Do-not-generalize:** <single-example / case-specific facts, or "none">
- **Contradictions:** <conflicts with wiki/ or raw/, with sources, or "none">
- **→ Resolve the items above, then run `/aos-ingest <path>`.**

### Rationale
- <why this disposition over the others>

### Exact next steps
- <commands / actions for the user to run>

### Open questions preserved
- <unresolved items, or "none">
```
