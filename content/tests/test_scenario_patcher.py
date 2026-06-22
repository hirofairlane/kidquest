"""Patch a ChallengeSet's riddles into a .fh2m template."""
from __future__ import annotations

from pathlib import Path

import pytest
from kidquest_content.scenario_patcher import PatchError, patch_scenario, reward_to_funds
from kidquest_fh2m import MapBody, assert_fully_parsable, read_map_name
from kidquest_fh2m.container import Fh2mContainer

TEMPLATE = Path(__file__).resolve().parents[2] / "fh2m" / "tests" / "fixtures" / "7_deserts.fh2m"


def _challenge_set(n: int) -> dict:
    return {
        "schema_version": "1",
        "profile_id": "youth_10yo",
        "era": "greek_colonies",
        "language_default": "es",
        "sphinxes": [
            {
                "subject": "math",
                "concept_tags": ["x"],
                "riddle": {"text": f"Riddle number {i}", "language": "es"},
                "answers": [str(i), f"answer{i}"],
                "reward": {"gold": 100 * i},
            }
            for i in range(1, n + 1)
        ],
    }


def test_reward_to_funds_order() -> None:
    # order: wood, mercury, ore, sulfur, crystal, gems, gold
    assert reward_to_funds({"gold": 500, "wood": 3}) == [3, 0, 0, 0, 0, 0, 500]


def test_patch_assigns_riddles_to_slots() -> None:
    template = TEMPLATE.read_bytes()
    patched, stats = patch_scenario(template, _challenge_set(3), name="Arturo - Reto 1")
    assert stats == {"slots": 3, "challenges": 3, "patched": 3}
    assert read_map_name(patched) == "Arturo - Reto 1"
    assert_fully_parsable(Fh2mContainer.parse(patched).body)

    body = MapBody.parse(Fh2mContainer.parse(patched).body)
    assert [s.riddle for s in body.sphinx] == ["Riddle number 1", "Riddle number 2", "Riddle number 3"]
    assert body.sphinx[0].answers == ["1", "answer1"]
    assert body.sphinx[2].resources[6] == 300  # gold of the 3rd reward


def test_more_challenges_than_slots_is_reported() -> None:
    patched, stats = patch_scenario(TEMPLATE.read_bytes(), _challenge_set(5))
    assert stats["slots"] == 3 and stats["challenges"] == 5 and stats["patched"] == 3


def test_template_without_slots_raises() -> None:
    # an empty-ish challenge set still needs slots; use a body with 0 sphinx by
    # constructing one is overkill — assert the error path via a doctored template.
    with pytest.raises(PatchError):
        # 7_deserts HAS slots, so force the no-slot path by clearing them:
        from kidquest_fh2m import Fh2mContainer as C

        c = C.parse(TEMPLATE.read_bytes())
        body = MapBody.parse(c.body)
        body.sphinx = []
        patch_scenario(c.with_body(body.serialize()).serialize(), _challenge_set(1))
