# Agentic OS — LLM Wiki Schema

This repository is an **LLM wiki**: a persistent, compounding memory store
maintained by an agent. It follows Andrej Karpathy's `llm-wiki` pattern
(<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>).

This file is the **schema**: it tells the agent how the wiki is structured,
what the conventions are, and which workflows to follow. Read it at the start
of every session.

## Three-layer model

1. **`raw/` — immutable sources.**
   - Original source material: notes, transcripts, articles, clips, exports.
   - The agent reads from `raw/` but **never edits or deletes** it. Treat it as
     evidence.
   - Downloaded images and binary assets go in `raw/assets/`.
   - Group sources by topic and name them `raw/<topic>/<slug>-YYYY-MM-DD.ext` so
     they are stable and citable. See `raw/README.md` for the convention.

2. **`wiki/` — synthesized memory.**
   - A directory of agent-generated, cross-linked Markdown pages: concepts,
     entities, summaries, analyses.
   - The agent freely writes, updates, splits, and links these pages.
   - `wiki/index.md` is the catalog. `wiki/log.md` is the activity record.

3. **This file (`AGENTS.md`) — the schema.**
   - Conventions and workflows. Update it when the conventions change.

## Operator prompts

Reusable workflow prompts may live in `skills/`.

`skills/` is not a memory layer. It is a prompt library for repeated operations
such as ingesting raw notes, querying memory, or linting the wiki.

`skills/aos-*` is the canonical, model-agnostic skill source. Claude mirrors it
under `.claude/skills/aos-*`; Codex mirrors it through
`plugins/agentic-os/skills/aos-*` and `plugins/agentic-os/.codex-plugin/plugin.json`.
Run `python3 scripts/sync-skills.py` after changing a skill, or
`python3 scripts/sync-skills.py --check` to verify the mirrors. Use
`python3 scripts/sync-skills.py --global` to also reconcile user-level Claude
symlinks and the personal Codex plugin pointer; add `--install-codex` when you
want the script to run `codex plugin add agentic-os@personal`. The check is part
of the pre-commit contract for skill changes and CI for every push/PR.

The canonical schema remains this file (`AGENTS.md`). If a skill conflicts with
`AGENTS.md`, follow `AGENTS.md`.

Deterministic check scripts live in `scripts/` (currently `scripts/wiki-lint.py`
and `scripts/sync-skills.py`). Like `skills/`, `scripts/` is tooling, not a
memory layer.

Available skills:

- `skills/aos-ingest/SKILL.md`
  - Use when ingesting one or more files from `raw/` into `wiki/`.
  - Run as `/aos-ingest <raw file path>` in Claude, or `$aos-ingest` in Codex.
- `skills/aos-query-memory/SKILL.md`
  - Use to read and summarize the wiki before doing work — answers "what does
    Agentic OS already know about this?".
  - Read-only: never edits `wiki/`, `raw/`, or anything else.
- `skills/aos-capture-approved-example/SKILL.md`
  - Use after the user approves a result to capture it as a new `raw/` source
    file (the capture half of the memory loop).
  - Writes one `raw/` file only with a `Status: Draft` header line, then prompts
    the user to run `/aos-ingest` manually.
- `skills/aos-promote-draft-memory/SKILL.md`
  - Use to triage a draft capture before it enters the wiki: decide whether it
    is worth remembering, suggest edits, and recommend ingest / keep-as-draft /
    delete / merge. The triage step between capture and `/aos-ingest`.
  - Near-read-only on `raw/`: edits, deletes, and merges are recommendations the
    user executes — but on an **ingest** verdict the skill itself performs the
    delegated approval flip (`Status: Approved` + an `Approved by:` delegation
    line; see the Global-rules carve-out).
  - Classifies every draft **low-risk** or **high-risk** (see the skill for the
    trait lists). On an ingest verdict: **low-risk** → the skill runs
    `/aos-ingest` itself, capped at a small synthesis footprint (≤1 new page,
    ≤2 modified pages excluding index/log — over the cap it flips but hands
    `/aos-ingest` to the user); **high-risk** → `/aos-ingest` stays user-driven and is
    blocked until the user resolves the skill's high-risk review block (strong
    claims, open questions, do-not-generalize items, contradictions).
