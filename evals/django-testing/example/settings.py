"""Settings accept only the private cluster created by run_postgres.py."""
import os
from pathlib import Path
import secrets
import stat


def owned_database():
    raw = os.environ.get("DJANGO_EVAL_OWNED_DIR")
    if not raw:
        raise RuntimeError("Run run_postgres.py; an owned private cluster is required")
    root = Path(raw).resolve()
    if (root.parent != Path("/tmp").resolve()
            or not root.name.startswith("django-skill-")
            or not root.is_dir()
            or root.stat().st_uid != os.getuid()
            or stat.S_IMODE(root.stat().st_mode) != 0o700
            or not (root / "owned-eval-cluster").is_file()
            or not (root / "socket/.s.PGSQL.55438").is_socket()):
        raise RuntimeError("Refusing an unverified PostgreSQL test cluster")
    return {"ENGINE": "django.db.backends.postgresql", "NAME": "skill_eval",
            "TEST": {"NAME": "test_skill_eval"}, "HOST": str(root / "socket"),
            "PORT": "55438", "USER": "skill_eval", "PASSWORD": ""}


SECRET_KEY = secrets.token_urlsafe(48)
DEBUG = False
ALLOWED_HOSTS = ["testserver"]
INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "rest_framework", "example"]
DATABASES = {"default": owned_database()}
ROOT_URLCONF = "example.urls"
MIDDLEWARE = []
TIME_ZONE = "UTC"
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.BasicAuthentication"]}
