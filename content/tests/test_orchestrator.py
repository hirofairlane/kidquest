"""Orchestrator: repair-retry on invalid output, never publish invalid content."""
from __future__ import annotations

import copy

import pytest
from kidquest_content.orchestrator import GenerationError, generate_daily


class FakeRunner:
    def synthesize(self, text, voice, out_path):  # noqa: ANN001
        out_path.write_bytes(b"WAV")


PROFILE = {"profile_id": "youth_10yo", "age": 10, "difficulty_modifier": 1.0, "reinforce_concepts": []}
CURRICULUM = {"curriculum_ref": "youth_10yo", "subjects": [
    {"subject": "math", "language": "es", "concepts": [{"concept_id": "fractions_halves", "label": "x", "difficulty": 3}]}
]}


def test_publishes_a_valid_level(tmp_path, valid_level) -> None:
    def generate(prompt, schema):  # noqa: ANN001
        return copy.deepcopy(valid_level)

    dest = generate_daily(
        PROFILE, CURRICULUM, tmp_path, "2026-06-22", generate=generate, runner=FakeRunner()
    )
    assert (dest / "level.json").exists()
    assert (dest / "audio").exists()


def test_repair_retry_recovers_from_one_invalid_response(tmp_path, valid_level) -> None:
    invalid = copy.deepcopy(valid_level)
    del invalid["puzzles"][0]["answer"]
    responses = [invalid, copy.deepcopy(valid_level)]

    def generate(prompt, schema):  # noqa: ANN001
        return responses.pop(0)

    dest = generate_daily(
        PROFILE, CURRICULUM, tmp_path, "2026-06-22", generate=generate, runner=FakeRunner(), max_attempts=3
    )
    assert (dest / "level.json").exists()
    assert responses == []  # both attempts consumed


def test_never_publishes_invalid_content(tmp_path, valid_level) -> None:
    invalid = copy.deepcopy(valid_level)
    del invalid["puzzles"][0]["answer"]

    def generate(prompt, schema):  # noqa: ANN001
        return copy.deepcopy(invalid)

    with pytest.raises(GenerationError):
        generate_daily(
            PROFILE, CURRICULUM, tmp_path, "2026-06-22", generate=generate, runner=FakeRunner(), max_attempts=2
        )
    assert not (tmp_path / "youth_10yo" / "2026-06-22" / "level.json").exists()
