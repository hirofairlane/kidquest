"""Validate a generated daily level against the JSON Schema AND the cross-field
invariants the schema cannot express. The orchestrator never publishes a level
that does not pass this gate.

Mirrors the client-side LevelLoader checks so client and server agree on what a
"valid level" is.
"""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = _REPO_ROOT / "shared" / "schemas" / "daily_level.schema.json"


class LevelInvalidError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text())


def _hex_distance(q: int, r: int) -> int:
    return (abs(q) + abs(r) + abs(q + r)) // 2


def cross_field_errors(level: dict) -> list[str]:
    errors: list[str] = []
    ow = level.get("overworld", {})
    width, height = ow.get("width"), ow.get("height")
    matrix = ow.get("matrix", [])
    legend = ow.get("tile_legend", {})

    if isinstance(matrix, list):
        if height is not None and len(matrix) != height:
            errors.append(f"matrix has {len(matrix)} rows, expected {height}")
        for y, row in enumerate(matrix):
            if width is not None and len(row) != width:
                errors.append(f"matrix row {y} has {len(row)} cols, expected {width}")
            for tile in row:
                if str(tile) not in legend:
                    errors.append(f"tile id {tile} missing from legend")

    ids = {p["id"] for p in level.get("puzzles", [])}
    dids = {d["id"] for d in level.get("dialogues", [])}
    eids = {e["id"] for e in level.get("encounters", [])}
    for ent in level.get("entities", []):
        for ref_key, pool, kind in (
            ("puzzle_ref", ids, "puzzle"),
            ("dialogue_ref", dids, "dialogue"),
            ("encounter_ref", eids, "encounter"),
        ):
            ref = ent.get(ref_key)
            if ref and ref not in pool:
                errors.append(f"entity {ent.get('id')} references unknown {kind} {ref}")

    for enc in level.get("encounters", []):
        units = enc.get("units", [])
        if not any(u.get("team") == "player" for u in units):
            errors.append(f"encounter {enc.get('id')} has no player unit")
        radius = enc.get("hex_radius", 0)
        for u in units:
            ax = u.get("axial", {})
            if _hex_distance(ax.get("q", 0), ax.get("r", 0)) > radius:
                errors.append(f"unit {u.get('id')} outside encounter {enc.get('id')} radius")
    return errors


def validate_level(level: dict, schema: dict | None = None) -> None:
    """Raise LevelInvalidError if the level fails schema or invariant checks."""
    schema = schema or load_schema()
    validator = Draft202012Validator(schema)
    errors = [
        f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(level), key=lambda e: list(e.path))
    ]
    errors.extend(cross_field_errors(level))
    if errors:
        raise LevelInvalidError(errors)
