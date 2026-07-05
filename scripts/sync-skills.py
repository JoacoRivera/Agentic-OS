#!/usr/bin/env python3
"""Sync Agentic OS skills from the canonical model-agnostic source.

Canonical skills live under `skills/aos-*`. Derived surfaces are:

- `.claude/skills/aos-*`
- `plugins/agentic-os/skills/aos-*`

Use `--global` to also reconcile user-level Claude and Codex plugin exposure.
Use `--check` to verify without modifying anything.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "skills"
PLUGIN = REPO / "plugins" / "agentic-os"
SURFACES = (
    REPO / ".claude" / "skills",
    PLUGIN / "skills",
)
HOME = Path(os.environ.get("AOS_SYNC_HOME", Path.home()))
GLOBAL_CLAUDE_SKILLS = HOME / ".claude" / "skills"
GLOBAL_PLUGIN_LINK = HOME / "plugins" / "agentic-os"
MARKETPLACE = HOME / ".agents" / "plugins" / "marketplace.json"
MARKETPLACE_SOURCE_PATH = "./plugins/agentic-os"
PLUGIN_NAME = "agentic-os"
PLUGIN_INSTALL_REF = "agentic-os@personal"


def skill_dirs(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        return {}
    return {
        p.name: p
        for p in sorted(root.iterdir())
        if p.is_dir() and p.name.startswith("aos-") and (p / "SKILL.md").is_file()
    }


def dir_equal(left: Path, right: Path) -> bool:
    if not right.is_dir():
        return False
    cmp = filecmp.dircmp(left, right)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(dir_equal(left / name, right / name) for name in cmp.common_dirs)


def validate_source() -> dict[str, Path]:
    skills = skill_dirs(SOURCE)
    if not skills:
        raise SystemExit("No canonical skills found under skills/aos-*")
    bad = [name for name in skills if not name.startswith("aos-")]
    if bad:
        raise SystemExit(f"Canonical skills must be aos-prefixed: {', '.join(bad)}")
    return skills


def check(skills: dict[str, Path]) -> int:
    problems: list[str] = []
    expected = set(skills)
    for surface in SURFACES:
        actual = set(skill_dirs(surface))
        for name in sorted(expected - actual):
            problems.append(f"missing {surface.relative_to(REPO)}/{name}")
        for name in sorted(actual - expected):
            problems.append(f"extra {surface.relative_to(REPO)}/{name}")
        for name in sorted(expected & actual):
            if not dir_equal(skills[name], surface / name):
                problems.append(f"out of sync {surface.relative_to(REPO)}/{name}")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def rel_home(path: Path) -> str:
    try:
        return f"~/{path.relative_to(HOME)}"
    except ValueError:
        return str(path)


def symlink_points_to(path: Path, target: Path) -> bool:
    return path.is_symlink() and path.resolve() == target.resolve()


def read_marketplace() -> dict:
    if not MARKETPLACE.exists():
        return {
            "name": "personal",
            "interface": {"displayName": "Personal"},
            "plugins": [],
        }
    try:
        return json.loads(MARKETPLACE.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {rel_home(MARKETPLACE)}: {exc}") from exc


def marketplace_has_agentic_os(marketplace: dict) -> bool:
    for plugin in marketplace.get("plugins", []):
        if plugin.get("name") != PLUGIN_NAME:
            continue
        source = plugin.get("source", {})
        return (
            source.get("source") == "local"
            and source.get("path") == MARKETPLACE_SOURCE_PATH
        )
    return False


def add_marketplace_plugin(marketplace: dict) -> dict:
    plugins = marketplace.setdefault("plugins", [])
    replacement = {
        "name": PLUGIN_NAME,
        "source": {"source": "local", "path": MARKETPLACE_SOURCE_PATH},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    }
    for index, plugin in enumerate(plugins):
        if plugin.get("name") == PLUGIN_NAME:
            plugins[index] = replacement
            break
    else:
        plugins.append(replacement)
    return marketplace


def check_global(skills: dict[str, Path]) -> int:
    problems: list[str] = []
    expected = set(skills)
    for name, src in skills.items():
        dst = GLOBAL_CLAUDE_SKILLS / name
        if not symlink_points_to(dst, src):
            problems.append(f"global Claude skill link missing/out of sync: {rel_home(dst)}")
    if GLOBAL_CLAUDE_SKILLS.is_dir():
        for child in sorted(GLOBAL_CLAUDE_SKILLS.iterdir()):
            if child.name.startswith("aos-") and child.name not in expected:
                problems.append(f"extra global Claude skill link: {rel_home(child)}")
    if not symlink_points_to(GLOBAL_PLUGIN_LINK, PLUGIN):
        problems.append(
            f"Codex plugin link missing/out of sync: {rel_home(GLOBAL_PLUGIN_LINK)}"
        )
    marketplace = read_marketplace()
    if not marketplace_has_agentic_os(marketplace):
        problems.append(
            f"personal marketplace missing {PLUGIN_NAME} -> {MARKETPLACE_SOURCE_PATH}: "
            f"{rel_home(MARKETPLACE)}"
        )
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def replace_symlink(dst: Path, target: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        if not dst.is_symlink():
            raise SystemExit(
                f"Refusing to replace non-symlink global skill/plugin path: {rel_home(dst)}"
            )
        dst.unlink()
    dst.symlink_to(target)


def sync_global(skills: dict[str, Path]) -> int:
    expected = set(skills)
    for name, src in skills.items():
        dst = GLOBAL_CLAUDE_SKILLS / name
        if not symlink_points_to(dst, src):
            replace_symlink(dst, src)
    if GLOBAL_CLAUDE_SKILLS.is_dir():
        for child in GLOBAL_CLAUDE_SKILLS.iterdir():
            if child.name.startswith("aos-") and child.name not in expected:
                if not child.is_symlink():
                    raise SystemExit(
                        "Refusing to remove non-symlink extra global Claude skill: "
                        f"{rel_home(child)}"
                    )
                child.unlink()

    if not symlink_points_to(GLOBAL_PLUGIN_LINK, PLUGIN):
        replace_symlink(GLOBAL_PLUGIN_LINK, PLUGIN)

    marketplace = read_marketplace()
    if not marketplace_has_agentic_os(marketplace):
        MARKETPLACE.parent.mkdir(parents=True, exist_ok=True)
        MARKETPLACE.write_text(json.dumps(add_marketplace_plugin(marketplace), indent=2) + "\n")

    return check_global(skills)


def install_codex_plugin() -> int:
    try:
        result = subprocess.run(["codex", "plugin", "add", PLUGIN_INSTALL_REF])
    except FileNotFoundError:
        print("codex executable not found; install the Codex CLI or run the plugin add manually.")
        return 127
    if result.returncode == 0:
        print("Codex plugin installed. Start a new Codex thread to refresh $aos-* skills.")
    return result.returncode


def sync(skills: dict[str, Path]) -> int:
    expected = set(skills)
    for surface in SURFACES:
        surface.mkdir(parents=True, exist_ok=True)
        for child in surface.iterdir():
            if child.is_dir() and child.name not in expected:
                shutil.rmtree(child)
        for name, src in skills.items():
            dst = surface / name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    return check(skills)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify without writing")
    parser.add_argument(
        "--global",
        dest="global_sync",
        action="store_true",
        help="also reconcile ~/.claude/skills and the personal Codex plugin pointer",
    )
    parser.add_argument(
        "--install-codex",
        action="store_true",
        help="run `codex plugin add agentic-os@personal` after a successful global sync",
    )
    args = parser.parse_args(argv)
    skills = validate_source()
    status = check(skills) if args.check else sync(skills)
    if args.global_sync and status == 0:
        status = check_global(skills) if args.check else sync_global(skills)
    if args.install_codex:
        if args.check:
            print("--install-codex is ignored with --check")
        elif not args.global_sync:
            print("--install-codex requires --global")
            status = 2
        elif status == 0:
            status = install_codex_plugin()
    elif args.global_sync and not args.check and status == 0:
        print(
            "Codex plugin pointer reconciled. Run "
            "`python3 scripts/sync-skills.py --global --install-codex` or "
            f"`codex plugin add {PLUGIN_INSTALL_REF}`, then start a new Codex thread."
        )
    return status


if __name__ == "__main__":
    sys.exit(main())
