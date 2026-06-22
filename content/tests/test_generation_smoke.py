"""Live generation smoke test against the local Ollama on the GPU box.

Marked ``smoke`` so it is EXCLUDED from cloud CI (`pytest -m "not smoke"`). Run it
manually on blackwell with Ollama up:

    KIDQUEST_SMOKE_MODEL=gemma4:e4b uv run pytest -m smoke content/tests

It asks the model for a daily level constrained to the schema and asserts the
response is structurally valid JSON for the contract (grammar-enforced by Ollama).
"""
from __future__ import annotations

import os

import pytest
from jsonschema import Draft202012Validator
from kidquest_content.curricula import load_curriculum
from kidquest_content.llm_client import generate_json, ollama_url
from kidquest_content.prompt_builder import build_prompt
from kidquest_content.schema_validator import load_schema

pytestmark = pytest.mark.smoke


def _ollama_reachable() -> bool:
    import requests

    try:
        requests.get(ollama_url(), timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False


@pytest.mark.skipif(not _ollama_reachable(), reason="local Ollama not reachable")
def test_live_generation_is_structurally_valid() -> None:
    model = os.environ.get("KIDQUEST_SMOKE_MODEL", "gemma4:e4b")
    profile = {
        "profile_id": "youth_10yo",
        "age": 10,
        "difficulty_modifier": 1.0,
        "reinforce_concepts": [],
    }
    schema = load_schema()
    prompt = build_prompt(profile, load_curriculum("youth_10yo"))

    level = generate_json(prompt, schema, model=model)

    # Structural validation only (small models may miss cross-field invariants).
    structural_errors = list(Draft202012Validator(schema).iter_errors(level))
    assert not structural_errors, structural_errors[:3]
    assert level["schema_version"] == "1"
