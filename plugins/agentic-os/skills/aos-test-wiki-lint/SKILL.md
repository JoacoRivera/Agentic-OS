---
name: aos-test-wiki-lint
description: Run the regression suite for scripts/wiki-lint.py. Use after editing the linter (a check's logic, a message, an exit code, or the --root seam) to confirm it still behaves correctly. This tests the linter itself, not the wiki content.
---

# Test Wiki Lint Skill

Use this skill to run the **regression tests for the linter itself**
(`scripts/wiki-lint.py`), not to lint the wiki. Reach for it whenever you change
`scripts/wiki-lint.py` — a check's logic, an error message, an exit code, the
`--root` seam, or when you add a new check.

## Distinction (do not confuse the two)

- `/aos-wiki-lint` → runs `scripts/wiki-lint.py` against the **real repo** to check
  whether the **wiki content** is healthy.
- `/aos-test-wiki-lint` (this skill) → runs `scripts/tests/test_wiki_lint.py` to check
  whether the **linter itself** still works. It composes throwaway fixture repos
  (a clean base + one violating overlay per check) and asserts the linter's exit
  code, error count, and error lines via the `--root` seam.

Neither blocks anything; both are report-only.

## Scope

Memory repo:

```text
~/agents/agentic-os
```

Relevant files (do not need to be read to run — listed for orientation):

- `scripts/wiki-lint.py` — the linter under test.
- `scripts/tests/test_wiki_lint.py` — the stdlib `unittest` runner.
- `scripts/tests/fixtures/base/` — the clean fixture repo (every check passes).
- `scripts/tests/fixtures/cases/<name>/` — one violating overlay per check.

## Run it

From the repo root (or anywhere inside the repo):

```bash
python3 scripts/tests/test_wiki_lint.py -v
```

Stdlib only — no dependencies, no network, no CI. A run takes well under a
second. Exit code 0 = all tests pass, non-zero = at least one failure.

## Rules

- Report the runner's output verbatim: the pass/fail line and, on failure, the
  failing test names and their assertion diffs. Never claim it passed when it did
  not.
- If the runner itself fails to start (e.g. a `python3` or import error), say so
  plainly under the result — that is a real failure, not a pass.
- Do not edit `scripts/wiki-lint.py`, the tests, or the fixtures unless the user
  asks. A failing test usually means the *linter* regressed — fix the linter, not
  the test. Only edit a test or fixture when the expectation itself was wrong
  (an intended message/behavior change), and say which case you changed and why.
- When adding a new linter check, add it here too: a clean fixture (so the base
  still passes) plus one violating overlay under `fixtures/cases/`, and a test
  asserting the new ERROR. Keep one violation class per overlay.
- Treat `raw/` as immutable; the fixtures under `scripts/tests/fixtures/` are the
  only "wiki/raw-looking" files you may edit, and they are deliberately outside
  `wiki/` and `raw/` so the real linter never sees them.

## Output format

```text
## Wiki-lint test report

### Result
- Command: python3 scripts/tests/test_wiki_lint.py
- Status: PASS | FAIL
- Tests run:

### Failures (if any)
- <test name> — <assertion summary>

### Notes
-
```

## Related

- `skills/aos-wiki-lint/SKILL.md` — the sibling that lints wiki content.
- `wiki/workflows/harness-inventory.md`
  — the Deterministic-wiki-lint row records this regression suite.
- `wiki/workflows/manual-operations.md`
  — automation-candidates table; the pre-commit checklist.
