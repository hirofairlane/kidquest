"""Contract test: the server's schema version matches the shared JSON Schema.

This is the server-side half of the single-source-of-truth guarantee; the client
has an equivalent test. If the schema bumps its version, both must update.
"""
from __future__ import annotations

import json
from pathlib import Path

from kidquest_server import SCHEMA_VERSION

ROOT = Path(__file__).resolve().parents[2]


def test_schema_version_matches_shared_schema() -> None:
    schema = json.loads(
        (ROOT / "shared" / "schemas" / "daily_level.schema.json").read_text()
    )
    const = schema["properties"]["schema_version"]["const"]
    assert SCHEMA_VERSION == const
