# Agentic OS

Agentic OS is a lightweight operating system for durable agent memory. It turns a
repository into an LLM wiki: immutable source material goes in `raw/`, synthesized
knowledge goes in `wiki/`, and reusable operating procedures live in `skills/`.

The goal is to make agent work compound across sessions without hiding where facts
came from. Agents read the schema in `AGENTS.md`, retrieve only the dynamic context
needed for the task, update memory with citations, and separate checks they actually
performed from checks still recommended.

## What This Repo Provides

- A public starter schema for the LLM-wiki pattern in `AGENTS.md`.
- A three-layer memory layout: `raw/`, `wiki/`, and schema/workflow instructions.
- Model-agnostic `skills/aos-*` prompts for ingesting memory, querying memory,
  linting wiki health, planning changes, implementing changes, running guardrail
  checklists, and recording evals.
- A Codex plugin mirror under `plugins/agentic-os/`.
- Claude/Codex mirror synchronization tooling in `scripts/sync-skills.py`.
- Deterministic wiki checks in `scripts/wiki-lint.py`.
- A small public workflow wiki covering task modes, verification discipline,
  guardrail hooks, evals, context placement, memory quality, and manual operations.

This repository intentionally does not include private project memory. It is a
starter harness, not an exported working vault.

## Repository Layout

```text
.
|-- AGENTS.md                         # Canonical schema and operating rules
|-- CLAUDE.md                         # Claude-facing pointer to the schema
|-- README.md                         # GitHub project overview and usage
|-- raw/                              # Immutable source evidence
|   |-- README.md                     # Raw source naming convention
|   `-- assets/                       # Binary/source assets
|-- wiki/                             # Synthesized, linked memory
|   |-- index.md                      # Human-facing wiki catalog
|   |-- log.md                        # Grow-only activity log
|   |-- agentic-os-setup.md
|   |-- agentic-os-usage.md
|   `-- workflows/                    # Workflow and guardrail documentation
|-- skills/                           # Canonical Agentic OS skill prompts
|-- plugins/agentic-os/               # Codex plugin mirror
|-- scripts/
|   |-- sync-skills.py                # Skill mirror check/sync tool
|   |-- wiki-lint.py                  # Deterministic wiki health checks
|   `-- tests/                        # Stdlib unittest coverage for scripts
`-- templates/                        # Starter capture/example templates
```

## Core Concepts

### `raw/` Is Evidence

Store original notes, transcripts, articles, exports, and captured examples under
`raw/`. Agents may read these files, but should not rewrite or delete them. Name
sources as:

```text
raw/<topic>/<slug>-YYYY-MM-DD.ext
```

Downloaded images and binary assets belong in `raw/assets/`.

### `wiki/` Is Synthesized Memory

The wiki contains compact, linked Markdown pages generated from sources and
session-grounded work. Pages use frontmatter for retrieval and trust:

```markdown
---
tags: [topic, example]
source: [raw/topic/source-2026-07-05.md]
updated: 2026-07-05
---
```

Use `wiki/index.md` as the catalog and `wiki/log.md` as the activity record.

### `skills/` Is Procedure, Not Memory

Skills are reusable workflow prompts. They describe how to perform operations such
as ingesting raw files, querying memory, linting the wiki, planning a change, or
implementing a change with guardrail checks.

Canonical skill sources live in `skills/aos-*`. Generated mirrors expose the same
procedures to Claude and Codex.

## Requirements

- Python 3.
- Git.
- No third-party Python packages are required for the included checks.

