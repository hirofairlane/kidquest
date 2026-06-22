"""Shared fixtures for content-pipeline tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_MINIMAL_LEVEL = json.loads(
    (REPO_ROOT / "shared" / "fixtures" / "levels" / "minimal.json").read_text()
)


@pytest.fixture
def valid_level() -> dict:
    return copy.deepcopy(_MINIMAL_LEVEL)
