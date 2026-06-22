"""Bake a ChallengeSet (the AI-authored educational layer) into a fheroes2 .fh2m
template: assign each Sphinx slot a riddle + accepted answers + resource reward,
and optionally rename the map.

Bridges the KidQuest content schema to the generic fheroes2 format library.
"""
from __future__ import annotations

from kidquest_fh2m import Fh2mContainer, MapBody, set_map_name

# fheroes2 Funds serialization order.
_FUNDS_ORDER = ("wood", "mercury", "ore", "sulfur", "crystal", "gems", "gold")


class PatchError(ValueError):
    pass


def reward_to_funds(reward: dict) -> list[int]:
    return [int(reward.get(k, 0)) for k in _FUNDS_ORDER]


def patch_scenario(template_bytes: bytes, challenge_set: dict, *, name: str | None = None) -> tuple[bytes, dict]:
    """Patch a template with a ChallengeSet's Sphinx riddles. Returns (bytes, stats).

    Challenges are assigned to Sphinx slots in order; extra challenges or extra
    slots are reported in the stats so the caller can warn.
    """
    container = Fh2mContainer.parse(template_bytes)
    body = MapBody.parse(container.body)
    challenges = challenge_set.get("sphinxes", [])

    if not body.sphinx:
        raise PatchError("template has no Sphinx slots to patch")

    count = min(len(body.sphinx), len(challenges))
    for slot, ch in zip(body.sphinx[:count], challenges[:count]):
        slot.riddle = ch["riddle"]["text"]
        slot.answers = list(ch["answers"])
        slot.artifact = 0
        slot.artifact_metadata = 0
        slot.resources = reward_to_funds(ch.get("reward", {}))

    out = container.with_body(body.serialize()).serialize()
    if name is not None:
        out = set_map_name(out, name)

    stats = {"slots": len(body.sphinx), "challenges": len(challenges), "patched": count}
    return out, stats
