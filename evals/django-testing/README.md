# Django recipe evaluations

These tests execute selected recipes behind the adapted skill. They are not an end-to-end evaluation of agent behavior or the entire upstream ECC project.

## Reproduce

Install `uv` and PostgreSQL client/server binaries (`initdb`, `pg_ctl`, `createdb`) on PATH, then from the repository root:

```sh
uv venv evals/django-testing/.venv --python 3.13
uv pip sync evals/django-testing/requirements.txt --python evals/django-testing/.venv/bin/python
evals/django-testing/.venv/bin/python evals/django-testing/run_postgres.py
```

The runner creates a private temporary PostgreSQL cluster with a unique Unix socket and TCP disabled. It ignores inherited PostgreSQL connection variables, `DATABASE_URL`, and pytest command overrides. It does not accept or modify an existing database. The settings require the owned temporary directory and live socket; direct pytest execution without the runner fails closed. Django creates and destroys `test_skill_eval` inside that cluster, then the runner stops and removes the cluster even when tests fail.

## Observed result

On 2026-10-08: **9 passed**, migration drift check passed, 100% statement coverage of the tiny `example` application. PostgreSQL 18.6; Python 3.13.13; Django 5.2.18 LTS; DRF 3.18.3; pytest 9.1.1; pytest-django 4.14.0; psycopg 3.3.6. Dependencies are pinned in `requirements.txt`.

| Test | Evidence |
| --- | --- |
| migrations_created_real_postgres_constraint | Applied migration exists; PostgreSQL constraint rejects empty title and savepoint recovery permits subsequent queries. |
| real_authentication_and_ownership | Missing/wrong credentials denied, other owner concealed, valid password returns literal expected payload. |
| forced_auth_checks_permissions_only | Forced identity is deliberately a separate boundary; clearing it removes access. |
| capture_callback_is_not_a_real_commit | Registration and explicit captured execution, without claiming a database commit. |
| real_commit_fires_callback_and_rollback_discards_it | Real commit timing and rollback suppression. |
| lock_requires_transaction_and_blocks_second_connection | Autocommit misuse fails; a separate physical connection cannot obtain NOWAIT lock until transaction ends. |
| settings_override_restores_after_error | Context restoration after a raised error. |
| non_owner_cannot_write_and_owner_write_persists | Denied write leaves persisted state unchanged; owner's write persists. |
| database_settings_fail_closed | Missing and unverified ownership settings are rejected. |

## Limitations

The example uses BasicAuthentication to test a real authentication boundary, not JWT or session CSRF. It does not exercise data migration upgrades, full browser flows, worker delivery, parallel pytest workers, multi-database routing, factory_boy, Hypothesis, or other framework versions. Initial schema migration checks do not prove all future data migrations. Coverage applies only to this tiny fixture app and does not measure skill effectiveness.
