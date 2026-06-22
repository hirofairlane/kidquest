"""Load the data-driven curricula (YAML). Adding a learner profile is adding one
of these files — no code change."""
from __future__ import annotations

from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]


def curricula_dir(base: Path | None = None) -> Path:
    return (base or _REPO_ROOT) / "curricula" / "profiles"


def load_curriculum(curriculum_ref: str, base: Path | None = None) -> dict:
    path = curricula_dir(base) / f"{curriculum_ref}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"no curriculum for {curriculum_ref!r} at {path}")
    return yaml.safe_load(path.read_text())
