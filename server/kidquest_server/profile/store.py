"""Player profile store.

The pure update functions (`record_defeat`, `record_clear`, `add_reinforce`)
return a new profile dict and never touch disk, so they unit-test without I/O.
`load_profile`/`save_profile` are the thin filesystem layer.

Adaptive updates delegate to the authoritative Game Director rules so the streak,
difficulty modifier and reinforcement list stay consistent with the client.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from ..config import data_dir
from ..director import next_difficulty, update_reinforce


def default_profile(profile_id: str, *, age: int = 0, curriculum_ref: str | None = None) -> dict:
    return {
        "profile_id": profile_id,
        "age": age,
        "curriculum_ref": curriculum_ref or profile_id,
        "difficulty_modifier": 1.0,
        "defeat_streak": 0,
        "last_level_started_at": None,
        "reinforce_concepts": [],
        "mastered_concepts": [],
        "history": [],
    }


def _path(profile_id: str, base: Path | None) -> Path:
    return (base or data_dir()) / f"{profile_id}.json"


def load_profile(profile_id: str, base: Path | None = None) -> dict:
    """Load a profile, or return a fresh default if none exists yet."""
    path = _path(profile_id, base)
    if path.exists():
        return json.loads(path.read_text())
    return default_profile(profile_id)


def save_profile(profile: dict, base: Path | None = None) -> Path:
    path = _path(profile["profile_id"], base)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    tmp.replace(path)
    return path


def record_defeat(profile: dict) -> dict:
    """A loss bumps the defeat streak (feeds REQ-GAM-02)."""
    updated = copy.deepcopy(profile)
    updated["defeat_streak"] = int(updated.get("defeat_streak", 0)) + 1
    return updated


def record_clear(profile: dict, hp_pct: float) -> dict:
    """A clear resets the streak and may raise difficulty (REQ-GAM-03)."""
    updated = copy.deepcopy(profile)
    updated["defeat_streak"] = 0
    updated["difficulty_modifier"] = next_difficulty(
        float(updated.get("difficulty_modifier", 1.0)), "cleared", hp_pct
    )
    return updated


def add_reinforce(profile: dict, failed: list[dict]) -> dict:
    """Fold failed concepts into the reinforcement list (REQ-GAM-01)."""
    updated = copy.deepcopy(profile)
    updated["reinforce_concepts"] = update_reinforce(
        updated.get("reinforce_concepts", []), failed
    )
    return updated
