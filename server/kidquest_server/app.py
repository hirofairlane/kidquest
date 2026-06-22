"""ASGI entry point: ``uvicorn kidquest_server.app:app``.

Uses environment-configured paths (KIDQUEST_CONTENT_STORE, KIDQUEST_DATA).
"""
from __future__ import annotations

from .api import create_app

app = create_app()
