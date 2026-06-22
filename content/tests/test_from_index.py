"""Curated-index -> ChallengeSet -> medal-bearing patched map."""
from __future__ import annotations

from pathlib import Path

import pytest
from kidquest_content.from_index import index_to_challenge_set, load_index
from kidquest_content.medals import MEDAL_POOL, MedalError, assign_medals
from kidquest_content.scenario_patcher import patch_scenario
from kidquest_fh2m import MapBody
from kidquest_fh2m.container import Fh2mContainer

INDEX_DIR = Path(__file__).resolve().parents[1] / "index"
TEMPLATE = Path(__file__).resolve().parents[2] / "fh2m" / "tests" / "fixtures" / "7_deserts.fh2m"


@pytest.mark.parametrize("name", ["astrid", "arturo", "sergio"])
def test_index_builds_valid_challenge_set(name: str) -> None:
    cs = index_to_challenge_set(load_index(INDEX_DIR / f"{name}.yaml"))
    assert cs["sphinxes"]  # non-empty and schema-valid (validated inside)
    # every item carries verified answers
    assert all(s["answers"] for s in cs["sphinxes"])


def test_astrid_content_is_all_spanish() -> None:
    cs = index_to_challenge_set(load_index(INDEX_DIR / "astrid.yaml"))
    assert all(s["riddle"]["language"] == "es" for s in cs["sphinxes"])


def test_arturo_english_only_for_english_subject() -> None:
    cs = index_to_challenge_set(load_index(INDEX_DIR / "arturo.yaml"))
    for s in cs["sphinxes"]:
        expected = "en" if s["subject"] == "english" else "es"
        assert s["riddle"]["language"] == expected


def test_assign_medals_distinct_and_bounded() -> None:
    medals = assign_medals(3)
    assert len(medals) == 3
    assert len({m[0] for m in medals}) == 3  # distinct artifact ids
    with pytest.raises(MedalError):
        assign_medals(len(MEDAL_POOL) + 1)


def test_patch_sets_medal_artifacts() -> None:
    cs = index_to_challenge_set(load_index(INDEX_DIR / "arturo.yaml"))
    medal_ids = [m[0] for m in assign_medals(3)]
    patched, stats = patch_scenario(TEMPLATE.read_bytes(), cs, name="Arturo", artifacts=medal_ids)
    body = MapBody.parse(Fh2mContainer.parse(patched).body)
    assert [s.artifact for s in body.sphinx] == medal_ids
    assert stats["patched"] == 3
