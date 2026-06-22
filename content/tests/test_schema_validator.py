"""Schema + cross-field validation of generated levels."""
from __future__ import annotations

import pytest
from kidquest_content.schema_validator import LevelInvalidError, validate_level


def test_valid_level_passes(valid_level) -> None:
    validate_level(valid_level)  # must not raise


def test_missing_required_field_fails(valid_level) -> None:
    del valid_level["puzzles"][0]["answer"]
    with pytest.raises(LevelInvalidError):
        validate_level(valid_level)


def test_matrix_dimension_mismatch_fails(valid_level) -> None:
    valid_level["overworld"]["matrix"].append([0, 0, 0])  # extra row
    with pytest.raises(LevelInvalidError) as exc:
        validate_level(valid_level)
    assert any("matrix" in e for e in exc.value.errors)


def test_dangling_reference_fails(valid_level) -> None:
    valid_level["entities"][0]["puzzle_ref"] = "nope"
    with pytest.raises(LevelInvalidError) as exc:
        validate_level(valid_level)
    assert any("unknown puzzle" in e for e in exc.value.errors)


def test_unit_outside_radius_fails(valid_level) -> None:
    valid_level["encounters"][0]["units"][1]["axial"] = {"q": 9, "r": 0}
    with pytest.raises(LevelInvalidError) as exc:
        validate_level(valid_level)
    assert any("outside encounter" in e for e in exc.value.errors)


def test_encounter_without_player_fails(valid_level) -> None:
    valid_level["encounters"][0]["units"][0]["team"] = "enemy"
    with pytest.raises(LevelInvalidError) as exc:
        validate_level(valid_level)
    assert any("no player unit" in e for e in exc.value.errors)
