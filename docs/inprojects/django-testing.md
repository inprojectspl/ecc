# inprojects Django testing adaptation

## Scope and provenance

This fork packages `plugins/django-testing` version 1.0.1 from canonical `skills/django-tdd`. Its release tag is `inprojects-v1.0.1`, independent of ECC releases. The base upstream commit is [`ef648e01899ba3e8dc6371642deaaf64b4477775`](https://github.com/affaan-m/ecc/commit/ef648e01899ba3e8dc6371642deaaf64b4477775).

The original MIT license remains intact. `django-tdd` is retained as the descriptive skill identifier so users can trace the adaptation. The upstream adaptation policy governs imports into ECC; this distribution is an explicitly requested fork adaptation, not a newly branded upstream ECC contribution.

The reviewed installable artifact includes only this skill, references, licenses, provenance, and plugin metadata. Do not point a marketplace at the repository root: that is the full upstream ECC distribution with unrelated hooks and integrations. No upstream npm package, hooks, MCP servers, or workflows are installed or enabled by this package.

## Patch ledger

| ID | Upstream concern | Adaptation and evidence |
| --- | --- | --- |
| DJ-01 | SQLite and migrations-disabled setup presented as default | Preserve supported engine; PostgreSQL schema and applied-migration checks execute with migrations enabled. |
| DJ-02 | Transaction behavior conflated with rollback fixtures | Separate ordinary DB, real commit, callback capture, and cross-connection locking boundaries; executed cases cover each. |
| DJ-03 | force_authenticate presented as authenticated coverage | Separate bypass tests from actual BasicAuthentication password verification; assert owner and non-owner reads/writes. |
| DJ-04 | Tests mostly assert setup data or broad success | Contract literals, DB constraint rejection, denied-write persistence, and independent expectation guidance. |
| DJ-05 | Mandatory factories, one assertion, fixed coverage targets | Select fixtures/factories and assertion count by behavior; honor project thresholds without inventing policy. |
| DJ-06 | Test DSN and cleanup not verified | Private mode-0700 cluster/socket, no TCP, explicit test settings, fail-closed negative checks, shutdown in finally. |
| DJ-07 | Large entrypoint with incomplete examples | Short entrypoint and three conditional references; self-contained plugin with no runtime dependency on other skills. |
| DJ-08 | Full ECC package exceeds selected scope | Skill-only package with manifest field allowlist, file allowlist, deterministic drift check, preserved license. |

## Validation on 2026-10-08

Executed Python 3.13.13, PostgreSQL 18.6, Django 5.2.18 (LTS), DRF 3.18.3, pytest 9.1.1, pytest-django 4.14.0, and psycopg 3.3.6. The eval lock records all versions. Django 5.2 LTS is an explicit eval target, not a claim that it is the newest Django series.

`evals/django-testing/.venv/bin/python evals/django-testing/run_postgres.py`: 9 tests passed; migration drift check passed; example application statement coverage was 100%. The 80% enforcement in this repository's eval runner follows ECC's contributor rule and is not propagated as a policy into the distributed skill. These small example metrics say nothing about an application's overall coverage.

See [the eval README](../../evals/django-testing/README.md) for reproduction, executed boundaries, and limitations. The initial harness run exposed a missing sessions app when clearing forced authentication; the fixture settings now include the real sessions app and migration.

Package validation: 7 regression tests passed for deterministic generation, drift detection, rejected hook files/manifest fields, and symlink confinement. Canonical skill validation, Claude plugin validation, generated package drift, and local reference links passed. Independent review reproduced a package-root symlink escape; the correction rejects directory boundaries before access and the reviewer verified all regressions pass.

The upstream context trigger manifest received only six Django testing phrases and refreshed derived digests/count to keep the changed canonical skill consistent. The upstream generator requires broad external model calls, so this small entry was curated manually, consistent with the manifest's existing hand-seeded status.

`npm test` passed after the narrow trigger consistency update: repository validators, catalogue and command-registry checks, and the upstream JavaScript suite (325 discovered test files). Dependencies were installed with `npm ci --ignore-scripts`; lifecycle scripts were not enabled. This does not certify all upstream instructions or integrations.

Full catalogue security review is outside this scoped package change. No claim is made about the unresolved third-party catalogue alert from the earlier audit; the published artifact is limited to reviewed text/manifests/license. Repeated live-agent outcome evaluations, JWT, session CSRF, data migration upgrades, browser E2E, workers, multiple database aliases, and other Django versions remain unmeasured.

## Updating upstream

1. Fetch upstream and inspect the diff from the recorded base SHA for `skills/django-tdd`, its referenced files, and LICENSE.
2. Reapply the patch ledger deliberately. Do not merge hook, MCP, publishing, or unrelated skill configuration into the isolated plugin.
3. Check primary documentation against target project versions, then rerun the private PostgreSQL examples, package drift checks, skill validation, and plugin validation.
4. Bump the plugin manifests through the canonical Claude manifest, regenerate, update provenance and changelog, and publish a new immutable `inprojects-vX.Y.Z` tag.
5. Point the marketplace at that tag and `plugins/django-testing`; never move a published tag.
