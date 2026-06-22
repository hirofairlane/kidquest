"""API tests: content serving (today / stale fallback / missing) and static media."""
from __future__ import annotations

import json

from fastapi.testclient import TestClient
from kidquest_server.api import create_app


def _write_level(store, profile_id: str, date_str: str, level: dict) -> None:
    d = store / profile_id / date_str
    d.mkdir(parents=True, exist_ok=True)
    (d / "level.json").write_text(json.dumps(level))


def client(tmp_path):
    store = tmp_path / "content-store"
    data = tmp_path / "data"
    return TestClient(create_app(store=store, data=data)), store


def test_health(tmp_path) -> None:
    c, _ = client(tmp_path)
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_profile_endpoint_returns_default_for_unknown(tmp_path) -> None:
    c, _ = client(tmp_path)
    r = c.get("/profile/youth_10yo")
    assert r.status_code == 200
    assert r.json()["profile_id"] == "youth_10yo"


def test_today_content_served_when_present(tmp_path) -> None:
    c, store = client(tmp_path)
    _write_level(store, "child_6yo", "2026-06-22", {"schema_version": "1", "n": 1})
    r = c.get("/content/today/child_6yo", params={"date": "2026-06-22"})
    assert r.status_code == 200
    body = r.json()
    assert body["stale"] is False
    assert body["date"] == "2026-06-22"
    assert body["level"]["n"] == 1


def test_missing_content_returns_404(tmp_path) -> None:
    c, _ = client(tmp_path)
    r = c.get("/content/today/child_6yo", params={"date": "2026-06-22"})
    assert r.status_code == 404


def test_falls_back_to_latest_available_day_as_stale(tmp_path) -> None:
    c, store = client(tmp_path)
    _write_level(store, "child_6yo", "2026-06-20", {"schema_version": "1", "n": 7})
    r = c.get("/content/today/child_6yo", params={"date": "2026-06-22"})
    assert r.status_code == 200
    body = r.json()
    assert body["stale"] is True
    assert body["date"] == "2026-06-20"
    assert body["level"]["n"] == 7


def test_static_audio_is_served(tmp_path) -> None:
    c, store = client(tmp_path)
    audio_dir = store / "child_6yo" / "2026-06-22" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    (audio_dir / "hello.wav").write_bytes(b"RIFFfake")
    r = c.get("/static/child_6yo/2026-06-22/audio/hello.wav")
    assert r.status_code == 200
    assert r.content == b"RIFFfake"
