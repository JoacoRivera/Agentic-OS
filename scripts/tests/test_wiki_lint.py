#!/usr/bin/env python3
"""Regression tests for scripts/wiki-lint.py.

Stdlib only (unittest + subprocess). Each test composes a throwaway repo from
fixtures/base/ (a minimal clean repo exercising every check positively) plus
one overlay from fixtures/cases/<name>/ (files copied over the base to inject
exactly one class of violation), then runs the linter against it via the
`--root` seam and asserts the exit code, the reported error count, and the
expected ERROR lines.

Run from anywhere:

    python3 scripts/tests/test_wiki_lint.py -v
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SCRIPT = TESTS.parent / "wiki-lint.py"
BASE = TESTS / "fixtures" / "base"
CASES = TESTS / "fixtures" / "cases"


def run_lint(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
    )


class WikiLintTests(unittest.TestCase):
    def build_repo(self, case: str | None = None) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="wiki-lint-fixture-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        shutil.copytree(BASE, tmp, dirs_exist_ok=True)
        if case is not None:
            shutil.copytree(CASES / case, tmp, dirs_exist_ok=True)
        return tmp

    def assert_case_errors(self, case: str, expected_errors: list[str]) -> None:
        """The case must fail with exactly the expected ERROR lines."""
        proc = run_lint(self.build_repo(case))
        self.assertEqual(proc.returncode, 1, msg=proc.stdout + proc.stderr)
        self.assertIn(f"- errors: {len(expected_errors)}", proc.stdout, msg=proc.stdout)
        for fragment in expected_errors:
            self.assertIn(fragment, proc.stdout, msg=proc.stdout)

    def assert_case_warnings(self, case: str, expected_warnings: list[str]) -> None:
        """The case must pass (warnings never fail) with exactly the expected WARNING lines."""
        proc = run_lint(self.build_repo(case))
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("- errors: 0", proc.stdout, msg=proc.stdout)
        self.assertIn(
            f"- warnings: {len(expected_warnings)}", proc.stdout, msg=proc.stdout
        )
        for fragment in expected_warnings:
            self.assertIn(fragment, proc.stdout, msg=proc.stdout)

    # ---- clean base: every check has a passing example -----------------

    def test_clean_base_passes(self):
        proc = run_lint(self.build_repo())
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("- errors: 0", proc.stdout)
        self.assertIn("Clean pass", proc.stdout)

    # ---- check 1: relative links resolve --------------------------------

    def test_broken_link(self):
        self.assert_case_errors(
            "broken-link",
            ["broken link: wiki/page.md -> missing.md"],
        )

    # ---- check 2: frontmatter present with required keys ----------------

    def test_missing_frontmatter(self):
        self.assert_case_errors(
            "missing-frontmatter",
            [
                "missing frontmatter: wiki/no-frontmatter.md",
                "frontmatter missing `updated:`: wiki/missing-key.md",
            ],
        )

    # ---- check 3: frontmatter source paths resolve ----------------------

    def test_missing_source(self):
        self.assert_case_errors(
            "missing-source",
            [
                "frontmatter source missing: wiki/page.md -> "
                "raw/topic/examples/does-not-exist-2026-01-01.md"
            ],
        )

    # ---- check 4: index coverage ----------------------------------------

    def test_unindexed_page(self):
        self.assert_case_errors(
            "unindexed-page",
            ["page not linked from index.md: wiki/orphan.md"],
        )

    # ---- check 5: log heading format, valid op, newest-first ------------

    def test_bad_log_format(self):
        self.assert_case_errors(
            "bad-log-format",
            [
                "invalid log op `oops`: wiki/log.md:6",
                "log entry out of order (newer below older): wiki/log.md:6",
                "malformed log heading: wiki/log.md:9",
            ],
        )

    # ---- check 6: log entry size ----------------------------------------

    def test_oversize_log_entry(self):
        self.assert_case_errors(
            "oversize-log-entry",
            [
                "log entry has 6 bullets (max 5): wiki/log.md:3",
                "log entry body is 11 lines (max 10): wiki/log.md:11",
            ],
        )

    # ---- check 7: capture status ----------------------------------------

    def test_bad_capture_status(self):
        self.assert_case_errors(
            "bad-capture-status",
            [
                "capture needs exactly one Status: line: "
                "raw/topic/examples/no-status-2026-07-02.md",
                "capture Status must be canonical inline `Draft` or `Approved` "
                "(got 'approved'): raw/topic/examples/lowercase-status-2026-07-02.md",
            ],
        )

    # ---- check 8: leaked tool-syntax markers -----------------------------

    def test_leaked_marker(self):
        proc = run_lint(self.build_repo("leaked-marker"))
        self.assertEqual(proc.returncode, 1, msg=proc.stdout + proc.stderr)
        self.assertIn("- errors: 1", proc.stdout, msg=proc.stdout)
        self.assertIn("leaked marker", proc.stdout)
        self.assertIn("wiki/page.md", proc.stdout)

    # ---- check 9: eval result format --------------------------------------

    def test_bad_eval_result(self):
        self.assert_case_errors(
            "bad-eval-result",
            [
                "eval result filename must be YYYY-MM-DD.md: "
                "wiki/workflows/evals/results/notadate.md",
                "eval result H1 must be `# Eval Results — 2026-07-02`: "
                "wiki/workflows/evals/results/2026-07-02.md",
                "malformed eval run heading",
                "eval run block missing field(s) type, must_not_include, "
                "action taken: wiki/workflows/evals/results/2026-07-02.md:13",
            ],
        )

    # ---- check 10: skill frontmatter ---------------------------------------

    def test_bad_skill_frontmatter(self):
        self.assert_case_errors(
            "bad-skill-frontmatter",
            [
                "canonical skill directory must start with `aos-`: skills/bad-prefix-skill",
                "skill missing SKILL.md: skills/aos-empty-skill",
                "skill missing frontmatter: skills/aos-no-frontmatter-skill/SKILL.md",
                "skill frontmatter missing `description:`: "
                "skills/aos-wrong-name-skill/SKILL.md",
                "skill frontmatter name `aos-something-else` != directory "
                "`aos-wrong-name-skill`: skills/aos-wrong-name-skill/SKILL.md",
            ],
        )

    # ---- check 11: harness drift (warnings) --------------------------------

    def test_harness_drift(self):
        self.assert_case_warnings(
            "harness-drift",
            [
                "harness drift: wiki/workflows/harness-inventory.md references "
                "missing scripts/missing.py",
                "harness drift: skill `aos-unlisted-skill` on disk but not in the "
                "harness-inventory.md Skills row",
                "harness drift: skill `aos-ghost-skill` in the harness-inventory.md "
                "Skills row but not on disk",
            ],
        )

    # ---- check 12: stray files (warnings) ----------------------------------

    def test_stray_files(self):
        self.assert_case_warnings(
            "stray-files",
            [
                "stray candidate (generated dir): scripts/__pycache__/",
                "stray candidate (temp/generated): scratch-note.md",
                "stray candidate (temp/generated): wiki/notes.tmp",
            ],
        )

    # ---- the --root seam itself ------------------------------------------

    def test_unlintable_root_exits_2(self):
        tmp = Path(tempfile.mkdtemp(prefix="wiki-lint-notarepo-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        proc = run_lint(tmp)
        self.assertEqual(proc.returncode, 2, msg=proc.stdout + proc.stderr)
        self.assertIn("not a lintable repo root", proc.stderr)


if __name__ == "__main__":
    unittest.main()
