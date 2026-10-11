"""CODEOWNERS parsing, GitHub-style pattern matching and checks. Offline and read-only."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path

OWNER_RE = re.compile(r"^(@[A-Za-z0-9][A-Za-z0-9-]*(/[A-Za-z0-9._-]+)?|[^@\s]+@[^@\s]+\.[^@\s]+)$")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
CODEOWNERS_LOCATIONS = ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS")


@dataclass(frozen=True)
class Rule:
    line: int
    pattern: str
    owners: tuple[str, ...]


@dataclass
class Finding:
    level: str  # error | warning | info
    code: str
    message: str
    line: int | None = None


@dataclass
class Report:
    path: str | None
    rules: list[Rule] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(f.level == "error" for f in self.findings)


def parse(text: str) -> tuple[list[Rule], list[Finding]]:
    rules: list[Rule] = []
    findings: list[Finding] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip() if not raw.lstrip().startswith("#") else ""
        if not line:
            continue
        parts = line.split()
        pattern, owners = parts[0], tuple(parts[1:])
        if not owners:
            findings.append(Finding("error", "NO_OWNERS", f"pattern {pattern} has no owners", number))
            continue
        bad = [o for o in owners if not OWNER_RE.match(o)]
        for owner in bad:
            findings.append(Finding("error", "INVALID_OWNER", f"{owner!r} is not @user, @org/team or an email", number))
        rules.append(Rule(number, pattern, owners))
    seen: dict[str, int] = {}
    for rule in rules:
        if rule.pattern in seen:
            findings.append(Finding("warning", "DUPLICATE_PATTERN", f"{rule.pattern} repeats line {seen[rule.pattern]}", rule.line))
        else:
            seen[rule.pattern] = rule.line
    return rules, findings


def pattern_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a CODEOWNERS pattern (gitignore-like) into a regex over POSIX relative paths."""
    anchored = "/" in pattern.rstrip("/") and not pattern.startswith("**/")
    body = pattern.lstrip("/")
    body = body.rstrip("/")
    out = []
    i = 0
    while i < len(body):
        if body.startswith("**", i):
            if i + 2 < len(body) and body[i + 2] == "/":
                out.append("(?:.*/)?")
                i += 3
                continue
            out.append(".*")
            i += 2
            continue
        ch = body[i]
        if ch == "*":
            out.append("[^/]*")
        elif ch == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(ch))
        i += 1
    core = "".join(out)
    prefix = "^" if anchored else "^(?:.*/)?"
    # A pattern matches the path itself or anything beneath a matched directory.
    return re.compile(prefix + core + "(?:$|/.*$)")


def owners_for(rules: list[Rule], rel_path: str) -> tuple[str, ...] | None:
    """GitHub semantics: the last matching rule wins."""
    match: tuple[str, ...] | None = None
    for rule in rules:
        if pattern_to_regex(rule.pattern).search(rel_path):
            match = rule.owners
    return match


def repo_files(root: Path):
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.is_file():
            yield rel.as_posix()


def find_codeowners(root: Path) -> Path | None:
    for loc in CODEOWNERS_LOCATIONS:
        candidate = root / loc
        if candidate.is_file():
            return candidate
    return None


def check(root: str | Path, require_file: bool = False, require_full: bool = False, exclude: tuple[str, ...] = ()) -> Report:
    base = Path(root).resolve()
    co = find_codeowners(base)
    if co is None:
        report = Report(path=None)
        level = "error" if require_file else "info"
        report.findings.append(Finding(level, "NO_CODEOWNERS", "no CODEOWNERS file in CODEOWNERS, .github/ or docs/"))
        return report
    report = Report(path=co.relative_to(base).as_posix())
    report.rules, report.findings = parse(co.read_text(encoding="utf-8", errors="replace"))
    if not report.rules:
        return report

    files = list(repo_files(base))
    file_set = [f for f in files if not f.startswith(report.path or "")]
    for rule in report.rules:
        rx = pattern_to_regex(rule.pattern)
        if not any(rx.search(f) for f in file_set):
            report.findings.append(Finding("warning", "UNMATCHED_PATTERN", f"{rule.pattern} matches no files", rule.line))
    if require_full:
        unowned = [
            f
            for f in file_set
            if owners_for(report.rules, f) is None and not any(fnmatch.fnmatch(f, pat) for pat in exclude)
        ]
        if unowned:
            report.findings.append(Finding("error", "UNOWNED_FILES", f"{len(unowned)} file(s) have no owner, e.g. {unowned[0]}"))
    return report