- `skills/aos-wiki-lint/SKILL.md`
  - Use to check wiki health before commits or after multiple ingests: runs
    `scripts/wiki-lint.py` first (deterministic checks), then the judgment
    checks (contradictions, raw-dump drift, invented certainty, hygiene).
  - Report-only by default: modifies nothing unless the user asks for fixes.
- `skills/aos-test-wiki-lint/SKILL.md`
  - Use after editing `scripts/wiki-lint.py` (a check, a message, an exit code,
    the `--root` seam, or a new check) to confirm the linter still behaves —
    runs the regression suite `scripts/tests/test_wiki_lint.py` (stdlib only).
  - Tests the **linter itself**, not the wiki content (that is `/aos-wiki-lint`).
    Report-only; a failure means fix the linter, not the test.

Report-only assistant skills (added 2026-07-03): each walks an already-defined
manual contract and emits its standard block; none blocks, enforces, or edits
wiki/raw content — the judgment and the commit decision stay with the user.

- `skills/aos-task-mode/SKILL.md`
  - Classify a task into a task mode and emit that mode's required-output
    skeleton (contract: `wiki/workflows/task-modes.md`).
- `skills/aos-verify-block/SKILL.md`
  - Emit the canonical verification performed-vs-recommended block for the
    current work; never upgrades an unrun check into "performed"
    (contract: `wiki/workflows/verification.md`).
- `skills/aos-hook/SKILL.md`
  - Run one guardrail lifecycle hook by hand (`/aos-hook <point>`) and produce the
    hook-result block (contract: `wiki/workflows/guardrail-hooks.md`).
- `skills/aos-pre-commit/SKILL.md`
  - Walk the pre-commit checklist against the real `git status`/`diff` and
    report the hook block — advisory, never a mechanical gate; never commits.
- `skills/aos-eval/SKILL.md`
  - Load an eval case, hand its input over verbatim, compare the output against
    the criteria, and help record the result. Judgment/mixed verdicts are
    drafts until the user confirms; the dated result file is written only for
    a confirmed real run (contract: `wiki/workflows/evals.md`).
- `skills/aos-plan/SKILL.md`
  - Plan a task without editing: classify mode, load relevant memory, run the
    pre-task contract internally, and emit an implementation-ready plan.
- `skills/aos-implement/SKILL.md`
  - Implement a change while applying the Agentic OS flow internally: mode
    classification, relevant memory load, required hooks, verification split,
    diff review, and close-out recommendations.

## Wiki conventions

### Page naming
- One concept/entity per page. Filenames are lowercase `kebab-case.md`.
- Group related pages in subdirectories under `wiki/` when a topic grows
  (e.g. `wiki/people/`, `wiki/projects/`). Reflect new groups in `index.md`.

### Per-sub-unit grouping (`general/` + one folder per unit)
When a project (or topic) is split across multiple **sub-units** — customers,
tenants, sites, environments — group its material by unit:

- One subfolder per unit, named for that unit in lowercase `kebab-case`
  (e.g. `wiki/projects/example-crm/acme/`, `.../contoso/`).
- A `general/` subfolder in the same parent for anything shared by **2+ units**.
- **Route by what the material documents, not by which unit hosts the code.** A
  process used by two or more units is `general/` even if one unit's
  implementation is primary (e.g. a shared onboarding flow used by two tenants → `general/`).
  A page or source that documents a **single** unit goes in that unit's folder.
- The **same per-unit / `general/` split applies to the project's `raw/` sources**,
  so a wiki page and the raw files it cites live under matching unit folders.
