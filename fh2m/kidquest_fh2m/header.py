"""Read/patch fields in the uncompressed BaseMapFormat header.

Only the map display name is needed for now (so generated scenarios show distinct
titles in fheroes2). The name lives in the uncompressed header, so we splice it in
place and keep the original zlib body bytes untouched (no recompression).
"""
from __future__ import annotations

from .container import Fh2mContainer
from .stream import StreamReader, StreamWriter


def _offset_of_name(header: bytes) -> int:
    """Byte offset of the `name` string within the header (after `mainLanguage`)."""
    r = StreamReader(header)
    r.read_raw(6)  # magic
    r.u16()  # version
    r.u8()  # isCampaign
    r.u8()  # difficulty
    r.u8()  # availablePlayerColors
    r.u8()  # humanPlayerColors
    r.u8()  # computerPlayerColors
    for _ in range(r.u32()):  # alliances vector<u8>
        r.u8()
    for _ in range(r.u32()):  # playerRace array<u8,6>
        r.u8()
    r.u8()  # victoryConditionType
    r.u8()  # isVictoryConditionApplicableForAI
    r.u8()  # allowNormalVictory
    for _ in range(r.u32()):  # victoryConditionMetadata vector<u32>
        r.u32()
    r.u8()  # lossConditionType
    for _ in range(r.u32()):  # lossConditionMetadata vector<u32>
        r.u32()
    r.i32()  # width
    r.u8()  # mainLanguage
    return r.pos  # name string starts here


def read_map_name(data: bytes) -> str:
    header = Fh2mContainer.parse(data).header
    r = StreamReader(header)
    r.pos = _offset_of_name(header)
    return r.string()


def set_map_name(data: bytes, new_name: str) -> bytes:
    """Return a copy of the .fh2m bytes with the map's display name replaced."""
    container = Fh2mContainer.parse(data)
    header = container.header
    name_start = _offset_of_name(header)
    r = StreamReader(header)
    r.pos = name_start
    name_len = r.u32()
    name_end = r.pos + name_len

    w = StreamWriter()
    w.string(new_name)
    new_header = header[:name_start] + w.getvalue() + header[name_end:]

    body_zlib = data[len(header):]  # original compressed body, untouched
    return new_header + body_zlib
