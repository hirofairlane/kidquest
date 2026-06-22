"""Profile store tests — pure adaptive updates and disk round-trip."""
from __future__ import annotations

from kidquest_server.profile import (
    add_reinforce,
    default_profile,
    load_profile,
    record_clear,
    record_defeat,
    save_profile,
)


def test_default_profile_has_baseline_fields() -> None:
    p = default_profile("youth_10yo", age=10)
    assert p["difficulty_modifier"] == 1.0
    assert p["defeat_streak"] == 0
    assert p["reinforce_concepts"] == []


def test_record_defeat_increments_streak_without_mutating_input() -> None:
    p = default_profile("p")
    after = record_defeat(p)
    assert after["defeat_streak"] == 1
    assert p["defeat_streak"] == 0  # original untouched


def test_record_clear_resets_streak_and_bumps_difficulty_on_strong_clear() -> None:
    p = default_profile("p")
    p["defeat_streak"] = 3
    after = record_clear(p, hp_pct=0.9)
    assert after["defeat_streak"] == 0
    assert after["difficulty_modifier"] == 1.1


def test_record_clear_does_not_bump_at_exactly_80pct() -> None:
    after = record_clear(default_profile("p"), hp_pct=0.8)
    assert after["difficulty_modifier"] == 1.0


def test_add_reinforce_increments_existing_and_appends_new() -> None:
    p = default_profile("p")
    p = add_reinforce(p, [{"concept_id": "ohms_law", "subject": "electronics"}])
    p = add_reinforce(p, [{"concept_id": "ohms_law", "subject": "electronics"}])
    p = add_reinforce(p, [{"concept_id": "fractions_halves", "subject": "math"}])
    by_id = {c["concept_id"]: c for c in p["reinforce_concepts"]}
    assert by_id["ohms_law"]["failures"] == 2
    assert by_id["fractions_halves"]["failures"] == 1


def test_save_and_load_round_trip(tmp_path) -> None:
    p = default_profile("youth_10yo", age=10)
    p = record_defeat(p)
    save_profile(p, base=tmp_path)
    loaded = load_profile("youth_10yo", base=tmp_path)
    assert loaded == p


def test_load_missing_profile_returns_default(tmp_path) -> None:
    loaded = load_profile("brand_new", base=tmp_path)
    assert loaded["profile_id"] == "brand_new"
    assert loaded["defeat_streak"] == 0
