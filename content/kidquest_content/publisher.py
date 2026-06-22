"""Publish a validated level (and its rendered audio) into the content store.

Writes ``<store>/<profile_id>/<date>/level.json`` atomically plus a small
manifest. Refuses to overwrite an existing day unless ``force`` is set, so a
re-run never silently clobbers content already in play.
"""
from __future__ import annotations

import json
from pathlib import Path


def publish(
    store: Path,
    profile_id: str,
    date_str: str,
    level: dict,
    audio_files: list[Path] | None = None,
    *,
    force: bool = False,
) -> Path:
    dest = store / profile_id / date_str
    level_file = dest / "level.json"
    if level_file.exists() and not force:
        raise FileExistsError(f"content already published for {profile_id}/{date_str} (use force)")

    dest.mkdir(parents=True, exist_ok=True)
    tmp = level_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(level, ensure_ascii=False, indent=2))
    tmp.replace(level_file)

    audio_rel = sorted(str(p.relative_to(dest)) for p in (audio_files or []))
    manifest = {
        "profile_id": profile_id,
        "date": date_str,
        "schema_version": level.get("schema_version"),
        "audio": audio_rel,
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    return dest
