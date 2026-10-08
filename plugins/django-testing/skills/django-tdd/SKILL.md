---
name: django-tdd
description: Plan, write, and review Django and Django REST Framework tests using pytest-django or Django test classes. Use for Django models, migrations, transactions, authentication, and API permissions; inspect the project's Django stack before applying these patterns.
metadata:
  origin: ECC
  adapted-by: inprojects
---

# Django testing with TDD

## When to activate

Use for Django or DRF testing tasks. Confirm Django in the relevant project or workspace package before applying framework advice. Preserve the existing runner, database engine, authentication scheme, and project conventions.

## Establish the contract

- Read dependency locks, settings, pytest configuration, fixtures, and a representative test. Match documentation to installed Django, DRF, pytest-django, factory_boy, and database versions.
- Separate planning, review, and implementation. A review produces findings with concrete failure cases; a plan does not silently modify code. For implementation, choose the smallest useful test boundary and follow the project's test-first workflow.
- Derive expected results from requirements, public contracts, or independently computed examples. Do not change assertions to match current implementation unless evidence establishes that the requirement was wrong.
- Cover the relevant success, boundary, failure, and authorization behavior. A coherent test may use several assertions, especially to verify denied requests leave state unchanged. Coverage identifies gaps; respect existing thresholds without inventing new universal percentages.

## Choose the boundary

| Behavior under test | Starting point |
| --- | --- |
| Pure domain calculation | Plain pytest, no database fixture |
| Model/query/serializer persistence | `db` or `django_db`, actual supported engine |
| Middleware, session, URL, or API contract | Django client or DRF `APIClient` |
| Commit, rollback, locking, cross-connection visibility | `transactional_db`, `django_db(transaction=True)`, or `TransactionTestCase` |
| Browser behavior, worker delivery, deployed networking | Existing browser, worker, or system test harness |

The Django client is in-process and does not prove browser behavior. Mock external services at a deliberate boundary; retain database integrations where constraints or query behavior form part of the contract.

## Read only the relevant reference

- [Database and transactions](references/database-and-transactions.md): safe PostgreSQL setup, migrations, savepoints, callbacks, row locks, and parallel workers.
- [DRF and authentication](references/drf-and-authentication.md): real credentials versus bypass helpers, object ownership, CSRF, and response contracts.
- [Fixtures and independent expectations](references/fixtures-and-expectations.md): factories, restoration, external effects, and reporting.

## Execution and reporting

Run the focused tests, then the related checks justified by changed behavior. Record the command, versions, database backend, pass/fail counts, and anything not executed. If a prerequisite is missing, report that boundary rather than substituting SQLite, bypassing authentication, disabling migrations, or claiming success from inspection.

This fork's executable examples live in the repository's `evals/django-testing`; they validate selected recipes, not the effectiveness of every agent invocation or an application's complete security.
