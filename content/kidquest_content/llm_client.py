"""Thin Ollama client for structured (JSON-schema-constrained) generation.

The HTTP transport is injectable so unit tests never hit the network. The daily
batch uses the real transport against the local Ollama on the GPU box.
"""
from __future__ import annotations

import json
import os
from typing import Callable, Protocol

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3-coder:30b"


class LLMError(RuntimeError):
    pass


class Transport(Protocol):
    def __call__(self, url: str, payload: dict) -> dict: ...


def _requests_transport(url: str, payload: dict) -> dict:
    import requests  # imported lazily so unit tests need no network stack

    resp = requests.post(url, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()


def dereference_schema(schema: dict) -> dict:
    """Inline local ``$defs``/``#/...`` refs so the schema is self-contained.

    Ollama's structured-output grammar builder is happiest with a fully inlined
    schema. Handles the internal references this project uses ($defs only).
    """
    defs = schema.get("$defs", {})

    def resolve(node: object) -> object:
        if isinstance(node, dict):
            if "$ref" in node and isinstance(node["$ref"], str):
                ref = node["$ref"]
                if ref.startswith("#/$defs/"):
                    target = defs[ref.split("/")[-1]]
                    return resolve(json.loads(json.dumps(target)))
            return {k: resolve(v) for k, v in node.items() if k != "$defs"}
        if isinstance(node, list):
            return [resolve(v) for v in node]
        return node

    return resolve(schema)  # type: ignore[return-value]


def ollama_url() -> str:
    return os.environ.get("KIDQUEST_OLLAMA_URL", DEFAULT_OLLAMA_URL)


def generate_json(
    prompt: str,
    schema: dict,
    *,
    model: str = DEFAULT_MODEL,
    url: str | None = None,
    transport: Transport | None = None,
    options: dict | None = None,
) -> dict:
    """Generate a JSON object constrained to ``schema`` and return it parsed.

    Raises LLMError if the transport fails or the response is not valid JSON.
    """
    send: Callable[[str, dict], dict] = transport or _requests_transport
    endpoint = (url or ollama_url()).rstrip("/") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "format": dereference_schema(schema),
        "stream": False,
        "options": options or {"temperature": 0.4},
    }
    try:
        body = send(endpoint, payload)
    except Exception as exc:  # noqa: BLE001 - surface any transport failure uniformly
        raise LLMError(f"LLM transport failed: {exc}") from exc

    raw = body.get("response", "")
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise LLMError(f"LLM did not return valid JSON: {exc}") from exc
