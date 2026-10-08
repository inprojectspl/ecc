"""Execute examples in a disposable, socket-only PostgreSQL cluster."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    for executable in ("initdb", "pg_ctl", "createdb"):
        if not shutil.which(executable):
            raise SystemExit(f"Missing {executable}; install PostgreSQL first")
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith("PG") and key not in ("DATABASE_URL", "DJANGO_SETTINGS_MODULE", "PYTEST_ADDOPTS")}
    with tempfile.TemporaryDirectory(prefix="django-skill-", dir="/tmp") as temporary:
        root = Path(temporary)
        data = root / "data"
        socket = root / "socket"
        socket.mkdir(mode=0o700)
        (root / "owned-eval-cluster").touch(mode=0o600)
        subprocess.run(["initdb", "-D", str(data), "-A", "trust", "-U", "skill_eval"],
                       check=True, stdout=subprocess.DEVNULL, env=environment)
        try:
            subprocess.run(["pg_ctl", "-D", str(data), "-l", str(root / "server.log"),
                            "-o", f"-F -k {socket} -p 55438 -c listen_addresses=''", "-w", "start"],
                           check=True, env=environment)
            subprocess.run(["createdb", "-h", str(socket), "-p", "55438", "-U", "skill_eval", "skill_eval"],
                           check=True, env=environment)
            environment["DJANGO_EVAL_OWNED_DIR"] = str(root)
            environment["DJANGO_SETTINGS_MODULE"] = "example.settings"
            cwd = Path(__file__).parent
            subprocess.run([sys.executable, "-m", "django", "makemigrations", "--check", "--dry-run"],
                           cwd=cwd, env=environment, check=True)
            result = subprocess.run([sys.executable, "-m", "coverage", "run", "--source=example", "-m", "pytest", "-q"],
                                    cwd=cwd, env=environment)
            subprocess.run([sys.executable, "-m", "coverage", "report", "--fail-under=80"], cwd=cwd, check=True)
        finally:
            if (data / "postmaster.pid").exists():
                subprocess.run(["pg_ctl", "-D", str(data), "-m", "fast", "-w", "stop"], check=True, env=environment)
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
