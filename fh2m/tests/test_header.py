"""Header name read/patch."""
from __future__ import annotations

from pathlib import Path

from kidquest_fh2m import assert_fully_parsable, read_map_name, set_map_name
from kidquest_fh2m.container import Fh2mContainer

FIX = Path(__file__).parent / "fixtures"


def test_read_known_name() -> None:
    assert read_map_name((FIX / "Ravenhold.fh2m").read_bytes()) == "Ravenhold"


def test_set_name_round_trips_and_keeps_body() -> None:
    original = (FIX / "7_deserts.fh2m").read_bytes()
    renamed = set_map_name(original, "Arturo - Reto 1")
    assert read_map_name(renamed) == "Arturo - Reto 1"
    # body is untouched (same decompressed payload), still fully parsable
    assert Fh2mContainer.parse(renamed).body == Fh2mContainer.parse(original).body
    assert_fully_parsable(Fh2mContainer.parse(renamed).body)
