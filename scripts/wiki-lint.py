#!/usr/bin/env python3
"""Deterministic wiki lint for the Agentic OS memory repo.

Mechanical checks only — judgment checks (contradictions, raw-dump drift,
invented certainty) stay manual in the /aos-wiki-lint skill. Run from the repo
root (or anywhere inside the repo):

    python3 scripts/wiki-lint.py [--root PATH]

Exit code 0 = no errors (warnings allowed), 1 = at least one error,
2 = the root is not a lintable repo (wiki/index.md, wiki/log.md, or
AGENTS.md missing). `--root` points the linter at another repo tree; it
exists as the seam for the regression tests in scripts/tests/.

Checks:
  1. Relative .md links resolve (wiki/**, AGENTS.md; code blocks/spans and
     placeholder targets ignored; _template.md files skipped).
  2. Frontmatter present with `tags:` + `updated:` on every wiki page except
     index.md and log.md.
  3. Frontmatter `source:` raw/ paths resolve to real files.
  4. Index coverage: every wiki page is linked from wiki/index.md (index.md,
     log.md, _template.md, and dated files under evals/results/ exempt).
  5. Log headings match `## [YYYY-MM-DD] <op> | <subject>` with a valid op,
     and dates are newest-first.
  6. Log entry size: 1-5 bullets and at most 10 body lines per entry.
  7. Capture status: every raw/**/examples/*.md (except _template.md) carries
     exactly one canonical inline `Status: Draft` or `Status: Approved` line.
  8. No leaked tool-syntax markers in wiki/ or AGENTS.md.
  9. Eval result files (wiki/workflows/evals/results/*.md, README/_template
     exempt): dated filename, matching `# Eval Results — <date>` H1, and every
     run block a `## eval-<slug> — PASS|PARTIAL|FAIL` heading carrying the
     required fields (target, type, must_include, must_not_include,
     verification, action taken).
 10. Skill frontmatter/sync: every skills/aos-* directory carries SKILL.md with
     `name:` (matching its directory), `description:`, and the `aos-` prefix;
     .claude/skills/ and plugins/agentic-os/skills/ mirror the canonical set.
 11. Harness drift (warnings): manual-operations.md / harness-inventory.md
     script references resolve, and the harness-inventory Skills-row list
     matches the skills actually on disk.
 12. Stray files (warnings): temp/generated/scratchpad candidates anywhere in
     the repo (.git, .obsidian, inbox/, and the linter's own test fixtures
     excluded).
"""
import argparse
import filecmp
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WIKI = REPO / "wiki"
RAW = REPO / "raw"
CANONICAL_SKILLS = REPO / "skills"
CLAUDE_SKILLS = REPO / ".claude" / "skills"
CODEX_SKILLS = REPO / "plugins" / "agentic-os" / "skills"
VALID_OPS = {"ingest", "query", "lint", "schema"}
LOG_MAX_BULLETS = 5
LOG_MAX_BODY_LINES = 10
LEAK_MARKERS = ("</invoke>", "</content>", "<system-reminder")
EVAL_RUN_HEADING = re.compile(
    r"^## eval-[a-z0-9-]+(?: \([^)]+\))? — (?:PASS|PARTIAL|FAIL)(?: \([^)]+\))?$"
)
EVAL_RUN_FIELDS = (
    "target",
    "type",
    "must_include",
    "must_not_include",
    "verification",
    "action taken",
)
DRIFT_PAGES = ("manual-operations.md", "harness-inventory.md")
STRAY_SUFFIXES = (".tmp", ".bak", ".orig", ".rej", ".swp", ".pyc", "~")
STRAY_DIR_NAMES = {"__pycache__", "node_modules"}
STRAY_FILE_NAMES = {".DS_Store", "Thumbs.db"}
STRAY_SKIP_DIRS = {".git", ".obsidian", "inbox"}

errors: list[str] = []
warnings: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def strip_code(text: str) -> str:
    """Remove fenced code blocks and inline code spans."""
    out, fenced = [], False
    for line in text.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


def frontmatter(text: str) -> str | None:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else None


def md_files(root: Path):
    return sorted(p for p in root.rglob("*.md"))


