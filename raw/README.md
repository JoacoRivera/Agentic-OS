# raw/ — immutable sources

Original source material the wiki is synthesized from: notes, transcripts,
articles, clips, exports. The agent **reads** from here but **never edits or
deletes** these files. Treat them as evidence.

## Naming convention

Group sources by topic in a subdirectory, and name each file
`slug-YYYY-MM-DD.ext`:

```
raw/<topic>/<slug>-YYYY-MM-DD.ext
```

- `<topic>` — lowercase kebab-case area the source belongs to (e.g. `agentic-os`).
- `slug` — short lowercase kebab-case description.
- `YYYY-MM-DD` — the date the source was created or captured (not ingested).
- `.ext` — the original format (`.md`, `.txt`, `.pdf`, `.html`, …).

Examples:

```
raw/agentic-os/setup-notes-2026-06-26.md
raw/llm-wiki/karpathy-gist-2026-06-26.md
```

Stable, topic-grouped paths make sources citable: wiki pages reference them in
their frontmatter `source:` field and in a `## Sources` section.

### Per-sub-unit grouping

When a topic is split across multiple sub-units (customers, tenants,
sites), group its sources the same way the wiki does (see `AGENTS.md` →
*Per-sub-unit grouping*): one subfolder per unit plus a `general/` subfolder for
sources shared by 2+ units, mirroring the wiki's unit folders so a page and the
raw it cites line up. Drop the redundant unit prefix inside a unit folder; keep
it in `general/` where it disambiguates. Example:

```
raw/projects/example-crm/vault-import-2026-06-27/
  general/        shared-onboarding-process.md
  acme/           user-guide.md
  contoso/        integration-notes.md
```

## Assets

Downloaded images and binary assets go in `raw/assets/`, following the same
naming convention.
