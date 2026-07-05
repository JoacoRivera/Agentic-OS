# Agentic OS

Agentic OS is a lightweight LLM-wiki operating system for maintaining durable agent memory.

The repository separates immutable source material (`raw/`), synthesized memory (`wiki/`), and reusable workflow prompts (`skills/`). `AGENTS.md` is the schema and should be read at the start of each agent session.

## Included

- Agentic OS schema (`AGENTS.md`, `CLAUDE.md`)
- Canonical `skills/aos-*` prompts
- Claude and Codex skill/plugin mirrors
- Deterministic wiki and skill checks under `scripts/`
- Public starter wiki workflow pages and eval cases
- Empty raw/memory starter structure

## Not Included

This public repository intentionally excludes private memory: no project raw sources, no project wiki pages, and no historical operation log from a working vault.

## Checks

```bash
python3 scripts/sync-skills.py --check
python3 -B -m unittest discover scripts/tests -v
python3 scripts/wiki-lint.py
```