# ---- 1. relative links ------------------------------------------------------
def check_links():
    files = [p for p in md_files(WIKI) if p.name != "_template.md"]
    files.append(REPO / "AGENTS.md")
    for f in files:
        text = strip_code(f.read_text())
        for m in re.finditer(r"\]\(([^)#\s]+?\.md)(#[^)]*)?\)", text):
            target = m.group(1)
            if target.startswith(("http://", "https://")) or "<" in target:
                continue
            resolved = (f.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"broken link: {rel(f)} -> {target}")


# ---- 2 + 3. frontmatter -----------------------------------------------------
def check_frontmatter():
    for f in md_files(WIKI):
        if f.name in ("index.md", "log.md"):
            continue
        fm = frontmatter(f.read_text())
        if fm is None:
            errors.append(f"missing frontmatter: {rel(f)}")
            continue
        for key in ("tags", "updated"):
            if not re.search(rf"^{key}\s*:", fm, re.M):
                errors.append(f"frontmatter missing `{key}:`: {rel(f)}")
        if f.name == "_template.md":
            continue
        for sm in re.finditer(r"raw/[^\s\]\)\"',]+", fm):
            src = sm.group(0).rstrip(".,")
            if "<" in src:
                continue
            if not (REPO / src).exists():
                errors.append(f"frontmatter source missing: {rel(f)} -> {src}")


# ---- 4. index coverage ------------------------------------------------------
def check_index():
    index = WIKI / "index.md"
    linked = set(re.findall(r"\]\(([^)#\s]+?\.md)\)", index.read_text()))
    for f in md_files(WIKI):
        r = str(f.relative_to(WIKI))
        if f.name in ("index.md", "log.md", "_template.md"):
            continue
        if "evals/results/" in r and f.name != "README.md":
            continue
        if r not in linked:
            errors.append(f"page not linked from index.md: wiki/{r}")


# ---- 5 + 6. log format, order, entry size ----------------------------------
def check_log():
    log = WIKI / "log.md"
    lines = log.read_text().splitlines()
    entries = []  # (lineno, date, body_lines)
    current = None
    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            m = re.match(r"^## \[(\d{4}-\d{2}-\d{2})\] (\S+) \| .+$", line)
            if not m:
                errors.append(f"malformed log heading: wiki/log.md:{i}: {line[:60]}")
                current = None
                continue
            d, op = m.group(1), m.group(2)
            try:
                d = date.fromisoformat(d)
            except ValueError:
                errors.append(f"invalid log date: wiki/log.md:{i}: {m.group(1)}")
                current = None
                continue
            if op not in VALID_OPS:
                errors.append(f"invalid log op `{op}`: wiki/log.md:{i}")
            current = (i, d, [])
            entries.append(current)
        elif current is not None and line.strip():
            current[2].append(line)
    prev = None
    for lineno, d, body in entries:
        if prev is not None and d > prev:
            errors.append(f"log entry out of order (newer below older): wiki/log.md:{lineno}")
        prev = d
        bullets = sum(1 for l in body if re.match(r"^- ", l))
        if bullets == 0:
            errors.append(f"log entry has no bullets: wiki/log.md:{lineno}")
        if bullets > LOG_MAX_BULLETS:
            errors.append(
                f"log entry has {bullets} bullets (max {LOG_MAX_BULLETS}): wiki/log.md:{lineno}"
            )
        if len(body) > LOG_MAX_BODY_LINES:
            errors.append(
                f"log entry body is {len(body)} lines (max {LOG_MAX_BODY_LINES}): wiki/log.md:{lineno}"
            )


# ---- 7. capture status ------------------------------------------------------
def check_captures():
    for f in md_files(RAW):
        if f.parent.name != "examples" or f.name == "_template.md":
            continue
        statuses = re.findall(r"^Status:(.*)$", f.read_text(), re.M)
        if len(statuses) != 1:
            errors.append(f"capture needs exactly one Status: line: {rel(f)}")
            continue
        value = statuses[0].strip()
        if value not in ("Draft", "Approved"):
            errors.append(
                f"capture Status must be canonical inline `Draft` or `Approved` "
                f"(got {value!r}): {rel(f)}"
            )


