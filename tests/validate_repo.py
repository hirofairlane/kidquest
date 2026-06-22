#!/usr/bin/env python3
"""Static repository invariants, run by CI and locally.

Checks:
  * every JSON Schema in shared/schemas parses and is itself a valid schema;
  * committed example documents validate against their schema
    (generic profiles, curricula YAML, the minimal level fixture);
  * the schema version is in sync across the schema, the server, and the client;
  * PRIVACY GUARD: no real player profile is committed. The only profile JSON
    files allowed in the tree are the generic examples under
    shared/fixtures/profiles/ named ``generic_*.json``.

Exit non-zero on any failure.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "shared" / "schemas"
SKIP_DIRS = {".git", "node_modules", ".venv", "dist", "content-store", ".uv", "__pycache__"}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _validate(errors: list[str], schema_name: str, doc: dict, label: str) -> None:
    schema = _load_json(SCHEMAS / schema_name)
    validator = Draft202012Validator(schema)
    issues = sorted(validator.iter_errors(doc), key=lambda e: e.path)
    if issues:
        for e in issues:
            loc = "/".join(str(p) for p in e.path) or "<root>"
            errors.append(f"{label}: {loc}: {e.message}")
    else:
        print(f"OK   {label} validates against {schema_name}")


def check_schemas(errors: list[str]) -> None:
    for schema_path in sorted(SCHEMAS.glob("*.schema.json")):
        try:
            schema = _load_json(schema_path)
            Draft202012Validator.check_schema(schema)
            print(f"OK   schema {schema_path.name}")
        except Exception as exc:  # noqa: BLE001 - report any parse/meta error
            errors.append(f"schema invalid {schema_path.name}: {exc}")


def check_examples(errors: list[str]) -> None:
    for profile in sorted((ROOT / "shared" / "fixtures" / "profiles").glob("*.json")):
        _validate(errors, "player_profile.schema.json", _load_json(profile), profile.name)

    level = ROOT / "shared" / "fixtures" / "levels" / "minimal.json"
    _validate(errors, "daily_level.schema.json", _load_json(level), level.name)

    for curr in sorted((ROOT / "curricula" / "profiles").glob("*.yaml")):
        doc = yaml.safe_load(curr.read_text())
        _validate(errors, "curriculum.schema.json", doc, curr.name)


def check_version_sync(errors: list[str]) -> None:
    schema_version = _load_json(SCHEMAS / "daily_level.schema.json")[
        "properties"
    ]["schema_version"]["const"]

    server_src = (ROOT / "server" / "kidquest_server" / "__init__.py").read_text()
    server_v = _search(r'SCHEMA_VERSION\s*=\s*"([^"]+)"', server_src)

    client_src = (ROOT / "client" / "src" / "engine" / "contract.ts").read_text()
    client_v = _search(r'SUPPORTED_SCHEMA_VERSION\s*=\s*"([^"]+)"', client_src)

    if schema_version == server_v == client_v:
        print(f"OK   schema version in sync: {schema_version}")
    else:
        errors.append(
            "schema version mismatch: "
            f"schema={schema_version} server={server_v} client={client_v}"
        )


def check_no_private_profiles(errors: list[str]) -> None:
    """Privacy guard: forbid committing anything that looks like a real profile."""
    allowed = (ROOT / "shared" / "fixtures" / "profiles").resolve()
    for path in _walk(ROOT):
        name = path.name
        is_profile_file = (
            name.startswith("player_profile")
            and name.endswith(".json")
            and not name.endswith(".schema.json")
        )
        in_profiles_dir = path.parent.resolve() == allowed and name.endswith(".json")
        if is_profile_file:
            errors.append(f"PRIVACY: forbidden profile file committed: {path.relative_to(ROOT)}")
        elif in_profiles_dir and not name.startswith("generic_"):
            errors.append(
                f"PRIVACY: only generic_*.json profiles may be committed: {path.relative_to(ROOT)}"
            )
    print("OK   privacy guard: no real player profiles committed")


def _walk(root: Path):
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.is_file():
            yield p


def _search(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None


def main() -> int:
    errors: list[str] = []
    check_schemas(errors)
    check_examples(errors)
    check_version_sync(errors)
    check_no_private_profiles(errors)

    if errors:
        print("\nFAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nAll static checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
