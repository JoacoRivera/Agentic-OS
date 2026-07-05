#!/usr/bin/env python3
"""Regression tests for scripts/sync-skills.py."""
from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


TESTS = Path(__file__).resolve().parent
SCRIPT = TESTS.parent / "sync-skills.py"


def load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_skills_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_skill(root: Path, name: str, body: str = "Body\n") -> None:
    skill = root / "skills" / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill.\n---\n\n# {name}\n\n{body}"
    )


class SyncSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="sync-skills-fixture-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        self.home = self.tmp / "home"
        (self.repo / "plugins" / "agentic-os").mkdir(parents=True)
        self.home.mkdir()
        write_skill(self.repo, "aos-demo")

        self.sync = load_sync_module()
        self.sync.REPO = self.repo
        self.sync.SOURCE = self.repo / "skills"
        self.sync.PLUGIN = self.repo / "plugins" / "agentic-os"
        self.sync.SURFACES = (
            self.repo / ".claude" / "skills",
            self.repo / "plugins" / "agentic-os" / "skills",
        )
        self.sync.HOME = self.home
        self.sync.GLOBAL_CLAUDE_SKILLS = self.home / ".claude" / "skills"
        self.sync.GLOBAL_PLUGIN_LINK = self.home / "plugins" / "agentic-os"
        self.sync.MARKETPLACE = self.home / ".agents" / "plugins" / "marketplace.json"

    def test_global_sync_links_claude_and_codex_surfaces(self):
        skills = self.sync.validate_source()

        self.assertEqual(self.sync.sync(skills), 0)
        self.assertEqual(self.sync.sync_global(skills), 0)

        claude_link = self.home / ".claude" / "skills" / "aos-demo"
        self.assertTrue(claude_link.is_symlink())
        self.assertEqual(claude_link.resolve(), (self.repo / "skills" / "aos-demo").resolve())

        plugin_link = self.home / "plugins" / "agentic-os"
        self.assertTrue(plugin_link.is_symlink())
        self.assertEqual(plugin_link.resolve(), (self.repo / "plugins" / "agentic-os").resolve())

        marketplace = self.sync.read_marketplace()
        self.assertTrue(self.sync.marketplace_has_agentic_os(marketplace))
        self.assertEqual(self.sync.check_global(skills), 0)

    def test_global_check_reports_missing_links_without_writing(self):
        skills = self.sync.validate_source()

        self.assertEqual(self.sync.check_global(skills), 1)
        self.assertFalse((self.home / ".claude").exists())
        self.assertFalse((self.home / "plugins").exists())
        self.assertFalse((self.home / ".agents").exists())

    def test_global_sync_refuses_to_replace_non_symlink(self):
        skills = self.sync.validate_source()
        blocking_path = self.home / ".claude" / "skills" / "aos-demo"
        blocking_path.mkdir(parents=True)

        with self.assertRaises(SystemExit):
            self.sync.sync_global(skills)

    def test_global_sync_removes_only_extra_aos_symlinks(self):
        skills = self.sync.validate_source()
        stale_target = self.tmp / "stale-skill"
        stale_target.mkdir()
        stale_link = self.home / ".claude" / "skills" / "aos-stale"
        unrelated_target = self.tmp / "unrelated-skill"
        unrelated_target.mkdir()
        unrelated_link = self.home / ".claude" / "skills" / "diagnosing-bugs"
        stale_link.parent.mkdir(parents=True)
        stale_link.symlink_to(stale_target)
        unrelated_link.symlink_to(unrelated_target)

        self.assertEqual(self.sync.sync_global(skills), 0)

        self.assertFalse(stale_link.exists())
        self.assertTrue(unrelated_link.is_symlink())


if __name__ == "__main__":
    unittest.main()
