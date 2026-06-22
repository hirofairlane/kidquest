"""Publishing to the content store: atomic, manifest, no silent overwrite."""
from __future__ import annotations

import json

import pytest
from kidquest_content.publisher import publish


def test_publish_writes_level_and_manifest(tmp_path, valid_level) -> None:
    dest = publish(tmp_path, "youth_10yo", "2026-06-22", valid_level)
    assert (dest / "level.json").exists()
    manifest = json.loads((dest / "manifest.json").read_text())
    assert manifest["profile_id"] == "youth_10yo"
    assert manifest["schema_version"] == "1"


def test_publish_refuses_overwrite_without_force(tmp_path, valid_level) -> None:
    publish(tmp_path, "youth_10yo", "2026-06-22", valid_level)
    with pytest.raises(FileExistsError):
        publish(tmp_path, "youth_10yo", "2026-06-22", valid_level)


def test_publish_overwrites_with_force(tmp_path, valid_level) -> None:
    publish(tmp_path, "youth_10yo", "2026-06-22", valid_level)
    valid_level["profile_id"] = "youth_10yo"
    dest = publish(tmp_path, "youth_10yo", "2026-06-22", valid_level, force=True)
    assert (dest / "level.json").exists()


def test_manifest_lists_audio_relative_paths(tmp_path, valid_level) -> None:
    audio_dir = tmp_path / "youth_10yo" / "2026-06-22" / "audio"
    audio_dir.mkdir(parents=True)
    a = audio_dir / "d1_0.wav"
    a.write_bytes(b"WAV")
    dest = publish(tmp_path, "youth_10yo", "2026-06-22", valid_level, [a])
    manifest = json.loads((dest / "manifest.json").read_text())
    assert manifest["audio"] == ["audio/d1_0.wav"]
