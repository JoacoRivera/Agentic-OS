---
tags: [workflow, manual-operations, runbook, operating-discipline, task-modes, guardrail-hooks, evals, verification, ai-code-review, memory-quality, context-engineering, harness, meta]
updated: 2026-07-04
workflow_kind: runbook
---
# Manual Operations Runbook

> The day-to-day operating guide: exactly what to do at each step of a real
> session — session start, task start, before/after edits, code review, memory,
> evals, and commit. The harness components are *defined*; this page is how you
> **run** them by hand until the stable parts are worth automating.

This is the practical companion to the harness. The other workflow pages each
*define* one discipline; this one *sequences* them into a session you can follow.
Where this page and a component page disagree on detail, the component page wins;
where any page and [`AGENTS.md`](../../AGENTS.md) disagree, `AGENTS.md` wins. It
sits beside the [Agentic OS Usage Guide](../agentic-os-usage.md) (paths, aliases,
mental model) — usage tells you *where things are*, this tells you *what to do
when*.

## Daily use summary

The whole runbook in nine steps. Everything below is detail on one of these:

```text
1. Declare mode.
2. Load relevant dynamic context.
3. Run the right manual hook checklist.
4. Perform work.
5. Split verification performed vs recommended.
6. Review diff / memory / eval result as applicable.
7. Update index/log/result files if needed.
8. Commit explicitly.
9. Close the session — file raw sources, sync wiki/index/log, leave open questions visible.
```