- Inside a unit folder, drop the now-redundant unit prefix from filenames
  (`baden/theoretical-loss.md`, not `baden/baden-theoretical-loss.md`); keep the
  unit name in `general/` filenames where it disambiguates (e.g.
  `general/bern-veto-process.md`).
- Reflect new unit groups in `index.md`. Don't pre-create empty unit folders —
  add a unit's folder when its first page or source lands.

### Page structure
Every wiki page except `index.md` and `log.md` starts with YAML frontmatter,
then a title and one-line summary.
The frontmatter is what makes pages reliably **recall-able** (grep `tags`) and
**trustworthy** (`source` links the evidence):

```markdown
---
tags: [topic, topic]
source: [raw/<topic>/<slug>-YYYY-MM-DD.md]   # omit if synthesized / no raw dependency
updated: YYYY-MM-DD
---

# Page Title

> One-line summary of what this page is.
```

Field rules:
- `tags` — required. Lowercase kebab-case keywords for retrieval.
- `source` — list of `raw/` files this page's claims depend on. Omit when the
  page is purely synthesized from other wiki pages.
- `updated` — the `YYYY-MM-DD` of the last meaningful edit.

Then the body. Cross-link other pages inline with relative Markdown links
(`[other page](other-page.md)`). Prefer linking over duplicating.

When a page makes claims that rest on `raw/` evidence, end it with a `## Sources`
section listing those files:

```markdown
## Sources
- [raw/<topic>/<slug>-YYYY-MM-DD.md](../raw/<topic>/<slug>-YYYY-MM-DD.md) — what it provides.
```

`wiki/_template.md` is a copyable starting point that follows this convention.

### `index.md` (catalog)
Content-oriented catalog of the wiki, organized by category. Each entry is a
link + a one-line summary:

```markdown
## Category
- [page title](page.md) — one-line summary.
```

### `log.md` (activity record)
Grow-only in substance: never delete an entry or alter its recorded facts
(mechanical corrections — a broken link, a typo — are allowed). **Prepend** new
entries so the newest sits at the top. One entry per meaningful change: a dated,
prefixed header plus **1–5 bullet lines**:

```markdown
## [YYYY-MM-DD] <op> | <subject>
- what changed, where, and why — one line per bullet where possible.
```

`<op>` is one of: `ingest`, `query`, `lint`, `schema`.

The log records *that* something changed and *where* — the content itself lives
in the wiki page (link it) and the raw capture, never restated in the log. Keep
an entry to at most 5 bullets and ~10 physical lines; `scripts/wiki-lint.py`
enforces this mechanically.

## Local dashboards

Dashboard or editor-specific files are optional local interfaces, not canonical memory. Do not put project facts only in dashboards; canonical memory belongs in `raw/` and `wiki/`.

## Workflows

### Ingest (new source → memory)
1. Place the source in `raw/` (assets in `raw/assets/`).
2. Read it. Create or update the relevant `wiki/` pages (synthesize, don't
   copy-paste). Add cross-links to existing pages.
3. Update `wiki/index.md` if pages were added or recategorized.
4. Prepend an `ingest` entry to `wiki/log.md`.

### Query (answer from memory)
1. Recall first: grep frontmatter `tags` and page titles across `wiki/`, then
   read the matching pages. `index.md` is the human-facing catalog; frontmatter
   is the reliable lookup backstop. Fall back to `raw/` only for evidence.
2. Synthesize the answer from existing pages.
3. If the exploration produced durable knowledge, file it back as a new or
   updated page and prepend a `query` entry to `wiki/log.md`.

### Lint (health check)
Start with the deterministic checks — run `python3 scripts/wiki-lint.py` from
the repo root (links, frontmatter, `source:` paths, index coverage, log
format/order/size, capture `Status:` validity, leaked tool-syntax markers).
Then review by judgment for: contradictions, orphan pages (unlinked from
`index.md` and from other pages), missing cross-references, and stale claims.
Fix what you can, flag what you can't, and prepend a `lint` entry to `log.md`.

