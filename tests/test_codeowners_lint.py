import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from codeowners_lint.cli import main
from codeowners_lint.core import check, owners_for, parse, pattern_to_regex


def repo(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp())
    for name, text in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


class MatchTests(unittest.TestCase):
    def test_bare_name_matches_anywhere(self):
        rx = pattern_to_regex("*.js")
        self.assertTrue(rx.search("src/app/index.js"))
        self.assertFalse(rx.search("src/app/index.ts"))

    def test_anchored_path(self):
        rx = pattern_to_regex("/docs/")
        self.assertTrue(rx.search("docs/guide.md"))
        self.assertFalse(rx.search("src/docs/guide.md"))

    def test_double_star(self):
        rx = pattern_to_regex("apps/**/config.yml")
        self.assertTrue(rx.search("apps/web/prod/config.yml"))
        self.assertTrue(rx.search("apps/config.yml"))

    def test_last_rule_wins(self):
        rules, _ = parse("* @a\n/src/ @b\n")
        self.assertEqual(owners_for(rules, "src/main.py"), ("@b",))
        self.assertEqual(owners_for(rules, "README.md"), ("@a",))


class ParseTests(unittest.TestCase):
    def test_invalid_owner_and_missing_owners(self):
        rules, findings = parse("*.py notanowner\n/docs/\n")
        codes = [f.code for f in findings]
        self.assertIn("INVALID_OWNER", codes)
        self.assertIn("NO_OWNERS", codes)
        self.assertEqual(len(rules), 1)

    def test_email_and_team_are_valid(self):
        _, findings = parse("* dev@example.com @org/core\n")
        self.assertEqual(findings, [])

    def test_comments_and_duplicates(self):
        _, findings = parse("# note\n* @a # trailing\n* @b\n")
        self.assertEqual([f.code for f in findings], ["DUPLICATE_PATTERN"])


class CheckTests(unittest.TestCase):
    def test_missing_file_is_info_unless_required(self):
        root = repo({"a.py": "x"})
        self.assertFalse(check(root).has_errors)
        self.assertTrue(check(root, require_file=True).has_errors)

    def test_unmatched_pattern_warns(self):
        root = repo({"CODEOWNERS": "*.rs @a\n", "a.py": "x"})
        codes = [f.code for f in check(root).findings]
        self.assertIn("UNMATCHED_PATTERN", codes)

    def test_require_full_reports_unowned(self):
        root = repo({".github/CODEOWNERS": "*.py @a\n", "a.py": "x", "b.md": "y"})
        report = check(root, require_full=True)
        self.assertTrue(any(f.code == "UNOWNED_FILES" for f in report.findings))

    def test_exclude_suppresses_unowned_for_generated_files(self):
        root = repo({".github/CODEOWNERS": "*.py @a\n", "a.py": "x", "gen/out.md": "y"})
        self.assertTrue(check(root, require_full=True).findings)
        report = check(root, require_full=True, exclude=("gen/*",))
        self.assertFalse(any(f.code == "UNOWNED_FILES" for f in report.findings))

    def test_codeowners_file_itself_not_counted(self):
        root = repo({"CODEOWNERS": "* @a\n"})
        report = check(root, require_full=True)
        self.assertFalse(any(f.code == "UNOWNED_FILES" for f in report.findings))


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(argv)
        return code, buf.getvalue()

    def test_ok(self):
        code, out = self.run_cli([str(repo({"CODEOWNERS": "* @a\n", "a.py": "x"}))])
        self.assertEqual(code, 0)
        self.assertIn("OK", out)

    def test_invalid_owner_exit_one_json(self):
        root = repo({"CODEOWNERS": "* bad\n", "a.py": "x"})
        code, out = self.run_cli(["--json", str(root)])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["findings"][0]["code"], "INVALID_OWNER")

    def test_bad_path(self):
        with contextlib.redirect_stderr(io.StringIO()):
            code, _ = self.run_cli(["/no/such"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