## Quick Start

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd agentic-os-public
   ```

2. Read the schema:

   ```bash
   sed -n '1,220p' AGENTS.md
   ```

3. Run the deterministic checks:

   ```bash
   python3 scripts/sync-skills.py --check
   python3 -B -m unittest discover scripts/tests -v
   python3 scripts/wiki-lint.py
   ```

4. Add source material under `raw/`.

5. Use the ingest workflow to synthesize durable facts into `wiki/`.

6. Keep `wiki/index.md` and `wiki/log.md` current when memory changes.

## Daily Usage

### Start a Session

Read `AGENTS.md` first. It defines the repository schema, global rules, and
workflow pointers. For non-trivial work, classify the task mode before acting:

- `exploration` for investigation without edits.
- `documentation` for docs and workflow edits.
- `memory-update` for raw-to-wiki memory work.
- `implementation`, `hotfix`, or `production-change` for code-bearing work.
- `research` for external source review.

### Add New Source Material

Place original material in `raw/` using stable, dated paths:

```text
raw/agentic-os/example-notes-2026-07-05.md
```

Do not summarize only in the filename. The source should contain the evidence
future agents need to cite.

### Ingest a Source Into Memory

The ingest loop is:

1. Read the raw source.
2. Create or update focused pages under `wiki/`.
3. Cite the raw file in frontmatter and in a `## Sources` section when claims
   depend on it.
4. Add or update links in `wiki/index.md`.
5. Prepend a concise entry to `wiki/log.md`.
6. Run `python3 scripts/wiki-lint.py`.

### Query Existing Memory

Before answering from memory, search the wiki first. Use tags, titles, and
`wiki/index.md` to find relevant pages. Fall back to `raw/` only when the
synthesized page needs evidence or the wiki is incomplete.

### Maintain Wiki Health

Run the linter before commits and after meaningful memory changes:

```bash
python3 scripts/wiki-lint.py
```

The script checks mechanical issues such as frontmatter, source paths, index
coverage, log formatting, capture status markers, eval result shape, skill
frontmatter, and known drift signals. Judgment checks still require human review:
contradictions, stale claims, missing cross-links, and raw-dump drift.

## Using the Skills

The canonical skills are in `skills/aos-*`.

Common operations:

- `aos-query-memory` - read and summarize what the wiki already knows.
- `aos-ingest` - synthesize one or more files from `raw/` into `wiki/`.
- `aos-wiki-lint` - run deterministic and judgment wiki-health checks.
- `aos-plan` - plan an Agentic OS change without editing.
- `aos-implement` - implement a change with task mode classification,
  context loading, guardrail checks, verification split, and diff review.
- `aos-pre-commit` - walk the advisory pre-commit checklist.
- `aos-capture-approved-example` - capture an approved result as a draft raw
  example for later ingestion.

In Codex, these are exposed as `$aos-*` skills when the plugin is installed. In
Claude, use the mirrored slash-command skills.

## Codex Plugin

The Codex plugin lives at:

```text
plugins/agentic-os/
```

Its manifest is:

```text
plugins/agentic-os/.codex-plugin/plugin.json
```

The plugin exposes the Agentic OS skills for querying and maintaining the wiki,
running report-only guardrails, checking verification discipline, and planning or
implementing changes.

After changing canonical skills, refresh/check mirrors:

```bash
python3 scripts/sync-skills.py
python3 scripts/sync-skills.py --check
```

Use the global mode when you also want to reconcile user-level Claude/Codex
exposure on a local machine:

```bash
python3 scripts/sync-skills.py --global
```

## Verification Commands

Run these before opening a pull request or committing a meaningful change:

```bash
python3 scripts/sync-skills.py --check
python3 -B -m unittest discover scripts/tests -v
python3 scripts/wiki-lint.py
```

Use the test suite when changing scripts:

```bash
python3 -B -m unittest discover scripts/tests -v
```

Use the sync check whenever `skills/`, Claude mirrors, or Codex plugin mirrors
change:

```bash
python3 scripts/sync-skills.py --check
```

## Safety Rules

- Do not store secrets: no passwords, API keys, private keys, tokens, or
  production credentials.
- Do not invent facts. Mark uncertainty explicitly.
- Preserve `raw/` sources as evidence.
- Prefer many focused linked pages over one giant wiki page.
- Keep `wiki/log.md` concise, dated, and grow-only in substance.
- Separate verification performed from verification recommended.

## Public Starter Scope

This repository is designed to be safe to publish. It excludes private raw
sources, private project wiki pages, and historical logs from a working vault.
When adapting it for a real project, keep private project memory in that
project's own repository or vault.

## License

No license file is currently included. Treat reuse rights as unspecified until a
license is added.
