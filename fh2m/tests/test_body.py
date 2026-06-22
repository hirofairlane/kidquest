"""Body parsing/patching against real fheroes2 maps.

Correctness oracles:
- structural: every section of every map skips exactly to end-of-body;
- byte-exact: MapBody parse→serialize reproduces the body;
- content: 7_deserts.fh2m carries known human-readable Sphinx riddles.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from kidquest_fh2m import Fh2mContainer, MapBody, Sphinx, assert_fully_parsable

FIX = Path(__file__).parent / "fixtures"
FIXTURES = sorted(FIX.glob("*.fh2m"))


def _body(name: str) -> bytes:
    return Fh2mContainer.parse((FIX / name).read_bytes()).body


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_every_section_is_fully_parsable(path: Path) -> None:
    assert_fully_parsable(Fh2mContainer.parse(path.read_bytes()).body)


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_body_round_trips_byte_exact(path: Path) -> None:
    body = Fh2mContainer.parse(path.read_bytes()).body
    assert MapBody.parse(body).serialize() == body


def test_reads_known_sphinx_riddles() -> None:
    body = MapBody.parse(_body("7_deserts.fh2m"))
    assert len(body.sphinx) == 3
    oasis = next(s for s in body.sphinx if "oasis" in s.riddle.lower())
    assert "3" in oasis.answers


def test_patch_sphinx_riddle_and_reward() -> None:
    container = Fh2mContainer.parse((FIX / "7_deserts.fh2m").read_bytes())
    body = MapBody.parse(container.body)
    original_uids = [s.uid for s in body.sphinx]

    target = body.sphinx[0]
    target.riddle = "How much is one half of eight?"
    target.answers = ["4", "four", "Four", "FOUR"]
    target.resources = [0, 0, 0, 0, 0, 0, 1500]  # +1500 gold reward

    patched_bytes = container.with_body(body.serialize()).serialize()

    # Re-read the whole file through the pipeline and confirm the patch stuck.
    reparsed = MapBody.parse(Fh2mContainer.parse(patched_bytes).body)
    assert_fully_parsable(Fh2mContainer.parse(patched_bytes).body)
    assert [s.uid for s in reparsed.sphinx] == original_uids  # structure preserved
    patched = reparsed.sphinx[0]
    assert patched.riddle == "How much is one half of eight?"
    assert patched.answers == ["4", "four", "Four", "FOUR"]
    assert patched.resources[6] == 1500
    # other sphinxes untouched
    assert reparsed.sphinx[1].riddle == body.sphinx[1].riddle


def test_sphinx_dataclass_defaults() -> None:
    s = Sphinx(uid=1, riddle="q", answers=["a"])
    assert s.resources == [0] * 7
    assert s.artifact == 0