Periodically (≈ every 7 days), also run a memory-health pass — see
[Memory health cadence](#memory-health-cadence).

## When to use this page

- At the **start of any non-trivial session** — to set up context and mode.
- At each **risky boundary** during work — editing, writing memory, committing.
- When you are unsure **which checklist** a step owes — the mode quick references
  and the per-step checklists below resolve it.
- Skip it for trivial one-liners (a typo fix, a quick read) — but even then the
  [`pre-commit`](#pre-commit-process) sanity check still applies before you commit.

## Current maturity stage

```text
Stage: Manual harness + scripted deterministic lint (judgment steps manual)
```

What this means in practice:

- **The reliability model is documented.** Task modes, guardrail hooks,
  verification, AI code review, memory quality, context engineering, and the
  harness inventory all exist as written contracts.
- **Deterministic wiki checks are scripted.** `scripts/wiki-lint.py` (run by
  `/aos-wiki-lint` and the pre-commit checklist) mechanically checks links,
  frontmatter, `source:` paths, index coverage, log format/order/size, capture
  `Status:` validity, and leaked tool-syntax markers; since 2026-07-03 also
  eval-result file format, skill frontmatter/sync (`skills/aos-*`,
  `.claude/skills/aos-*`, and `plugins/agentic-os/skills/aos-*`),
  harness drift (this page + the inventory checked against the repo's scripts
  and skills — warnings), and stray temp/generated/scratchpad candidates
  (warnings). It reports; it does not block anything by itself. The script has
  its own regression suite
  (`scripts/tests/test_wiki_lint.py`, stdlib-only, run via the `--root` seam
  against clean/violating fixture pairs) — added 2026-07-02 because the linter
  had become load-bearing while untested.
- **Judgment enforcement is still manual.** The agent (or you) walks each
  checklist by hand and writes the result block. Nothing blocks mechanically —
  no git hooks, Claude Code hooks, or runners. Since 2026-07-03 five
  **report-only assistant skills** (`/aos-task-mode`, `/aos-verify-block`, `/aos-hook`,
  `/aos-pre-commit`, `/aos-eval`) walk these checklists and draft the blocks
  consistently — they are conveniences over the same manual contract, not
  gates. Two wrapper skills (`/aos-plan`, `/aos-implement`) now integrate those
  assistants into the normal plan/implement flow, so users can ask for one short
  skill instead of remembering the long harness prompt.
- **Automation comes after repeated manual use proves which checks are stable.**
  We codify the manual process first, run it for real, and only then automate the
  parts that turn out deterministic and repetitive.
- **Deterministic checks get automated before judgment-heavy workflows.** A link
  check or frontmatter check is mechanical and safe to script; an AI code review or
  a memory-promotion decision needs human judgment and stays manual longer.
- **Model routing remains deferred.** No per-task/per-mode model selection; see
  [Harness Inventory](harness-inventory.md) §Current maturity.

See [Harness Inventory](harness-inventory.md) for the full component-by-component
map of what is defined / manual / deferred.

## Default session start

Run this once at the top of a session, before declaring a task:

- [ ] **Check repo state if needed** — `git status` (and `git log --oneline -5` if
      resuming). Skip if you already know the tree is clean.
- [ ] **Identify the kind of work** — Agentic OS harness/meta, project work (e.g.
      ExampleCRM), research, memory capture, or implementation. This sets which dynamic
      context is relevant.
- [ ] **Load only the relevant dynamic context.** Pull in the matching skill,
      workflow page, or project page — not everything. See
      [Context Engineering](context-engineering.md).
- [ ] **Do not preload every workflow page.** They are dynamic context; load on
      demand. Preloading them defeats the point and bloats attention.
- [ ] **Treat `AGENTS.md` as static context, workflow pages as dynamic.**
      `AGENTS.md` is read every session; the workflow pages are pulled in when a
      task makes them relevant.
- [ ] **Decide whether a task mode needs declaring.** Non-trivial work does; a
      trivial read/typo does not.

Need facts before starting? `/aos-query-memory` (Agentic OS) or `/project-context` (ExampleCRM) —
see the [Usage Guide](../agentic-os-usage.md) §Skill scoping.

For routine Agentic OS work, prefer the wrappers:

- `/aos-plan <task>` — no edits; classifies mode, loads memory if useful, runs
  the pre-task contract internally, and returns a scoped plan.
- `/aos-implement <task>` — edits; classifies mode, loads memory if useful,
  applies required hooks internally, produces the verification split and risks,
  and suggests `/aos-pre-commit` plus `/aos-capture-approved-example` at close-out.

## Start of task

Operationalizes [`pre-task`](guardrail-hooks.md#a-pre-task). Before doing the work:

- [ ] **Declare the task mode** for non-trivial work — `Mode: <name>` on the first
      line. See [Task Modes](task-modes.md) for the selection guide.
- [ ] **State the goal** in one line.
- [ ] **State the scope** — what is in, what is out. If scope is unknown, say so
      explicitly rather than guessing.
- [ ] **Identify the relevant dynamic context** and name it (or "none applies"):
      a skill, a workflow page, a project wiki page, a `raw/` note, an eval case.
- [ ] **Decide whether the task must escalate to `production-change`** — prod
      behavior, data migration, schema, security, money/business-critical logic, or
      broad architecture. If yes, re-declare the mode before touching anything.
- [ ] **State the expected output shape** — what the result will look like (a diff,
      a wiki page, a findings list, an eval result block).

Run the [`pre-task`](guardrail-hooks.md#a-pre-task) hook and record its block if the
task is non-trivial.

## Before editing

Operationalizes [`pre-edit`](guardrail-hooks.md#b-pre-edit). Before changing any file:

- [ ] **Name the expected files/directories** you intend to touch.
- [ ] **State scope boundaries** — what you will *not* touch.
- [ ] **Classify the change** — docs-only, code, config, schema, migration,
      security, or production behavior. The class sets the bar for everything after.
- [ ] **Confirm the edit scope matches the mode** — an `exploration` makes no
      edits; a `hotfix` stays minimal; no unrelated refactor rides along.
- [ ] **Decide whether approval is needed** before broad changes — edits outside
      the declared scope need explicit approval, captured on the record.
- [ ] **Decide whether AI Code Review will be required after edits** — yes for
      code/config/script changes under `implementation`/`hotfix`/`production-change`
      (see [code-change process](#code-change-process)).

If the change is migration / schema / security / production behavior and the mode is
not yet `production-change`, **escalate first** — that is a `block`.

## After editing

Operationalizes [`post-edit`](guardrail-hooks.md#c-post-edit). After changing files,
before moving on:

- [ ] **Review the changed-file list** — `git status` / `git diff --stat`.
- [ ] **Compare the agent's summary against the actual diff** — nothing
      described-but-absent, nothing present-but-undescribed.
- [ ] **Confirm no unrelated files changed.**
- [ ] **Confirm index/log/navigation updates** if a wiki page changed
      (`wiki/index.md`, `wiki/log.md`).
- [ ] **Split verification performed vs. recommended** using the canonical block in
      [Verification](verification.md) — never claim a test/lint/build/source/link
      that did not actually happen (those are `block`-level).
- [ ] **List unresolved risks and assumptions.**
- [ ] **Decide whether AI Code Review is required** — run it now for code/config/
      script changes (see below).

## Verification

Reference: [Verification](verification.md).

Every non-trivial result must split **verification performed** from
**verification recommended**. Performed means a command, check, source, or file was
actually run or read in this session, with the observed result recorded.
Recommended means it has not happened yet and is still owed before the result is
fully trusted. If no verification ran, say that explicitly instead of implying it.

For very small documentation edits, the compact form is acceptable as long as it
keeps both halves visible:

```markdown
Verification: <what was done>; recommended: <what is still owed>.
```

Use the full block for implementation, production-change, hotfix, research, and
memory-update work, and for documentation work where the change or claim is
substantial enough that a later reader will rely on the check history.

## Code change process

Reference: [AI Code Review](ai-code-review.md).

**When AI Code Review is required:**

- `implementation` — required.
- `hotfix` — required, focused on the exact fix and its regression risk.
- `production-change` — required, strictest, **plus a human-review gate** (an agent
  self-review is necessary but not sufficient).
- `documentation` — only when the change touches code, config, or scripts.
- `exploration` / `research` / `memory-update` — optional unless code/config is
  touched.

**Standard output:** one AI Code Review block — `Mode`, `Scope`, changed files
reviewed, `Result` (`approve` / `approve-with-notes` / `request-changes` /
`block`), findings with severities, and the performed-vs-recommended verification
split. See the [output format](ai-code-review.md#standard-review-output-format).

**What always blocks** (fixed severities, not judgment calls):

- **False/vague verification claims** — "tests should pass", "looks fine" with
  nothing run.
- **Unrelated edits** outside the declared scope (unless explicitly approved on the
  record).
- **Invented dependencies/APIs** — imports, methods, or framework behavior that do
  not exist or behave differently than claimed.
- **Un-escalated production-changing behavior** — prod behavior, migration, schema,
  security, money/business-critical, broad architecture done outside
  `production-change`.
- **Unresolved `block` findings** — the change must not be committed until they are
  resolved (or explicitly approved on the record, per
  [bypass](guardrail-hooks.md#bypass)).

## Memory / wiki update process

Reference: [Memory Quality](memory-quality.md) and
[`pre-memory-update`](guardrail-hooks.md#d-pre-memory-update).

- [ ] **Declare the memory-quality category** being written — raw / curated-project
      / curated-workflow / approved-example / stale-deprecated / uncertain-open.
- [ ] **Confirm source/session grounding** — a `raw/` file or this session's actual
      facts, recorded under *verification performed*. No grounding ⇒ no write.
- [ ] **Check whether the fact already exists** in the wiki — do not duplicate;
      update the existing page instead.
- [ ] **Preserve do-not-generalize notes** — single-instance findings stay
      single-instance; one project's quirk is not promoted into a global rule.
- [ ] **Preserve open questions** — unresolved gaps stay open (category F), not
      silently resolved.
- [ ] **Do not promote raw → curated unless all promotion gates pass** — grounding,
      scope, fact-vs-inference, verification preserved, open questions preserved, no
      over-generalization, prior contradictory pages reconciled (see the
      [promotion rules](memory-quality.md#how-raw-memory-becomes-curated-knowledge)).
      An ungrounded promotion is a `block`.
- [ ] **Mark stale/conflicting knowledge visibly** — a status callout or an open
      question — instead of silently overwriting. A stale marker is not removed
      unless the content is actually re-verified.

The mechanics live in the skills: `/aos-ingest` to promote a `raw/` source into `wiki/`,
`/aos-promote-draft-memory` to triage a draft first, `/aos-capture-approved-example` to
file an approved result back into `raw/`.

## Eval run process

Reference: [Evals](evals.md) and [`pre-eval-result`](guardrail-hooks.md#e-pre-eval-result).

- [ ] **Pick an eval case** from `wiki/workflows/evals/cases/`.
- [ ] **Use its `input` verbatim, without coaching** — no hints the real task would
      not contain.
- [ ] **Compare the output** against the case's `must_include`, `must_not_include`,
      and `verification` criteria.
- [ ] **Mark PASS / PARTIAL / FAIL**, justified against those criteria.
- [ ] **Record only real runs** in a dated result file under
      `wiki/workflows/evals/results/` (`results/YYYY-MM-DD.md`, newest first). Never
      create a result file for a run that did not happen.
- [ ] **On failure, fix the workflow/skill/instructions, not the eval** — only edit
      the eval if the eval itself was wrong (mis-stated expectation, impossible
      criterion). Re-run after the fix.

There is no runner — this is a manual checklist by design.

## Pre-commit process

Operationalizes [`pre-commit`](guardrail-hooks.md#f-pre-commit). Before every commit:

- [ ] **`git status`** — review what is staged/unstaged.
- [ ] **`git diff`** — read the actual change.
- [ ] **Confirm changed files match the intended scope** — nothing unrelated.
- [ ] **Confirm no unresolved `block` finding** from AI Code Review (and that a
      required review was actually performed).
- [ ] **Confirm links/index/log updated** if a wiki page changed.
- [ ] **Run `python3 scripts/sync-skills.py --check`** if `skills/`,
      `.claude/skills/`, or `plugins/agentic-os/skills/` changed. Drift is a
      pre-commit `block`: run `python3 scripts/sync-skills.py` to regenerate the
      derived Claude/Codex mirrors, then re-check.
- [ ] **Run `python3 scripts/wiki-lint.py`** if a wiki page, capture, or the log
      changed — it is cheap and deterministic. Run the full `/aos-wiki-lint` (judgment
      pass) after multiple ingests; if not run, record it under *verification
      recommended* (do not claim it ran).
- [ ] **Confirm no temp/generated/stray files** are staged (e.g. nothing from the
      scratchpad, no Obsidian plugin noise).
- [ ] **Confirm a verification block is present** — warn if the *recommended* half
      is missing.
- [ ] **Commit explicitly with a scope-matching message.** Commits are deliberate,
      never auto.

`production-change` gets the strongest `pre-commit`: review + index/log + recommended
lint are gates, not afterthoughts, and every escalation check is a `block`.

## Session close

The end-of-session bookend — mirrors the [`AGENTS.md`](../../AGENTS.md) session
closing checklist (which wins on any conflict). Before stopping:

- [ ] **File raw/session sources** under `raw/` if any were created or received this
      session (preserve them exactly; don't edit `raw/`).
- [ ] **Update affected curated wiki pages** if new durable knowledge was produced.
- [ ] **Update `wiki/index.md`** only when navigation actually changed (new/renamed/
      recategorized pages).
- [ ] **Prepend a `wiki/log.md` entry** (newest first) when wiki content or schema
      changed.
- [ ] **Record eval results only if a real eval ran** — under
      `wiki/workflows/evals/results/`; never file a result for a run that did not happen.
- [ ] **Leave unresolved questions visible** — keep open questions and stale markers in
      place rather than silently resolving them.
- [ ] **Commit explicitly, or leave a clearly described uncommitted state** — never an
      auto-commit, never a silent half-done tree.

## Memory health cadence

Reference: [`AGENTS.md`](../../AGENTS.md) §Memory health cadence and
[Memory Quality](memory-quality.md). Separate from the per-session loop above — this is
a periodic pass, not a per-task step:

- [ ] **Every ~7 days, run (or schedule) a memory-health pass.** The newest `lint`
      entry in `wiki/log.md` is the cadence anchor; the Obsidian dashboard's
      `HEALTH · DUE` chip flags when 7+ days have passed.
- [ ] **Run `/aos-wiki-lint`** for hygiene (contradictions, orphans, broken links, stale
      claims). Don't claim it ran unless it did.
- [ ] **Run `/aos-promote-draft-memory`** to triage draft/raw material that is ready to
      become curated.
- [ ] **Do not auto-promote raw → curated** without grounding and verification — the
      promotion gates in [Memory Quality](memory-quality.md) still apply.
- [ ] **Do not remove stale/deprecated markers** unless the content was actually
      re-verified this pass.

## Mode-specific quick references

The minimum manual process per [task mode](task-modes.md). "AI review" =
[AI Code Review](ai-code-review.md) applies; "Memory quality" =
[Memory Quality](memory-quality.md) gates apply; "Evals" = an eval may be relevant.

### `exploration`
- **Context:** the code/sources to inspect; relevant project page if any.
- **Checks:** `pre-task` only (no edits).
- **Verification:** findings trace to inspected files/sources; compact block OK.
- **AI review:** no (unless it ends up touching code).
- **Memory quality:** only if a finding is captured (then it is `raw`).
- **Evals:** rarely.
- **Commit:** usually nothing to commit; if notes are filed, commit them explicitly.

### `implementation`
- **Context:** project page + the relevant engineering skill; existing code patterns.
- **Checks:** `pre-task` → `pre-edit` → `post-edit` → `pre-commit`.
- **Verification:** full performed-vs-recommended block.
- **AI review:** **required.**
- **Memory quality:** only if it writes memory.
- **Evals:** the [implementation-verification](evals/cases/implementation-verification.md)
  case is the behavior bar.
- **Commit:** explicit, scope-matching; no `block` finding unresolved.

### `production-change`
- **Context:** project page, current source/runtime behavior, the relevant skill.
- **Checks:** all hooks; **strongest `pre-commit`**; every escalation check is a
  `block`.
- **Verification:** full block **plus an explicit test plan and a human-review gate**;
  an empty "recommended" is suspect.
- **AI review:** **required, strictest, with a human sign-off** before commit/merge.
- **Memory quality:** capture the change as a memory-update candidate afterward.
- **Evals:** highest bar — success criteria, test plan, rollback, honest verification.
- **Commit:** only after human review; message matches scope exactly.

### `hotfix`
- **Context:** the incident + the exact failing area; minimal surrounding code.
- **Checks:** `pre-task` → `pre-edit` (minimal) → `post-edit` → `pre-commit`.
- **Verification:** full block focused on the fix and its **regression risk**.
- **AI review:** **required**, focused on the exact fix.
- **Memory quality:** capture follow-up cleanup if any.
- **Evals:** usually not at the moment; add one if the bug class recurs.
- **Commit:** narrow, explicit; note regression risk in the message/body.

### `research`
- **Context:** the papers/docs/APIs/libraries under study; cite them.
- **Checks:** the source/context checks of `pre-task`; **no edit hooks** unless it
  changes docs.
- **Verification:** sources actually read = performed; PoC/validation = recommended;
  state confidence/applicability limits.
- **AI review:** no (unless code/config is touched).
- **Memory quality:** if filed, it is `raw` or an open question until validated.
- **Evals:** [research-applicability](evals/cases/research-applicability.md) — must
  say what **not** to implement.
- **Commit:** only if research notes are filed; explicit.

### `documentation`
- **Context:** the source/page each claim rests on; flag stale areas.
- **Checks:** `pre-edit`/`post-edit` when files change; `pre-commit` link/index/log
  checks.
- **Verification:** source grounding + link/index/log checks; `/aos-wiki-lint` if run
  (else recommended).
- **AI review:** **only if** the change touches code/config/scripts.
- **Memory quality:** applies when the doc *is* memory (then prefer `memory-update`).
- **Evals:** [context-placement](evals/cases/context-placement.md) if placement is
  in question.
- **Commit:** explicit; index/log updated; no `/aos-wiki-lint` claim unless it ran.

### `memory-update`
- **Context:** the `raw/` source or session facts being captured.
- **Checks:** **`pre-memory-update` always** (its strictest gate); `pre-commit`.
- **Verification:** **strictest** — source/session grounding required under
  *performed*; an ungrounded memory page is blocked, not warned.
- **AI review:** only if it touches code/config.
- **Memory quality:** **central** — declare the category; do not promote raw →
  curated without grounding; mark stale/conflicting content; preserve
  do-not-generalize notes and open questions.
- **Evals:** [memory-update-integrity](evals/cases/memory-update-integrity.md) is the
  bar.
- **Commit:** explicit; `index.md` links new pages; `log.md` newest-first entry.

## Automation candidates

What to automate, in what order, and why. Classified **Built** (implemented in
`scripts/wiki-lint.py` — first five checks 2026-07-02, four more 2026-07-03 —
and pinned by the regression suite in `scripts/tests/` — one clean + one
violating fixture case per check, stdlib runner, 14 tests), **Automate soon**
(deterministic, low-risk checks), **Automate later** (assistant commands /
report-only helpers), and **Defer** (blocking hooks, model routing, complex
observability).

| Manual process | Automate first? | Why | Candidate form | Risk |
| --- | --- | --- | --- | --- |
| Link validation (wiki) | **Built** | Fully deterministic; broken links are common and cheap to detect | `scripts/wiki-lint.py` (run by `/aos-wiki-lint`) | Low |
| Frontmatter / schema validation | **Built** | Mechanical: required keys present, `source:` paths resolve | `scripts/wiki-lint.py` | Low |
| Index coverage (every page linked) | **Built** | Deterministic set diff: pages vs. index entries | `scripts/wiki-lint.py` | Low |
| Log ordering (newest-first, dated, entry size) | **Built** | Mechanical ordering/format/size check | `scripts/wiki-lint.py` | Low |
| Capture `Status:` validity | **Built** | Mechanical: one canonical `Draft`/`Approved` line per capture | `scripts/wiki-lint.py` | Low |
| Eval result format validation | **Built** (2026-07-03) | Deterministic shape check on `results/*.md`: dated filename, matching H1, run-block headings, required fields | `scripts/wiki-lint.py` | Low |
| Skill frontmatter validation | **Built** (2026-07-03) | Mechanical: `name` (matching its directory) + `description` present in every SKILL.md | `scripts/wiki-lint.py` | Low |
| Manual-ops ↔ harness-inventory drift | **Built** (2026-07-03) | Both pages checked against the repo (shared ground truth): script refs resolve, Skills-row list matches disk | `scripts/wiki-lint.py` (warning-level) | Low |
| Required-section validation (workflow pages) | Automate soon | Deterministic presence check for expected headings | `/aos-wiki-lint` sub-check | Low–medium (heading drift) |
| Git stray-file detection | **Built** (2026-07-03) | Filesystem scan flagging temp/generated/scratchpad candidates | `scripts/wiki-lint.py` (warning-level) | Low |
| Skill mirror sync check | **Built** (2026-07-03) | Canonical `skills/aos-*` must match Claude and Codex mirrors | `scripts/sync-skills.py --check` in pre-commit/CI + `scripts/wiki-lint.py` | Low |
| AI code review checklist assistant | Automate later | Speeds the manual read but the judgment stays human | `/ai-code-review` skill emitting the block skeleton | Medium (false confidence if trusted as a gate) |
| Pre-commit checklist assistant | **Built** (2026-07-03) | Report-only helper that walks the checklist and drafts the block | `/aos-pre-commit` skill (advisory; never commits or blocks) | Medium (must stay advisory, not blocking) |
| Report-only assistants (mode skeleton, verification block, hook walk, eval run) | **Built** (2026-07-03) | Each walks an already-proven manual contract and emits its standard block; judgment stays human (`/aos-eval` verdicts on judgment cases need user confirmation) | `/aos-task-mode`, `/aos-verify-block`, `/aos-hook`, `/aos-eval` skills | Medium (false confidence if a report is treated as a gate) |
| Actual blocking git hooks | Defer | Needs the manual contract proven first; a wrong gate blocks real work | git `pre-commit` / Claude Code hook | High (hard stop on false positives) |
| Model routing | Defer | No usage data yet on which mode needs which model; intentionally not started | per-mode routing layer | High (correctness/cost; premature) |

The standing posture (from [Harness Inventory](harness-inventory.md)): keep the
harness lightweight; automate only once the manual discipline proves its shape, and
deterministic checks before judgment-heavy ones.

## Do not automate yet

These need real usage data and human judgment before any automation is safe:

- **Model routing** — no data yet on which mode benefits from which model; deferred
  by design.
- **Blocking hooks** (git / Claude Code) — a mechanical hard stop on a not-yet-proven
  contract blocks legitimate work on false positives. Prove the manual checklist first.
- **Automatic memory promotion** (raw → curated) — promotion is the moment authority
  is granted; it requires the human-judged grounding/scope/over-generalization gates
  in [Memory Quality](memory-quality.md).
- **Automatic stale-marker removal** — removing a stale callout is a verification
  claim; it must follow an actual re-verification, not a script.
- **Automatic code approval** — AI Code Review is a judgment read; a green parse/test
  is necessary, not sufficient.
- **Automatic eval pass/fail without review** — judgment-type evals need a human
  reading; a machine PASS would manufacture false confidence.
- **Automatic production-change approval** — the human-review gate is the whole point;
  it must not be automated away.

**Why, in one line:** each of these is a judgment call whose failure compounds (bad
memory, broken prod, false confidence). Automate the deterministic checks that *feed*
these decisions first; keep the decisions human until repeated manual use shows a
stable, safe rule.

## Related

- [Harness Inventory](harness-inventory.md) — the component map this runbook
  operationalizes (`Agent = Model + Harness`).
- [Task Modes](task-modes.md) — step 1: declare the mode.
- [Context Engineering](context-engineering.md) — step 2: load the right context.
- [Guardrail Hooks](guardrail-hooks.md) — step 3: the per-boundary checklists.
- [Verification](verification.md) — step 5: performed vs. recommended.
- [AI Code Review](ai-code-review.md) — step 6 for code changes.
- [Memory Quality](memory-quality.md) — step 6 for memory changes.
- [Evals](evals.md) — step 6 for behavior checks.
- [Agentic OS Usage Guide](../agentic-os-usage.md) — paths, aliases, skill scoping,
  the daily mental model.
- [`AGENTS.md`](../../AGENTS.md) — the static schema (wins on any conflict).

## Open questions (accepted)

- Whether this runbook should eventually be backed by a single `/session` or
  `/run-checklist` skill that walks the active step's checklist — deferred, same
  posture as the other deferred skills (no automation until the manual process proves
  its shape).
- Whether the stray-candidate check should also flag `.log` files — left out to
  avoid ambiguity with legitimate content.
- Whether the mode quick references drift from [Task Modes](task-modes.md) over time
  and should instead be generated from it — watch for divergence first.
- Whether the pre-commit checklist should gain a "run the linter's own tests"
  line (`python3 scripts/tests/test_wiki_lint.py`, ~0.4 s), or whether that is
  over-ceremony for a suite that only changes when the linter does.
- Whether "a new lint check ships with its own clean + violating fixture pair"
  should become a written rule here, or stay an unwritten practice.
- Whether `scripts/sync-skills.py --check` should be folded into the pre-commit
  checklist or remain a separate explicit check after skill edits.

