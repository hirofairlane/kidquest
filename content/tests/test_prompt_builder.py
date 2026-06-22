"""Prompt builder is pure, deterministic, and prioritizes reinforcement."""
from __future__ import annotations

from kidquest_content.curricula import load_curriculum
from kidquest_content.prompt_builder import build_prompt


def test_prompt_is_deterministic() -> None:
    profile = {"profile_id": "youth_10yo", "age": 10, "difficulty_modifier": 1.0, "reinforce_concepts": []}
    curriculum = load_curriculum("youth_10yo")
    assert build_prompt(profile, curriculum) == build_prompt(profile, curriculum)


def test_reinforced_concepts_appear_before_the_curriculum() -> None:
    profile = {
        "profile_id": "youth_10yo",
        "age": 10,
        "difficulty_modifier": 1.0,
        "reinforce_concepts": [{"concept_id": "fractions_halves", "subject": "math", "failures": 2}],
    }
    prompt = build_prompt(profile, load_curriculum("youth_10yo"))
    assert prompt.index("PRIORITY") < prompt.index("Curriculum to cover")
    assert "fractions_halves" in prompt


def test_subject_language_is_stated_for_english_science_child() -> None:
    profile = {"profile_id": "child_6yo", "age": 6, "difficulty_modifier": 1.0, "reinforce_concepts": []}
    prompt = build_prompt(profile, load_curriculum("child_6yo"))
    assert "science_en [present in en]" in prompt


def test_adult_profile_is_pure_data_electronics() -> None:
    profile = {"profile_id": "adult_artificer", "age": 40, "difficulty_modifier": 1.0, "reinforce_concepts": []}
    prompt = build_prompt(profile, load_curriculum("adult_artificer"))
    assert "electronics" in prompt
    assert "ohms_law" in prompt
