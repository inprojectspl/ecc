# Fixtures and independent expectations

## Data setup

Use factories when they clarify required relationships and reduce distracting setup. Small direct ORM setup is equally valid. Choose deterministic contract values for fields used in assertions; use `Decimal("19.99")` for money rather than binary floats. Factories should construct preconditions, not precompute the behavior being tested. A slug assigned by the factory cannot prove the application's slug generation works.

Declare database access explicitly through `db`, `django_db`, or a fixture that requests it. Keep fixtures scoped narrowly enough to prevent mutable ORM objects, client sessions, or factory state leaking between tests. Use `get_user_model()` and inspect `USERNAME_FIELD` and custom manager requirements rather than assuming every project accepts `username` and `email` identically.

A factory calling `set_password()` must persist the hash when creating a database user; check the installed factory_boy version's post-generation save semantics. A call-only mock of `set_password` does not verify that real login works.

## Restoration and external effects

Use pytest-django's `settings` fixture or Django's `override_settings` context/decorator for settings overrides. Use `monkeypatch` for environment variables and scoped mocks for external boundaries; restore them even when an assertion raises. Do not patch `DATABASES` after connections have initialized and assume Django will reconnect safely.

Use Django's locmem email backend or pytest-django's `mailoutbox` to inspect recipients and content. Eager Celery execution exercises task bodies differently from a broker/worker deployment. Retain a worker-backed check when delivery, retry, serialization, or acknowledgement behavior is part of the requirement.

Patch where the dependency is looked up. Assert meaningful arguments, returned behavior, and relevant state, not merely that a mock was called once. Do not replace the ORM for tests claiming PostgreSQL behavior.

## Strong expectations and properties

Choose expected values from a written rule or independent examples. For property-based tests, encode a domain invariant plus boundary examples. Reimplementing the same algorithm in the test can reproduce its bug; a round-trip property alone may miss matching defects in encoder and decoder. Database-backed property tests need isolation per generated example; ordinary function-scoped fixtures may persist state across examples. Use the framework-compatible integration or explicit per-example cleanup and validate the resulting isolation.

Test one behavior coherently, with enough assertions to reject plausible broken implementations. Avoid blanket bans on multiple assertions, arbitrary coverage targets, or requiring a fixture/factory for every object.

## Report scope honestly

Record commands actually run and distinguish pass, fail, skipped, expected failure, and not run. State whether authentication was forced, migrations were enabled, the engine was PostgreSQL, and a real commit or worker was exercised. Passing example tests demonstrates those recipes on pinned versions; it does not prove all application requirements, all database engines, or skill selection quality.

## Sources

- [pytest-django helpers](https://pytest-django.readthedocs.io/en/latest/helpers.html)
- [Django 5.2 overriding settings](https://docs.djangoproject.com/en/5.2/topics/testing/tools/#overriding-settings)
- [factory_boy Django integration](https://factoryboy.readthedocs.io/en/stable/orms.html#the-djangomodelfactory-subclass)
- [Hypothesis Django integration](https://hypothesis.readthedocs.io/en/latest/reference/integrations.html#django)
