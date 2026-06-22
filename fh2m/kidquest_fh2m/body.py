"""Parse the (zlib-decompressed) MapFormat body to read/patch the educational
metadata (Sphinx riddles), preserving everything else byte-exact.

Strategy: the body is 15 concatenated sections (see FORMAT.md). We *skip* over the
sections before and after ``sphinxMetadata`` (advancing the cursor per the exact
serialization rules) and keep them as raw byte slices; only ``sphinxMetadata`` is
parsed into typed objects. Re-serialization is therefore byte-exact for the
untouched parts, and exact for sphinx as long as our read/write is symmetric.

Two oracles guard correctness (see tests):
- structural: skipping ALL 15 sections must land exactly at end-of-body;
- content: kk.fh2m's sphinx must decode to the riddle the author typed.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .stream import StreamReader, StreamWriter

# ── primitive skips (advance the cursor by the serialized size) ───────────────


def _skip_bytes(r: StreamReader, n: int) -> None:
    r.read_raw(n)


def _skip_string(r: StreamReader) -> None:
    r.read_raw(r.u32())


def _skip_vec(r: StreamReader, skip_elem) -> None:  # noqa: ANN001
    for _ in range(r.u32()):
        skip_elem(r)


def _skip_map(r: StreamReader, skip_key, skip_val) -> None:  # noqa: ANN001
    for _ in range(r.u32()):
        skip_key(r)
        skip_val(r)


def _u8(r: StreamReader) -> None:
    r.read_raw(1)


def _u32(r: StreamReader) -> None:
    r.read_raw(4)


def _i32(r: StreamReader) -> None:
    r.read_raw(4)


def _funds(r: StreamReader) -> None:
    r.read_raw(28)  # 7 x int32


# ── struct skips (field order per FORMAT.md) ──────────────────────────────────


def _skip_tile_object(r: StreamReader) -> None:
    r.read_raw(4 + 1 + 4)  # id u32, group u8, index u32


def _skip_tile(r: StreamReader) -> None:
    r.read_raw(2 + 1)  # terrainIndex u16, terrainFlags u8
    _skip_vec(r, _skip_tile_object)


def _skip_daily_event(r: StreamReader) -> None:
    _skip_string(r)
    r.read_raw(1 + 1 + 4 + 4)  # human u8, computer u8, firstDay u32, repeat u32
    _funds(r)


def _skip_castle(r: StreamReader) -> None:
    _skip_string(r)  # customName
    _skip_vec(r, _i32)  # defenderMonsterType array<i32,5>
    _skip_vec(r, _i32)  # defenderMonsterCount array<i32,5>
    r.read_raw(1)  # customBuildings bool
    _skip_vec(r, _u32)  # builtBuildings
    _skip_vec(r, _u32)  # bannedBuildings
    _skip_map(r, _u8, _i32)  # mustHaveSpells map<u8,i32>
    _skip_vec(r, _i32)  # bannedSpells
    _skip_vec(r, _i32)  # availableToHireMonsterCount array<i32,6>


def _skip_hero(r: StreamReader) -> None:
    _skip_string(r)  # customName
    r.read_raw(4)  # customPortrait i32
    _skip_vec(r, _i32)  # armyMonsterType
    _skip_vec(r, _i32)  # armyMonsterCount
    _skip_vec(r, _i32)  # artifact
    _skip_vec(r, _i32)  # artifactMetadata
    _skip_vec(r, _i32)  # availableSpells
    r.read_raw(1 + 1)  # isOnPatrol bool, patrolRadius u8
    _skip_vec(r, _u8)  # secondarySkill array<i8,8>
    _skip_vec(r, _u8)  # secondarySkillLevel array<u8,8>
    r.read_raw(2 + 4 + 2 + 2 + 2 + 2 + 2 + 1)
    # customLevel i16, customExperience i32, customAttack/Defense/Knowledge/SpellPower i16,
    # magicPoints i16, race u8


def _skip_sphinx(r: StreamReader) -> None:
    _skip_string(r)  # riddle
    _skip_vec(r, _skip_string)  # answers
    r.read_raw(4 + 4)  # artifact i32, artifactMetadata i32
    _funds(r)


def _skip_sign(r: StreamReader) -> None:
    _skip_string(r)


def _skip_adv_event(r: StreamReader) -> None:
    _skip_string(r)  # message
    r.read_raw(1 + 1 + 1 + 4 + 4)  # human u8, computer u8, isRecurring bool, artifact i32, artMeta i32
    _funds(r)
    r.read_raw(2 + 2 + 2 + 2 + 4 + 1 + 1 + 4 + 4)
    # attack/defense/knowledge/spellPower i16, experience i32, secSkill u8, secSkillLvl u8,
    # monsterType i32, monsterCount i32


def _skip_selection(r: StreamReader) -> None:
    _skip_vec(r, _i32)


def _skip_capturable(r: StreamReader) -> None:
    r.read_raw(1)  # ownerColor u8


def _skip_monster(r: StreamReader) -> None:
    r.read_raw(4 + 4 + 1)  # count i32, joinCondition i32, isWeeklyGrowthDisabled bool
    _skip_vec(r, _i32)  # selected


def _skip_artifact(r: StreamReader) -> None:
    r.read_raw(4 + 4)  # radius i32, captureCondition i32
    _skip_vec(r, _i32)  # selected


def _skip_resource(r: StreamReader) -> None:
    r.read_raw(4)  # count i32


def _skip_translation_sphinx(r: StreamReader) -> None:
    _skip_string(r)  # riddle
    _skip_vec(r, _skip_string)  # answers


def _skip_translation_format(r: StreamReader) -> None:
    _skip_vec(r, _skip_string)  # dailyEvents
    _skip_vec(r, _skip_string)  # rumors
    _skip_map(r, _u32, _skip_string)  # castleMetadata
    _skip_map(r, _u32, _skip_string)  # heroMetadata
    _skip_map(r, _u32, _skip_translation_sphinx)  # sphinxMetadata
    _skip_map(r, _u32, _skip_string)  # signMetadata
    _skip_map(r, _u32, _skip_string)  # adventureMapEventMetadata


# Sections 1..6 (skipped), and 8..15 (skipped). Section 7 (sphinx) is parsed.
def _skip_sections_before_sphinx(r: StreamReader) -> None:
    _skip_vec(r, _u32)  # 1 additionalInfo
    _skip_vec(r, _skip_tile)  # 2 tiles
    _skip_vec(r, _skip_daily_event)  # 3 dailyEvents
    _skip_vec(r, _skip_string)  # 4 rumors
    _skip_map(r, _u32, _skip_castle)  # 5 castleMetadata
    _skip_map(r, _u32, _skip_hero)  # 6 heroMetadata


def _skip_sections_after_sphinx(r: StreamReader) -> None:
    _skip_map(r, _u32, _skip_sign)  # 8 signMetadata
    _skip_map(r, _u32, _skip_adv_event)  # 9 adventureMapEventMetadata
    _skip_map(r, _u32, _skip_selection)  # 10 selectionObjectMetadata
    _skip_map(r, _u32, _skip_capturable)  # 11 capturableObjectsMetadata
    _skip_map(r, _u32, _skip_monster)  # 12 monsterMetadata
    _skip_map(r, _u32, _skip_artifact)  # 13 artifactMetadata
    _skip_map(r, _u32, _skip_resource)  # 14 resourceMetadata
    _skip_map(r, _u8, _skip_translation_format)  # 15 translationInfo


# ── typed Sphinx section (the part we patch) ──────────────────────────────────


@dataclass
class Sphinx:
    uid: int
    riddle: str
    answers: list[str]
    artifact: int = 0
    artifact_metadata: int = 0
    resources: list[int] = field(default_factory=lambda: [0] * 7)  # wood..gold


def _read_sphinx_section(r: StreamReader) -> list[Sphinx]:
    out: list[Sphinx] = []
    for _ in range(r.u32()):
        uid = r.u32()
        riddle = r.string()
        answers = [r.string() for _ in range(r.u32())]
        artifact = r.i32()
        artifact_metadata = r.i32()
        resources = [r.i32() for _ in range(7)]
        out.append(Sphinx(uid, riddle, answers, artifact, artifact_metadata, resources))
    return out


def _write_sphinx_section(entries: list[Sphinx]) -> bytes:
    w = StreamWriter()
    w.u32(len(entries))
    for e in entries:
        w.u32(e.uid)
        w.string(e.riddle)
        w.u32(len(e.answers))
        for a in e.answers:
            w.string(a)
        w.i32(e.artifact)
        w.i32(e.artifact_metadata)
        for v in e.resources:
            w.i32(v)
    return w.getvalue()


class MapBody:
    """A parsed body split as: prefix (sections 1-6) | sphinx (7, typed) | tail (8-15)."""

    def __init__(self, prefix: bytes, sphinx: list[Sphinx], tail: bytes) -> None:
        self.prefix = prefix
        self.sphinx = sphinx
        self.tail = tail

    @classmethod
    def parse(cls, body: bytes) -> "MapBody":
        r = StreamReader(body)
        _skip_sections_before_sphinx(r)
        sphinx_start = r.pos
        sphinx = _read_sphinx_section(r)
        sphinx_end = r.pos
        return cls(prefix=body[:sphinx_start], sphinx=sphinx, tail=body[sphinx_end:])

    def serialize(self) -> bytes:
        return self.prefix + _write_sphinx_section(self.sphinx) + self.tail


def assert_fully_parsable(body: bytes) -> None:
    """Structural oracle: skipping all 15 sections lands exactly at end-of-body."""
    r = StreamReader(body)
    _skip_sections_before_sphinx(r)
    _skip_map(r, _u32, _skip_sphinx)  # 7 sphinxMetadata
    _skip_sections_after_sphinx(r)
    if r.pos != len(body):
        raise ValueError(f"body not fully consumed: {r.pos} of {len(body)} bytes")
