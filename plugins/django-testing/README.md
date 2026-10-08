# Django testing plugin

This inprojects distribution contains only the adapted `django-tdd` skill and its references, plus required manifests, provenance, and the upstream MIT license. It does not include ECC hooks, MCP configuration, agents, or other skills.

Plugin identifier: `django-testing`. Skill identifier: `django-tdd`. Version: `1.0.1`. Fork tag: `inprojects-v1.0.1`. Marketplace integrations must use the `plugins/django-testing` subdirectory of the pinned fork, not the ECC repository root.

Canonical instructions live at `skills/django-tdd` in the fork. Run `python3 scripts/package_django_plugin.py` after changes and `python3 scripts/package_django_plugin.py --check` before release. Generated files under this plugin are committed so clients do not execute packaging code during installation.

For project use, install this package in a Django project and preserve the project's runner and settings. The skill verifies that Django applies to the relevant workspace package before using framework advice.

See [PROVENANCE.md](PROVENANCE.md) for upstream identity, [CHANGELOG.md](CHANGELOG.md) for this distribution's changes, and `docs/inprojects/django-testing.md` in the fork for validation evidence and update procedure. This is a scoped fork package, not an audit or endorsement of the full upstream ECC catalogue.
