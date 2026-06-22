"""Runtime configuration via environment variables.

Functions (not module-level constants) so importing the package has no side
effects and tests can override paths per-call.
"""
from __future__ import annotations

import os
from pathlib import Path

# Repository root (…/KidQuest), used to resolve default relative paths.
_REPO_ROOT = Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    """Directory holding live player profiles (gitignored)."""
    return Path(os.environ.get("KIDQUEST_DATA", str(_REPO_ROOT / "server" / "data")))


def content_store() -> Path:
    """Root of the pre-generated content store the server reads from."""
    return Path(os.environ.get("KIDQUEST_CONTENT_STORE", str(_REPO_ROOT / "content-store")))
