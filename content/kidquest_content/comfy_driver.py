"""Drive ComfyUI to batch-generate sprites/tiles (optional, non-blocking for play).

Follows the queue → poll → download pattern: POST a workflow to ``/prompt``, poll
``/history/<id>`` until it completes, then fetch images from ``/view``. The HTTP
transport is injectable so unit tests never touch a real ComfyUI.

Child-safety: any LoRA referenced by an AssetSpec must pass the allowlist
(`safety.assert_lora_allowed`) BEFORE a workflow is ever submitted.
"""
from __future__ import annotations

import copy
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from .safety import assert_lora_allowed

DEFAULT_COMFY_URL = "http://localhost:8188"


class ComfyError(RuntimeError):
    pass


@dataclass(frozen=True)
class AssetSpec:
    id: str
    prompt: str
    lora: str | None = None
    seed: int = 0


class Transport(Protocol):
    def post_json(self, url: str, payload: dict) -> dict: ...
    def get_json(self, url: str) -> dict: ...
    def get_bytes(self, url: str) -> bytes: ...


def comfy_url() -> str:
    return os.environ.get("KIDQUEST_COMFY_URL", DEFAULT_COMFY_URL)


def fill_workflow(template: dict, spec: AssetSpec) -> dict:
    """Substitute {{PROMPT}}/{{SEED}}/{{LORA}} placeholders in a workflow template.

    Enforces the LoRA allowlist before producing the workflow.
    """
    if spec.lora is not None:
        assert_lora_allowed(spec.lora)

    def fill(node: object) -> object:
        if isinstance(node, dict):
            return {k: fill(v) for k, v in node.items()}
        if isinstance(node, list):
            return [fill(v) for v in node]
        if node == "{{SEED}}":
            return spec.seed
        if isinstance(node, str):
            out = node.replace("{{PROMPT}}", spec.prompt)
            if spec.lora is not None:
                out = out.replace("{{LORA}}", spec.lora)
            return out
        return node

    return fill(copy.deepcopy(template))  # type: ignore[return-value]


class ComfyClient:
    def __init__(self, base_url: str | None = None, transport: Transport | None = None) -> None:
        self.base_url = (base_url or comfy_url()).rstrip("/")
        self.transport = transport or _RequestsTransport()

    def submit(self, workflow: dict) -> str:
        body = self.transport.post_json(f"{self.base_url}/prompt", {"prompt": workflow})
        prompt_id = body.get("prompt_id")
        if not prompt_id:
            raise ComfyError(f"ComfyUI did not return a prompt_id: {body}")
        return prompt_id

    def poll(
        self,
        prompt_id: str,
        *,
        timeout: float = 300.0,
        interval: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
        attempts: int = 600,
    ) -> dict:
        for _ in range(attempts):
            data = self.transport.get_json(f"{self.base_url}/history/{prompt_id}")
            if prompt_id in data:
                return data[prompt_id]
            sleep(interval)
        raise ComfyError(f"timed out waiting for prompt {prompt_id} after {timeout}s")

    def images_in(self, history_entry: dict) -> list[dict]:
        images: list[dict] = []
        for node_out in history_entry.get("outputs", {}).values():
            images.extend(node_out.get("images", []))
        return images

    def download(self, image: dict) -> bytes:
        qs = f"filename={image['filename']}&subfolder={image.get('subfolder', '')}&type={image.get('type', 'output')}"
        return self.transport.get_bytes(f"{self.base_url}/view?{qs}")

    def generate_asset(
        self,
        spec: AssetSpec,
        workflow_template: dict,
        out_dir: Path,
        *,
        sleep: Callable[[float], None] = time.sleep,
    ) -> Path:
        workflow = fill_workflow(workflow_template, spec)
        prompt_id = self.submit(workflow)
        history = self.poll(prompt_id, sleep=sleep)
        images = self.images_in(history)
        if not images:
            raise ComfyError(f"no images produced for asset {spec.id}")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{spec.id}.png"
        out_path.write_bytes(self.download(images[0]))
        return out_path


class _RequestsTransport:
    def post_json(self, url: str, payload: dict) -> dict:  # pragma: no cover - real IO
        import requests

        resp = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_json(self, url: str) -> dict:  # pragma: no cover - real IO
        import requests

        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_bytes(self, url: str) -> bytes:  # pragma: no cover - real IO
        import requests

        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        return resp.content
