# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.4] - 2026-10-25

### Added

- `--exclude GLOB` (repeatable) to exempt generated files from `--require-full`.

### Fixed

- `--require-full` now reports unowned files when `CODEOWNERS` contains only comments or no valid rules.

## [0.1.3] - 2026-10-25

### Fixed

- Exclude only the selected CODEOWNERS file from `--require-full`; similarly prefixed files are now checked.

## [0.1.2] - 2026-10-13

### Fixed

- Match GitHub's CODEOWNERS file precedence: `.github/`, repository root, then `docs/`.
- Ignore invalid-owner rules after reporting them, matching GitHub's behavior for invalid lines.
- Keep package and CLI versions synchronized and publish installable release artifacts.

## [0.1.1] - 2026-10-11

### Added

- CI now also runs the test suite on Windows (windows-latest), not only Ubuntu.


## [0.1.0] - 2026-10-11

### Added

- Validate CODEOWNERS: invalid owners, rules without owners, unmatched and duplicate patterns.
- `--require-full` reports files without an owner; `--require-file` and `--strict` modes.
- Bundled demo in `examples/demo`.

[Unreleased]: https://github.com/GhosTnever-lkm/codeowners-lint/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/GhosTnever-lkm/codeowners-lint/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/GhosTnever-lkm/codeowners-lint/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/GhosTnever-lkm/codeowners-lint/releases/tag/v0.1.2
[0.1.1]: https://github.com/GhosTnever-lkm/codeowners-lint/releases/tag/v0.1.1
[0.1.0]: https://github.com/GhosTnever-lkm/codeowners-lint/releases/tag/v0.1.0
