"""FastAPI application: serve player profiles and pre-generated daily content.

No inference happens here. `create_app` is a factory so tests can point it at a
temporary content store and data directory.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

from .. import SCHEMA_VERSION
from ..config import content_store as default_store
from ..config import data_dir as default_data
from ..content import resolve_content
from ..profile import load_profile


def create_app(store: Path | None = None, data: Path | None = None) -> FastAPI:
    store = store or default_store()
    data = data or default_data()
    store.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title="KidQuest", version="0.0.0")

    @app.get("/health")
    def health() -> dict:
        return {"ok": True, "schema_version": SCHEMA_VERSION}

    @app.get("/profile/{profile_id}")
    def get_profile(profile_id: str) -> dict:
        return load_profile(profile_id, data)

    @app.get("/content/today/{profile_id}")
    def get_today(profile_id: str, date_str: str | None = Query(default=None, alias="date")) -> dict:
        day = date_str or date.today().isoformat()
        resolved = resolve_content(store, profile_id, day)
        if resolved is None:
            raise HTTPException(status_code=404, detail="no content generated for this profile yet")
        return {
            "profile_id": profile_id,
            "date": resolved.date,
            "stale": resolved.stale,
            "level": resolved.level,
        }

    # Static media (pre-rendered TTS audio, sprites) lives under the content store.
    app.mount("/static", StaticFiles(directory=str(store)), name="static")
    return app
