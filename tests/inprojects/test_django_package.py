"""Distribution checks use a temporary minimal repository, never the live plugin."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("package_django", ROOT / "scripts/package_django_plugin.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for relative in ("skills/django-tdd", "plugins/django-testing"):
            shutil.copytree(ROOT / relative, self.root / relative)
        shutil.copyfile(ROOT / "LICENSE", self.root / "LICENSE")
        self.plugin = self.root / "plugins/django-testing"

    def test_generation_is_deterministic_and_detects_content_drift(self):
        self.assertEqual(module.package(self.root, check=True), 0)
        source = self.root / "skills/django-tdd/SKILL.md"
        source.write_text(source.read_text() + "\nAn isolated test mutation.\n")
        self.assertEqual(module.package(self.root, check=True), 1)
        self.assertEqual(module.package(self.root), 0)
        first = {str(p.relative_to(self.plugin)): p.read_bytes() for p in self.plugin.rglob("*") if p.is_file()}
        self.assertEqual(module.package(self.root), 0)
        second = {str(p.relative_to(self.plugin)): p.read_bytes() for p in self.plugin.rglob("*") if p.is_file()}
        self.assertEqual(first, second)
        self.assertEqual(module.package(self.root, check=True), 0)

    def test_rejects_unreviewed_hook_surface(self):
        hooks = self.plugin / "hooks/hooks.json"
        hooks.parent.mkdir()
        hooks.write_text("{}")
        with self.assertRaisesRegex(ValueError, "Unexpected distribution files"):
            module.package(self.root, check=True)

    def test_rejects_manifest_hook_extension(self):
        path = self.plugin / ".claude-plugin/plugin.json"
        manifest = json.loads(path.read_text())
        path.write_text(json.dumps({**manifest, "hooks": "./hooks.json"}))
        with self.assertRaisesRegex(ValueError, "skill-only"):
            module.package(self.root)

    def test_rejects_output_symlink(self):
        target = self.plugin / "skills/django-tdd/SKILL.md"
        target.unlink()
        target.symlink_to(self.root / "skills/django-tdd/SKILL.md")
        with self.assertRaisesRegex(ValueError, "symlink output"):
            module.package(self.root)

    def test_rejects_symlinked_package_root_without_writing_external_files(self):
        external = self.root / "external-package"
        self.plugin.rename(external)
        self.plugin.symlink_to(external, target_is_directory=True)
        target = external / "skills/django-tdd/SKILL.md"
        original = target.read_bytes()
        source = self.root / "skills/django-tdd/SKILL.md"
        source.write_text("Changed source that must not escape")
        for check in (True, False):
            with self.assertRaisesRegex(ValueError, "symlink boundary"):
                module.package(self.root, check=check)
        self.assertEqual(target.read_bytes(), original)

    def test_rejects_symlinked_source_directory(self):
        source = self.root / "skills/django-tdd"
        external = self.root / "external-source"
        source.rename(external)
        source.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink boundary"):
            module.package(self.root)

    def test_rejects_symlinked_license(self):
        license_path = self.root / "LICENSE"
        external = self.root / "external-license"
        license_path.rename(external)
        license_path.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "symlink boundary"):
            module.package(self.root)


if __name__ == "__main__":
    unittest.main()
