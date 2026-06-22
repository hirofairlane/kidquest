"""ChallengeSet generator: prompt is pure; output is repaired, validated, safe."""
from __future__ import annotations

import copy

import pytest
from kidquest_content.challenges import (
    ChallengeSetInvalidError,
    UnsafeChallengeError,
    build_challenge_prompt,
    generate_challenge_set,
    repair_challenge_set,
    validate_challenge_set,
)
from kidquest_content.curricula import load_curriculum

PROFILE = {
    "profile_id": "youth_10yo",
    "age": 10,
    "difficulty_modifier": 1.0,
    "reinforce_concepts": [{"concept_id": "main_rivers", "subject": "geography"}],
}

VALID = {
    "schema_version": "1",
    "profile_id": "youth_10yo",
    "era": "greek_colonies",
    "language_default": "es",
    "sphinxes": [
        {
            "subject": "geography",
            "concept_tags": ["main_rivers"],
            "riddle": {"text": "What is the longest river of Spain?", "language": "en"},
            "answers": ["Tajo", "Tagus", "tajo"],
            "reward": {"gold": 1500},
        }
    ],
}


def test_prompt_is_deterministic_and_themed() -> None:
    curr = load_curriculum("youth_10yo")
    p1 = build_challenge_prompt(PROFILE, curr, "greek_colonies", 4)
    p2 = build_challenge_prompt(PROFILE, curr, "greek_colonies", 4)
    assert p1 == p2
    assert "Emporion" in p1  # era theme present
    assert "exactly 4 sphinxes" in p1
    assert p1.index("PRIORITY") < p1.index("Curriculum to draw from")  # reinforce first


def test_generate_returns_validated_set() -> None:
    cs = generate_challenge_set(PROFILE, load_curriculum("youth_10yo"), "greek_colonies",
                                generate=lambda p, s: copy.deepcopy(VALID))
    assert cs["sphinxes"][0]["answers"][0] == "Tajo"
    validate_challenge_set(cs)


def test_repair_fills_defaults() -> None:
    broken = {"sphinxes": [{"riddle": {"text": "Q"}, "answers": [], "concept_tags": []}]}
    fixed = repair_challenge_set(broken, "youth_10yo", "greek_colonies", 4)
    s = fixed["sphinxes"][0]
    assert s["answers"] == ["?"]
    assert s["reward"]["gold"] == 1000
    assert s["subject"] == "history"
    validate_challenge_set(fixed)


def test_invalid_set_raises() -> None:
    with pytest.raises(ChallengeSetInvalidError):
        validate_challenge_set({"schema_version": "1"})


def test_banned_text_is_rejected() -> None:
    bad = copy.deepcopy(VALID)
    bad["sphinxes"][0]["riddle"]["text"] = "this is nsfw"
    with pytest.raises(UnsafeChallengeError):
        generate_challenge_set(PROFILE, load_curriculum("youth_10yo"), "greek_colonies",
                               generate=lambda p, s: copy.deepcopy(bad))
