"""codeowners-lint [PATH] [--require-file] [--require-full] [--exclude GLOB] [--strict] [--json]"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .core import check


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="codeowners-lint", description="Validate CODEOWNERS against the repository tree (offline).")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--require-file", action="store_true", help="missing CODEOWNERS is an error")
    p.add_argument("--require-full", action="store_true", help="every file must have an owner")
    p.add_argument("--strict", action="store_true", help="warnings fail the run")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="ignore files matching this glob for --require-full (repeatable)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--version", action="version", version=__version__)
    args = p.parse_args(argv)
    if not Path(args.path).is_dir():
        print(f"codeowners-lint: not a directory: {args.path}", file=sys.stderr)
        return 2
    report = check(args.path, require_file=args.require_file, require_full=args.require_full, exclude=tuple(args.exclude))
    if args.json:
        print(json.dumps({"path": report.path, "rules": [asdict(r) | {"owners": list(r.owners)} for r in report.rules],
                          "findings": [asdict(f) for f in report.findings]}, indent=2, ensure_ascii=False))
    else:
        print(f"CODEOWNERS: {report.path or 'not found'} ({len(report.rules)} rules)")
        if not report.findings:
            print("OK: no findings")
        for f in report.findings:
            loc = f" (line {f.line})" if f.line else ""
            print(f"[{f.level.upper()}] {f.code}{loc}: {f.message}")
    failed = report.has_errors or (args.strict and any(f.level == "warning" for f in report.findings))
    return 1 if failed else 0
