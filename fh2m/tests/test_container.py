"""Container round-trip against real fheroes2 sample maps (no game assets needed)."""
from __future__ import annotations

from pathlib import Path

import pytest
from kidquest_fh2m import FORMAT_VERSION, Fh2mContainer

FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("*.fh2m"))


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_parse_reports_version_13(path: Path) -> None:
    c = Fh2mContainer.parse(path.read_bytes())
    assert c.version == FORMAT_VERSION
    assert c.header.startswith(b"h2map\x00")
    assert len(c.body) > len(c.header)  # decompressed body dwarfs the small header


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_round_trip_preserves_header_and_body(path: Path) -> None:
    original = Fh2mContainer.parse(path.read_bytes())
    # Re-serialize (recompresses the body) then parse again.
    reparsed = Fh2mContainer.parse(original.serialize())
    assert reparsed.header == original.header
    assert reparsed.body == original.body


def test_rejects_non_fh2m() -> None:
    with pytest.raises(Exception):
        Fh2mContainer.parse(b"not a map at all............")


def test_with_body_replaces_payload(path: Path = None) -> None:  # type: ignore[assignment]
    c = Fh2mContainer.parse(FIXTURES[0].read_bytes())
    patched = c.with_body(c.body + b"")  # identity replacement
    assert Fh2mContainer.parse(patched.serialize()).body == c.body
