# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `--exclude GLOB` (repeatable) to exempt generated files from `--require-full`.

## [0.1.0] - 2026-10-11

### Added

- Validate CODEOWNERS: invalid owners, rules without owners, unmatched and duplicate patterns.
- `--require-full` reports files without an owner; `--require-file` and `--strict` modes.
- Bundled demo in `examples/demo`.

[Unreleased]: https://github.com/GhosTnever-lkm/codeowners-lint/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/GhosTnever-lkm/codeowners-lint/releases/tag/v0.1.0
