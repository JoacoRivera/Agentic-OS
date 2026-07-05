---
name: aos-wiki-lint
description: Check the Agentic OS Markdown wiki for schema, index, log, consistency, and memory hygiene issues. Use before commits or after multiple ingests.
---

# Wiki Lint Skill

Use this skill to inspect the Agentic OS Markdown wiki for structural and memory-quality issues.

## Scope

Memory repo:

```text
~/agents/agentic-os
```

Check:

- `AGENTS.md`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/**/*.md`

Do not treat skills (`skills/`, or the legacy `skills/` pointer) as memory.

Do not edit `raw/`.

## Deterministic checks — run the script first

Always start by running the deterministic linter from the repo root:

```bash
python3 scripts/wiki-lint.py
```

It mechanically covers: broken relative links (wiki + `AGENTS.md`), frontmatter
presence/keys, frontmatter `source:` paths resolving to real files, index
coverage, dead index links, log heading format/op/order, log entry size,
capture `Status:` validity, leaked tool-syntax markers, eval result file format
(`results/YYYY-MM-DD.md` naming, H1, run-block headings and required fields),
skill frontmatter (`skills/*/SKILL.md` — `name` matching its directory
+ `description`), harness drift as warnings (script references in
manual-operations/harness-inventory resolve; the inventory's Skills-row list
matches the skills on disk), and stray temp/generated/scratchpad file
candidates as warnings. Report its output
verbatim in the lint report (errors → Critical issues, warnings → Warnings).
Do not re-derive those checks by hand — spend the manual pass on the judgment
checks below (contradictions, raw-dump drift, invented certainty, hygiene).

If the script itself fails to run, say so under Critical issues; never claim
it ran when it did not.

This skill lints wiki **content**. To test the **linter itself** after editing
`scripts/wiki-lint.py`, use the sibling `/aos-test-wiki-lint`
(`skills/aos-test-wiki-lint/SKILL.md`), which runs the regression suite.

## Rules

- Do not modify files unless the user explicitly asks for fixes.
- Do not invent missing facts.
- Do not promote single-example observations into general rules.
- Preserve TODOs and unknowns as open questions.
- Treat `raw/` as immutable source material.
- Treat `wiki/index.md` as the catalog.
- Treat `wiki/log.md` as grow-only, newest entries first.

## Checks

Checks 1–5 (and the mechanical half of 6) are covered by `scripts/wiki-lint.py`
— run it instead of walking them by hand. Checks 7–8 and the judgment half of 6
require reading pages; do those manually.

### 1. Frontmatter

Every normal wiki page should have YAML frontmatter:

```yaml
tags:
source:
updated:
```

Flag pages with missing or malformed frontmatter.

### 2. Index coverage

Check whether important wiki pages are listed in:

- `wiki/index.md`

Flag orphaned wiki pages.

### 3. Dead index links

Check whether entries in `wiki/index.md` point to missing files.

### 4. Log format

Check `wiki/log.md`.

Expected heading format:

```text
## [YYYY-MM-DD] <op> | <subject>
```

Valid ops:

- `ingest`
- `query`
- `lint`
- `schema`

Flag malformed entries.

### 5. Log order

Newest entries should appear first.

Flag entries that appear out of chronological order.

### 6. Source references

Check that wiki pages reference their source raw files when applicable.

Flag missing source references.

### 7. Open questions

Check whether TODOs, unknowns, or missing details are preserved as open questions.

Flag suspiciously invented certainty.

### 8. Memory hygiene

Flag:

- duplicated facts across sibling pages,
- over-detailed wiki pages that look like raw dumps,
- full drafts copied into wiki pages,
- single-example patterns promoted as general rules,
- stale/conflicting claims without conflict notes,
- skills treated as memory.

## Output format

```text
## Wiki lint report

### Summary
- Status:
- Files checked:
- Issues found:

### Critical issues
-

### Warnings
-

### Suggestions
-

### Suggested fixes
-

### No-change confirmation
- I did not modify files.
```

If the user asks to fix issues, make minimal edits and report the diff.
