---
tags: [agentic-os, usage, workflow]
updated: 2026-07-05
---
# Agentic OS Usage Guide

> Public starter usage notes for operating this repository as an LLM wiki.

## Core Loop

1. Add immutable evidence under `raw/`.
2. Promote durable knowledge into `wiki/` with the ingest workflow.
3. Keep `wiki/index.md` and `wiki/log.md` current.
4. Run deterministic checks before committing.

## Skill Scoping

Use `skills/aos-*` for Agentic OS operations. Project-specific skills belong in the project that owns the domain, not in this public starter repository.

## Git

Commits should be deliberate reviewed checkpoints. Before committing, inspect status and diff, run the relevant checks, and keep private memory out of public history.