### Memory health cadence
Reconcile memory at least every **7 days**: a maintenance pass is `/aos-wiki-lint`
(hygiene) plus `/aos-promote-draft-memory` (triage the draft queue). The newest
`lint` entry in `log.md` is the cadence anchor — running `/aos-wiki-lint` and
prepending its `lint` entry resets the timer. The Obsidian dashboard surfaces
this: a `HEALTH · DUE` chip and a "MEMORY HEALTH · CADENCE" panel light up when
7+ days have passed since that last `lint` entry (or when none exists yet).

### Manual operations (running the harness by hand)

The day-to-day runbook that *sequences* the components below into one session —
session-start, start-of-task, before/after-edit, code/memory/eval, and pre-commit
checklists, per-mode quick references, an automation-candidates table, and what not to
automate yet. Current stage: **manual harness with scripted deterministic lint
checks (`scripts/wiki-lint.py`); judgment steps still manual**. The flow,
checklists, and roadmap live in the workflow page, not here:
[wiki/workflows/manual-operations.md](wiki/workflows/manual-operations.md).

### Task modes (work classification)
Before executing a non-trivial task, classify it into a **task mode** — a
lightweight routing layer that sets how much structure, verification, and review
the work needs. The seven modes (`exploration`, `implementation`,
`production-change`, `hotfix`, `research`, `documentation`, `memory-update`), the
selection guide, each mode's required output fields, and the universal
anti-fabrication rule live in the workflow page, not here:
[wiki/workflows/task-modes.md](wiki/workflows/task-modes.md). Declare the chosen
mode in the first line of the work (`Mode: <name>`). Modes are routing, not
bureaucracy.

### Evals (agent-behavior checks)
A lightweight, manual evaluation layer checks that skills, workflows, memory
ingestion, and task-mode outputs hold up — the verification counterpart to task
modes. Cases (a YAML record: `id`/`name`/`type`/`mode`/`target`/`input`/`expected`/
`must_include`/`must_not_include`/`verification`/`notes`), the manual run checklist,
and the result-recording convention live in the wiki, not here:
[wiki/workflows/evals.md](wiki/workflows/evals.md). No runner — pick a case, feed its
input, compare, record. On a fail, fix the skill/workflow, not the eval.

### Context engineering (static vs. dynamic context)

Skills, examples, and project memory are **dynamic context** — loaded only when a
task makes them relevant. This file is **static context**: keep it to short,
invariant, high-frequency rules and *pointers*. Don't copy whole procedures or
project-specific facts in here; put procedure in `.claude/skills/` or
`wiki/workflows/`, project facts in `wiki/projects/`, examples beside their
workflow/skill, and eval criteria under the eval layer. The decision table,
placement rules, and the "what a good skill contains" checklist live in the
workflow page, not here:
[wiki/workflows/context-engineering.md](wiki/workflows/context-engineering.md).

### Harness inventory (the machinery around the model)

The agent is `Model + Harness`: the harness is every component around the model that
makes agentic work reliable (static/dynamic context, skills, tools, memory,
workflows, evals, guardrails, execution environment, observability, future hooks).
The central map of which components exist, where each lives, what is static vs.
dynamic, manual vs. automated, and which gaps remain lives in the workflow page, not
here: [wiki/workflows/harness-inventory.md](wiki/workflows/harness-inventory.md).

### Guardrail hooks (lifecycle checks)

Deterministic, **manual** checklists run at risky boundaries — `pre-task`,
`pre-edit`, `post-edit`, `pre-memory-update`, `pre-eval-result`, `pre-commit` — each
resolving to `block` / `warn` / `note`. They make a task mode's bar fire at the
moment of action (e.g. `memory-update` always runs `pre-memory-update`; edits run
`pre-edit`/`post-edit`). Definitions only — no scripts, git hooks, or runner yet. The
points, checks, severity, output block, and mode→hook matrix live in the workflow
page, not here: [wiki/workflows/guardrail-hooks.md](wiki/workflows/guardrail-hooks.md).

