"""Game Director adaptive rules — authoritative implementation.

The client carries an advisory copy in TypeScript
(`client/src/engine/director/DirectorRules.ts`). Both are checked against the
same golden vectors (`shared/fixtures/director/cases.json`) so they cannot drift.
Pure functions: no I/O, no globals.
"""
from __future__ import annotations

from typing import Literal, TypedDict

LevelResult = Literal["cleared", "defeated"]

DIFFICULTY_STEP = 1.1
STRONG_CLEAR_HP = 0.8


class ReinforceConcept(TypedDict):
    concept_id: str
    subject: str
    failures: int


class FailedConcept(TypedDict):
    concept_id: str
    subject: str


def update_reinforce(
    reinforce: list[ReinforceConcept],
    failed: list[FailedConcept],
) -> list[ReinforceConcept]:
    """REQ-GAM-01: fold failed concepts into the reinforcement list.

    Existing concepts increment in place (keeping order); new concepts are
    appended in input order with a failure count of 1.
    """
    result: list[ReinforceConcept] = [dict(r) for r in reinforce]  # type: ignore[misc]
    index: dict[str, ReinforceConcept] = {r["concept_id"]: r for r in result}
    for item in failed:
        cid = item["concept_id"]
        existing = index.get(cid)
        if existing is not None:
            existing["failures"] += 1
        else:
            entry: ReinforceConcept = {
                "concept_id": cid,
                "subject": item["subject"],
                "failures": 1,
            }
            result.append(entry)
            index[cid] = entry
    return result


def should_spawn_artifact(
    defeat_streak: int,
    elapsed_seconds: float,
    time_limit_seconds: float,
) -> bool:
    """REQ-GAM-02: Magic Artifact after two straight defeats or a too-long level."""
    return defeat_streak >= 2 or elapsed_seconds > time_limit_seconds


def next_difficulty(difficulty_modifier: float, result: LevelResult, hp_pct: float) -> float:
    """REQ-GAM-03: a clear with more than 80% HP raises difficulty by 10%."""
    if result == "cleared" and hp_pct > STRONG_CLEAR_HP:
        return round(difficulty_modifier * DIFFICULTY_STEP, 4)
    return difficulty_modifier
