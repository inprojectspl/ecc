# Database and transaction tests

## Safe setup

Use the project's supported database engine for database-dependent behavior. PostgreSQL constraints, JSON, collation, transactions, and locks are not validated by an SQLite substitute. SQLite remains appropriate when it is an actual supported target or for clearly bounded portable behavior.

Before any command that creates, drops, flushes, or migrates a database, identify the resolved host/socket, role, database, and every Django alias. Use an isolated disposable server/container or a specifically provisioned test role with no production access. A name starting with `test_` alone is not proof of ownership. Refuse missing or ambiguous configuration; never fall back to a developer or production DSN. Avoid displaying passwords in logs.

Django's runner can connect to the configured base database or maintenance database while creating the test database. Protect those connections too. Custom fixtures, `--reuse-db`, routers, mirrors, and worker suffixes can change the target. Django test database creation is not a substitute for verifying settings before running tests.

The fork's `evals/django-testing/run_postgres.py` creates its own mode-0700 temporary directory, initializes a private PostgreSQL server, disables TCP, and passes an explicit Unix socket to dedicated test settings. It accepts no external DSN and shuts down only that cluster in `finally`. Copying this harness is optional; an existing verified CI container works too.

## Migrations and constraints

Keep migrations enabled for migration/schema integration checks. `--no-migrations`, `--nomigrations`, or `MIGRATION_MODULES` overrides remove evidence about the deployment path. If the project has a separate fast lane, label its limitations and retain a migrations-enabled lane on the real engine. With `--reuse-db`, use `--create-db` after schema changes when needed; do not assume a reused database is current.

`makemigrations --check --dry-run` detects model/migration drift, but does not prove data migrations work. For a data migration, construct the previous state using historical models from `MigrationExecutor`, apply the target migration, and assert independently expected transformed data and constraints. Restore the migration graph to its leaf state even on failure in a dedicated migration test database.

To test a database constraint, execute a write through the actual database. `full_clean()` and serializer validation exercise different layers. Catch an expected `IntegrityError` outside an inner atomic block so subsequent assertions run after its savepoint has rolled back:

```python
import pytest
from django.db import IntegrityError, transaction

@pytest.mark.django_db
def test_empty_title_is_rejected(owner):
    # Note and owner are domain-specific fixtures/models, not Django APIs.
    with pytest.raises(IntegrityError), transaction.atomic():
        Note.objects.create(owner=owner, title="")
    assert not Note.objects.exists()
```

## Pick the transaction model deliberately

`db`, ordinary `django_db`, and Django `TestCase` wrap work for rollback isolation. They do not represent real outer commits. Calling `commit()` inside their atomic block is an error; disabling Django's wrappers or mocking commit hides the problem. Use `transaction=True` or `TransactionTestCase` when the behavior depends on transaction boundaries. These tests use cleanup rather than one rollback and can be slower.

For callback registration and its side effect, `django_capture_on_commit_callbacks(execute=True)` can exercise callbacks inside an ordinary database test. This deliberately executes captured callbacks, not a real commit. For commit timing or rollback suppression, use a transactional test:

```python
@pytest.mark.django_db(transaction=True)
def test_callback_waits_for_commit():
    delivered = []
    with transaction.atomic():
        transaction.on_commit(lambda: delivered.append("receipt"))
        assert delivered == []
    assert delivered == ["receipt"]
```

Registering a callback outside an atomic block executes it immediately. A rolled-back savepoint discards callbacks registered within it. Test these cases when the feature depends on them.

`select_for_update()` must run within a real transaction on PostgreSQL. Ordinary `TestCase` can mask a missing application transaction because the test itself is already atomic. Test this with `transaction=True`; use separate physical connections plus bounded waits (`NOWAIT`, a timeout, or explicit synchronization) to prove contention. Avoid sleep-based timing assertions.

A transaction on the test connection cannot roll back commits made by a live server, worker, or other connection. Provision cleanup for all participating connections and use separate databases/schemas per worker as required. Retain pytest-django's worker suffix logic when overriding database settings.

## Sources

Read the version matching the project:

- [pytest-django database access](https://pytest-django.readthedocs.io/en/latest/database.html)
- [Django 5.2 transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/)
- [Django 5.2 testing tools](https://docs.djangoproject.com/en/5.2/topics/testing/tools/)
- [Django 5.2 migrations and historical models](https://docs.djangoproject.com/en/5.2/topics/migrations/#historical-models)