### Verification (performed vs. recommended)

Every non-trivial result must separate **verification performed** (checks/commands/
sources actually run or read this session, with the result observed) from
**verification recommended** (what a human still owes). Never claim a test, build,
lint, source inspection, link check, or memory grounding that did not actually happen —
those false claims are `block`-level. The canonical block, the compact one-liner, the
forbidden-claims list, and the per-task-mode bar live in the workflow page, not here:
[wiki/workflows/verification.md](wiki/workflows/verification.md).

### AI code review (review the diff, not just the tests)

Code an agent wrote or modified gets a structured review *before commit* — not only
"does it compile / do tests pass" but scope, architectural fit, real-vs-hallucinated
dependencies, domain rules, data safety, security, and whether the summary matches the
diff. Required for `implementation`/`hotfix`/`production-change` (and `documentation`
that touches code/config/scripts); strictest with a human gate for `production-change`.
The checklist, finding severities (`block`/`request-changes`/`note`/`question`), review
outcomes, and output block live in the workflow page, not here:
[wiki/workflows/ai-code-review.md](wiki/workflows/ai-code-review.md).

### Memory quality (not all memory is equal)

Stored knowledge carries different authority: raw notes and stale docs are low,
curated project/workflow knowledge is high (within scope), approved examples are
pattern evidence, and unverified claims stay open questions. Don't promote raw →
curated without grounding; mark stale content rather than keep it as current truth.
The category table, raw→curated promotion rules, conflict resolution, and the stale-
marking convention live in the workflow page, not here:
[wiki/workflows/memory-quality.md](wiki/workflows/memory-quality.md).

## Global rules

- **Do not store secrets**: no passwords, API keys, private keys, tokens, or
  production credentials.
- **Do not invent facts.** Mark uncertainty explicitly and cite the `raw/`
  source when a claim depends on one.
- Preserve `raw/` sources exactly. **Two narrow carve-outs:**
  1. Mechanical header-marker normalization (e.g. unifying a capture's
     `Status:` line to the canonical `Draft`/`Approved` form) is allowed when a
     schema change requires it — never content changes — and every such pass is
     recorded as a `schema` entry in `wiki/log.md`.
  2. The **delegated approval flip**: when `/aos-promote-draft-memory`'s triage
     verdict is *ingest*, that skill itself sets the capture's `Status:` line
     to `Approved` and records the delegation in the header's `Approved by:`
     field with the date (`Approved by: delegated skill policy —
     /aos-promote-draft-memory (YYYY-MM-DD)`). Those two header lines only — never
     content — and the attribution in the file is the record of the flip.
  Anything beyond these is a new dated `raw/` file, not an edit to an existing
  one.
- Prefer many small linked pages over one giant file.
- Keep entries concise and dated (`YYYY-MM-DD`).
- If a source omits commands, paths, dates, owners, or implementation details,
  preserve the gap as an open question. Do not infer missing project commands.
- Preserve TODOs, FIXME notes, and unresolved questions as open questions unless
  the source clearly resolves them.

## Dense wiki pages

Some project pages may become dense because they summarize many classes, fields, modules, tenants, or integration points.

Dense pages are allowed when they are synthesized, structured, and useful for retrieval.

However, do not let wiki pages become mirrors of raw snapshots.

When updating a dense page:

- Prefer summaries, patterns, risks, and navigation pointers over exhaustive enumeration.
- Move exhaustive source detail to `raw/`.
- Keep raw file paths in `source`.
- Preserve only the facts likely to help future agents reason or search.
- If a page grows because it contains multiple separable topics, split it into child pages and link them from the parent.
- Do not split only because a page is long; split when it has distinct retrieval purposes.

## Session closing checklist

Before ending a session:
- Ensure new sources are filed under `raw/`.
- Ensure affected `wiki/` pages and `wiki/index.md` are updated.
- Prepend a `log.md` entry summarizing the session's changes.