# ---- 8. leaked tool syntax --------------------------------------------------
def check_leaks():
    # Code spans/fences are stripped first so a *documented* marker (in
    # backticks) is fine; a bare leaked marker is not.
    for f in [*md_files(WIKI), REPO / "AGENTS.md"]:
        text = strip_code(f.read_text())
        for marker in LEAK_MARKERS:
            if marker in text:
                errors.append(f"leaked marker `{marker}` in {rel(f)}")


# ---- 9. eval result format --------------------------------------------------
def check_eval_results():
    results = WIKI / "workflows" / "evals" / "results"
    if not results.is_dir():
        return
    for f in md_files(results):
        if f.name in ("README.md", "_template.md"):
            continue
        try:
            expected_date = date.fromisoformat(f.stem).isoformat()
        except ValueError:
            errors.append(f"eval result filename must be YYYY-MM-DD.md: {rel(f)}")
            continue
        lines = strip_code(f.read_text()).splitlines()
        h1 = next((l for l in lines if l.startswith("# ")), None)
        expected_h1 = f"# Eval Results — {expected_date}"
        if h1 != expected_h1:
            errors.append(f"eval result H1 must be `{expected_h1}`: {rel(f)}")
        blocks = []  # (lineno, field names seen)
        current = None
        for i, line in enumerate(lines, 1):
            if line.startswith("## "):
                if not EVAL_RUN_HEADING.match(line):
                    errors.append(
                        f"malformed eval run heading (want `## eval-<slug> — "
                        f"PASS|PARTIAL|FAIL`): {rel(f)}:{i}: {line[:60]}"
                    )
                    current = None
                    continue
                current = (i, set())
                blocks.append(current)
            elif current is not None:
                m = re.match(r"^- ([a-z_ ]+):", line)
                if m:
                    current[1].add(m.group(1))
        if not blocks:
            errors.append(f"eval result file has no run blocks: {rel(f)}")
        for lineno, fields in blocks:
            missing = [k for k in EVAL_RUN_FIELDS if k not in fields]
            if missing:
                errors.append(
                    f"eval run block missing field(s) "
                    f"{', '.join(missing)}: {rel(f)}:{lineno}"
                )


