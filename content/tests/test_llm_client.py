"""LLM client: no network in unit tests; schema is inlined and passed as format."""
from __future__ import annotations

import json

import pytest
from kidquest_content.llm_client import LLMError, dereference_schema, generate_json


def test_dereference_inlines_local_refs() -> None:
    schema = {
        "type": "object",
        "properties": {"lang": {"$ref": "#/$defs/language"}},
        "$defs": {"language": {"type": "string", "enum": ["es", "en"]}},
    }
    out = dereference_schema(schema)
    assert "$defs" not in out
    assert out["properties"]["lang"] == {"type": "string", "enum": ["es", "en"]}


def test_generate_json_returns_parsed_response_and_passes_format() -> None:
    captured: dict = {}

    def transport(url: str, payload: dict) -> dict:
        captured["url"] = url
        captured["payload"] = payload
        return {"response": json.dumps({"schema_version": "1", "ok": True})}

    out = generate_json("prompt", {"type": "object"}, transport=transport, model="m")
    assert out == {"schema_version": "1", "ok": True}
    assert captured["url"].endswith("/api/generate")
    assert captured["payload"]["format"] == {"type": "object"}
    assert captured["payload"]["model"] == "m"


def test_generate_json_raises_on_non_json_response() -> None:
    def transport(url: str, payload: dict) -> dict:
        return {"response": "{not valid"}

    with pytest.raises(LLMError):
        generate_json("p", {"type": "object"}, transport=transport)


def test_generate_json_wraps_transport_failure() -> None:
    def transport(url: str, payload: dict) -> dict:
        raise TimeoutError("boom")

    with pytest.raises(LLMError):
        generate_json("p", {"type": "object"}, transport=transport)
