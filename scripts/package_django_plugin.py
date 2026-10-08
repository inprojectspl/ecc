"""Package only the adapted Django skill; never import the ECC plugin suite."""
import argparse
import json
from pathlib import Path
import re


def package(root, check=False):
    plugin = root / "plugins/django-testing"
    source = root / "skills/django-tdd"
    # Reject symlinked roots and directories before reading or writing artifacts.
    for path in (root / "plugins", plugin, root / "skills", source,
                 source / "references", root / "LICENSE"):
        if path.is_symlink():
            raise ValueError(f"Refusing symlink boundary: {path}")
    for base in (source, plugin):
        for path in base.rglob("*"):
            if path.is_symlink():
                raise ValueError(f"Refusing symlink output or source: {path}")
    manifest_path = plugin / ".claude-plugin/plugin.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest["name"] != "django-testing" or not re.fullmatch(r"[0-9]+[.][0-9]+[.][0-9]+", manifest["version"]):
        raise ValueError("Unexpected plugin identity or version")
    if set(manifest) != {"name", "version", "description", "author", "repository", "license", "skills"}:
        raise ValueError("Only the reviewed skill-only manifest fields are allowed")
    if manifest["skills"] != ["./skills/"]:
        raise ValueError("Unexpected skills directory")
    outputs = {}
    for path in [source / "SKILL.md", *sorted((source / "references").rglob("*.md"))]:
        if path.is_symlink():
            raise ValueError(f"Refusing symlink source: {path}")
        outputs[plugin / "skills/django-tdd" / path.relative_to(source)] = path.read_bytes()
    metadata = {key: value for key, value in manifest.items() if key != "skills"}
    outputs[plugin / ".codex-plugin/plugin.json"] = (json.dumps({**metadata, "skills": "./skills/"}, indent=2) + "\n").encode()
    outputs[plugin / "plugin.json"] = (json.dumps({"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", **metadata}, indent=2) + "\n").encode()
    outputs[plugin / "LICENSE"] = (root / "LICENSE").read_bytes()
    outputs[plugin / "skills/django-tdd/LICENSE"] = (root / "LICENSE").read_bytes()
    authored = {manifest_path, *(plugin / name for name in ("README.md", "CHANGELOG.md", "PROVENANCE.md"))}
    existing = {path for path in plugin.rglob("*") if path.is_file()}
    unexpected = existing - outputs.keys() - authored
    if unexpected:
        raise ValueError("Unexpected distribution files: " + ", ".join(str(path.relative_to(plugin)) for path in sorted(unexpected)))
    for path in plugin.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Refusing symlink output: {path}")
    changed = [path for path, data in outputs.items() if not path.exists() or path.read_bytes() != data]
    if check:
        if changed:
            for path in changed:
                print(f"Package drift: {path.relative_to(root)}")
            return 1
        print(f"Package matches canonical source: {manifest['name']} {manifest['version']}")
        return 0
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f"Packaged {manifest['name']} {manifest['version']}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on generated artifact drift")
    args = parser.parse_args()
    return package(Path(__file__).resolve().parents[1], check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
