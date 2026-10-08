# DRF and authentication tests

## Keep authentication and permission evidence distinct

`APIClient.force_authenticate(user=...)` bypasses authentication. Use it when isolating permission or application behavior, and label that boundary. It does not verify passwords, token parsing, expiry, signatures, authentication backends, or session login. `client.force_login()` similarly bypasses credential verification.

Use actual configured credentials through `APIClient.credentials()`, request headers, or `client.login()` for authentication tests. A fresh client per actor/test avoids cookie or header leakage. If reusing a forced client, clear forced authentication and credentials; DRF's logout path may require the configured session backend.

For JWT applications, obtain a valid token through the project's supported issuer/helper and test applicable invalid signature, expiration, issuer/audience, or revocation behavior. Do not introduce JWT into a session or BasicAuthentication project just to follow an example. Keep passwords and tokens created by tests local to disposable test identities.

The framework's response status depends on configured authentication classes and the endpoint contract. An unauthenticated denial can be 401 or 403; object concealment may deliberately be 404. Assert the exact agreed status and relevant error shape, without allowing a broad set of statuses to hide regressions.

## Authorization matrix

For protected operations, select the relevant combinations:

- No credentials and invalid credentials.
- Authorized owner or tenant member.
- Authenticated other user or tenant, including read, list, update, and delete as applicable.
- Privileged role and inactive or revoked actor when part of the contract.

Assert allowed response data and persisted effects. For a denied write, reload affected records and assert they stayed unchanged; verify no external effect when relevant. For list endpoints, assert the actual returned identifier set, not only its size. DRF object permissions are not automatically applied to every row of a list queryset or to creation; test queryset filtering and create-time enforcement separately.

```python
@pytest.mark.django_db
def test_other_user_cannot_edit(note, other_user):
    client = APIClient()
    client.force_authenticate(user=other_user)  # Permission boundary only.
    response = client.patch(f"/notes/{note.pk}/", {"title": "Hijacked"}, format="json")
    assert response.status_code == 404  # This API conceals other users' notes.
    note.refresh_from_db()
    assert note.title == "Private contract"
```

`note`, `other_user`, the path, and the concealment status above are application-specific. The runnable fork example tests BasicAuthentication separately with real password verification and asserts literal response fields and persisted titles.

## Middleware and CSRF

`APIRequestFactory` exercises a view boundary; it does not run the complete middleware stack. Use a client when middleware, sessions, routing, or renderer behavior matters. `APIClient(enforce_csrf_checks=True)` enables CSRF checks for a session-authenticated test. Prove both the missing-token denial and the valid-token path for the actual login/form flow. Forced authentication and the client's default disabled CSRF checks do not prove CSRF protection.

Use `format="json"` for JSON writes and assert stable public response fields. Do not compute expected data by calling the serializer under test. Distinguish serializer validation, model validation, and database constraints; they can legitimately enforce different boundaries.

## Sources

- [DRF testing](https://www.django-rest-framework.org/api-guide/testing/)
- [DRF authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [DRF object permissions and limitations](https://www.django-rest-framework.org/api-guide/permissions/#limitations-of-object-level-permissions)
