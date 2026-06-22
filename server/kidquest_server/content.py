"""Read-only access to the pre-generated content store.

Layout: ``<store>/<profile_id>/<YYYY-MM-DD>/level.json`` (+ ``audio/``). The live
server performs no inference — it only serves what the daily batch produced. When
today's content is missing (the manual batch hasn't run yet) it falls back to the
most recent available day, flagged as stale, so the game still has something to
play.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResolvedContent:
    date: str
    stale: bool
    level: dict


def _level_file(store: Path, profile_id: str, date_str: str) -> Path:
    return store / profile_id / date_str / "level.json"


def resolve_content(store: Path, profile_id: str, date_str: str) -> ResolvedContent | None:
    """Today's level, else the newest available day (stale), else None."""
    exact = _level_file(store, profile_id, date_str)
    if exact.exists():
        return ResolvedContent(date_str, False, json.loads(exact.read_text()))

    profile_dir = store / profile_id
    if not profile_dir.exists():
        return None
    available = sorted(
        d.name
        for d in profile_dir.iterdir()
        if d.is_dir() and _level_file(store, profile_id, d.name).exists()
    )
    if not available:
        return None
    latest = available[-1]  # ISO dates sort lexicographically
    return ResolvedContent(latest, True, json.loads(_level_file(store, profile_id, latest).read_text()))