# ---- 10. skill frontmatter / sync -------------------------------------------
def skill_dirs(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        return {}
    return {d.name: d for d in sorted(root.iterdir()) if d.is_dir()}


def dirs_equal(left: Path, right: Path) -> bool:
    if not right.is_dir():
        return False
    cmp = filecmp.dircmp(left, right)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(dirs_equal(left / name, right / name) for name in cmp.common_dirs)


def check_skill_root(root: Path, label: str) -> set[str]:
    names: set[str] = set()
    if not root.is_dir():
        errors.append(f"skill root missing: {rel(root)}")
        return names
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        if not d.name.startswith("aos-"):
            errors.append(f"{label} skill directory must start with `aos-`: {rel(d)}")
            continue
        sf = d / "SKILL.md"
        if not sf.is_file():
            errors.append(f"skill missing SKILL.md: {rel(d)}")
            continue
        fm = frontmatter(sf.read_text())
        if fm is None:
            errors.append(f"skill missing frontmatter: {rel(sf)}")
            continue
        for key in ("name", "description"):
            if not re.search(rf"^{key}\s*:\s*\S", fm, re.M):
                errors.append(f"skill frontmatter missing `{key}:`: {rel(sf)}")
        m = re.search(r"^name\s*:\s*(\S+)", fm, re.M)
        if m and m.group(1) != d.name:
            errors.append(
                f"skill frontmatter name `{m.group(1)}` != directory "
                f"`{d.name}`: {rel(sf)}"
            )
            continue
        if not re.search(r"^description\s*:\s*\S", fm, re.M):
            continue
        names.add(d.name)
    return names


def check_skills():
    if not CANONICAL_SKILLS.is_dir():
        return
    canonical = check_skill_root(CANONICAL_SKILLS, "canonical")
    for surface in (CLAUDE_SKILLS, CODEX_SKILLS):
        actual = check_skill_root(surface, "derived")
        for name in sorted(canonical - actual):
            errors.append(f"derived skill missing: {rel(surface / name)}")
        for name in sorted(actual - canonical):
            errors.append(f"derived skill not in canonical source: {rel(surface / name)}")
        for name in sorted(canonical & actual):
            if not dirs_equal(CANONICAL_SKILLS / name, surface / name):
                errors.append(f"derived skill out of sync: {rel(surface / name)}")


# ---- 11. harness drift (warnings) -------------------------------------------
def check_harness_drift():
    # The two pages drift apart from each other via the repo: both name the
    # same scripts/skills, so both are checked against what is on disk.
    pages = [WIKI / "workflows" / name for name in DRIFT_PAGES]
    for page in pages:
        if not page.is_file():
            continue
        text = page.read_text()
        for ref in sorted(set(re.findall(r"scripts/[\w./-]+\.\w+", text))):
            if not (REPO / ref).exists():
                warnings.append(f"harness drift: {rel(page)} references missing {ref}")
    inventory = pages[1]
    if not (inventory.is_file() and CANONICAL_SKILLS.is_dir()):
        return
    m = re.search(r"`skills/`\s*\(([^)]*)\)", inventory.read_text())
    if m is None:
        warnings.append(
            "harness drift: no `skills/` (`…`) list found in the "
            "harness-inventory.md Skills row"
        )
        return
    listed = set(re.findall(r"`([\w-]+)`", m.group(1)))
    on_disk = {
        d.name for d in CANONICAL_SKILLS.iterdir() if (d / "SKILL.md").is_file()
    }
    for name in sorted(on_disk - listed):
        warnings.append(
            f"harness drift: skill `{name}` on disk but not in the "
            f"harness-inventory.md Skills row"
        )
    for name in sorted(listed - on_disk):
        warnings.append(
            f"harness drift: skill `{name}` in the harness-inventory.md "
            f"Skills row but not on disk"
        )


# ---- 12. stray files (warnings) ----------------------------------------------
def check_strays():
    fixtures = REPO / "scripts" / "tests" / "fixtures"

    def walk(d: Path):
        for p in sorted(d.iterdir()):
            if p.is_dir():
                if p.name in STRAY_SKIP_DIRS or p == fixtures:
                    continue
                if p.name in STRAY_DIR_NAMES:
                    warnings.append(f"stray candidate (generated dir): {rel(p)}/")
                    continue
                walk(p)
            elif (
                p.name in STRAY_FILE_NAMES
                or p.name.endswith(STRAY_SUFFIXES)
                or "scratch" in p.name.lower()
            ):
                warnings.append(f"stray candidate (temp/generated): {rel(p)}")

    walk(REPO)


def set_root(root: Path) -> None:
    """Point the linter at a different repo root (the test seam)."""
    global REPO, WIKI, RAW, CANONICAL_SKILLS, CLAUDE_SKILLS, CODEX_SKILLS
    REPO = root.resolve()
    WIKI = REPO / "wiki"
    RAW = REPO / "raw"
    CANONICAL_SKILLS = REPO / "skills"
    CLAUDE_SKILLS = REPO / ".claude" / "skills"
    CODEX_SKILLS = REPO / "plugins" / "agentic-os" / "skills"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic wiki lint for the Agentic OS memory repo."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repo root to lint (default: the repo containing this script)",
    )
    args = parser.parse_args(argv)
    if args.root is not None:
        set_root(args.root)
    errors.clear()
    warnings.clear()
    missing = [
        p
        for p in (WIKI / "index.md", WIKI / "log.md", REPO / "AGENTS.md")
        if not p.is_file()
    ]
    if missing:
        for p in missing:
            print(f"ERROR   not a lintable repo root: {p} missing", file=sys.stderr)
        return 2
    check_links()
    check_frontmatter()
    check_index()
    check_log()
    check_captures()
    check_leaks()
    check_eval_results()
    check_skills()
    check_harness_drift()
    check_strays()
    print("## Deterministic wiki lint")
    print(f"- errors: {len(errors)}")
    print(f"- warnings: {len(warnings)}")
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    if not errors and not warnings:
        print("Clean pass — no mechanical issues found.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
