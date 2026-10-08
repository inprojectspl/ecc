import base64

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.db.migrations.recorder import MigrationRecorder
from django.test import override_settings
from rest_framework.test import APIClient

from example.models import Note


@pytest.fixture
def owner(db):
    return get_user_model().objects.create_user(username="owner", password="eval-password")


@pytest.fixture
def note(owner):
    return Note.objects.create(owner=owner, title="Private contract")


@pytest.mark.django_db
def test_migrations_created_real_postgres_constraint(owner):
    assert connection.vendor == "postgresql"
    assert MigrationRecorder(connection).migration_qs.filter(
        app="example", name="0001_initial"
    ).exists()
    with pytest.raises(IntegrityError), transaction.atomic():
        Note.objects.create(owner=owner, title="")
    assert not Note.objects.exists()


def credentials(username, password):
    value = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"HTTP_AUTHORIZATION": f"Basic {value}"}


@pytest.mark.django_db
def test_real_authentication_and_ownership(note):
    other = get_user_model().objects.create_user(username="other", password="eval-password")
    client = APIClient()
    url = f"/notes/{note.pk}/"
    assert client.get(url).status_code == 401
    assert client.get(url, **credentials("owner", "wrong")).status_code == 401
    assert client.get(url, **credentials(other.username, "eval-password")).status_code == 404
    response = client.get(url, **credentials("owner", "eval-password"))
    assert response.status_code == 200
    assert response.json() == {"id": note.pk, "title": "Private contract"}
    note.refresh_from_db()
    assert note.title == "Private contract"


@pytest.mark.django_db
def test_forced_auth_checks_permissions_only(note):
    client = APIClient()
    client.force_authenticate(user=note.owner)
    assert client.get(f"/notes/{note.pk}/").status_code == 200
    client.force_authenticate(user=None)
    assert client.get(f"/notes/{note.pk}/").status_code == 401


@pytest.mark.django_db
def test_capture_callback_is_not_a_real_commit(django_capture_on_commit_callbacks):
    delivered = []
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        transaction.on_commit(lambda: delivered.append("receipt"))
        assert delivered == []
    assert len(callbacks) == 1
    assert delivered == ["receipt"]


@pytest.mark.django_db(transaction=True)
def test_real_commit_fires_callback_and_rollback_discards_it():
    delivered = []
    with transaction.atomic():
        transaction.on_commit(lambda: delivered.append("committed"))
        assert delivered == []
    assert delivered == ["committed"]
    with pytest.raises(ValueError), transaction.atomic():
        transaction.on_commit(lambda: delivered.append("rolled back"))
        raise ValueError("cancelled")
    assert delivered == ["committed"]


@pytest.mark.django_db(transaction=True)
def test_lock_requires_transaction_and_blocks_second_connection():
    import psycopg
    from django.db.transaction import TransactionManagementError

    owner = get_user_model().objects.create_user(username="locker")
    note = Note.objects.create(owner=owner, title="Locked")
    with pytest.raises(TransactionManagementError):
        Note.objects.select_for_update().get(pk=note.pk)
    params = connection.get_connection_params()
    # Use a separate physical connection to observe database locking.
    with psycopg.connect(**params) as competing:
        with transaction.atomic():
            Note.objects.select_for_update().get(pk=note.pk)
            with pytest.raises(psycopg.errors.LockNotAvailable):
                with competing.cursor() as cursor:
                    cursor.execute("SELECT id FROM example_note WHERE id = %s FOR UPDATE NOWAIT", [note.pk])
            competing.rollback()
        with competing.cursor() as cursor:
            cursor.execute("SELECT id FROM example_note WHERE id = %s FOR UPDATE NOWAIT", [note.pk])
            assert cursor.fetchone() == (note.pk,)


def test_settings_override_restores_after_error(settings):
    original = settings.TIME_ZONE
    with pytest.raises(ValueError):
        with override_settings(TIME_ZONE="Europe/Warsaw"):
            assert settings.TIME_ZONE == "Europe/Warsaw"
            raise ValueError("failed assertion path")
    assert settings.TIME_ZONE == original


@pytest.mark.django_db
def test_non_owner_cannot_write_and_owner_write_persists(note):
    get_user_model().objects.create_user(username="other", password="eval-password")
    client = APIClient()
    url = f"/notes/{note.pk}/"
    denied = client.patch(url, {"title": "Hijacked"}, format="json",
                          **credentials("other", "eval-password"))
    assert denied.status_code == 404
    note.refresh_from_db()
    assert note.title == "Private contract"
    accepted = client.patch(url, {"title": "Updated contract"}, format="json",
                            **credentials("owner", "eval-password"))
    assert accepted.status_code == 200
    note.refresh_from_db()
    assert note.title == "Updated contract"


def test_database_settings_fail_closed(monkeypatch):
    from example.settings import owned_database

    monkeypatch.delenv("DJANGO_EVAL_OWNED_DIR")
    with pytest.raises(RuntimeError, match="owned private cluster"):
        owned_database()
    monkeypatch.setenv("DJANGO_EVAL_OWNED_DIR", "/tmp")
    with pytest.raises(RuntimeError, match="unverified"):
        owned_database()
