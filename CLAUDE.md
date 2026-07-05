# Claude Code entry point

This repository is an LLM wiki with a strict operating contract.
**Read `AGENTS.md` in full before doing anything else.** It is the schema:
the three-layer model (`raw/` immutable evidence → `wiki/` synthesized memory
→ skills as prompt workflows), the page conventions, and the ingest / query /
lint workflows this repo depends on.

Two rules worth repeating even here:

- **The wiki IS the memory.** `wiki/index.md` is the catalog, `wiki/log.md`
  the activity record. Do not create `memory/`, `MEMORY.md`, or any second
  memory system.
- **Never edit or delete files under `raw/`** — they are evidence. New
  knowledge enters as a new dated `raw/` file and is promoted with `/aos-ingest`.
