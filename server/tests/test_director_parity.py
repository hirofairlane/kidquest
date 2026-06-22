"""Parity tests: the Python director rules must match the shared golden vectors
(the same JSON the TypeScript suite uses). This is what keeps the two
implementations from drifting.
"""
from __future__ import annotations

import json
from pathlib import Path

from kidquest_server.director import (
    next_difficulty,
    should_spawn_artifact,
    update_reinforce,
)

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / "shared" / "fixtures" / "director" / "cases.json").read_text())


def test_feedback_loop_cases() -> None:
    for case in CASES["feedback_loop"]:
        out = update_reinforce(case["input"]["reinforce"], case["input"]["failed"])
        assert out == case["expected"], case["name"]


def test_anti_frustration_cases() -> None:
    for case in CASES["anti_frustration"]:
        i = case["input"]
        got = should_spawn_artifact(
            i["defeat_streak"], i["elapsed_seconds"], i["time_limit_seconds"]
        )
        assert got is case["expected"]["spawn_artifact"], case["name"]


def test_dynamic_difficulty_cases() -> None:
    for case in CASES["dynamic_difficulty"]:
        i = case["input"]
        got = next_difficulty(i["difficulty_modifier"], i["result"], i["hp_pct"])
        assert got == case["expected"]["difficulty_modifier"], case["name"]
