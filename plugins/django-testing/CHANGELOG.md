# Changelog

All notable changes to the inprojects Django testing plugin are documented here.
This plugin follows Semantic Versioning independently of the upstream ECC suite.

## [Unreleased]

## [1.0.0] - 2026-10-08

### Added

- Isolated Claude Code, Codex, and portable plugin packaging for `django-tdd`.
- PostgreSQL examples covering applied migrations, constraints, real authentication, ownership, commit callbacks, row locks, settings restoration, and fail-closed configuration.
- Upstream provenance and a maintained patch ledger.

### Changed

- Match the project's versions, runner, database, and authentication instead of imposing SQLite, disabled migrations, or coverage targets.
- Distinguish real authentication from bypass helpers and real commits from callback capture.
- Move detailed recipes into three focused references and keep the entrypoint concise.

[Unreleased]: https://github.com/inprojectspl/ecc/compare/inprojects-v1.0.0...main
[1.0.0]: https://github.com/inprojectspl/ecc/releases/tag/inprojects-v1.0.0
