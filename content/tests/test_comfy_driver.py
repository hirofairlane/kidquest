"""ComfyUI driver: mocked transport (no real ComfyUI), allowlist enforcement."""
from __future__ import annotations

import pytest
from kidquest_content.comfy_driver import AssetSpec, ComfyClient, ComfyError, fill_workflow
from kidquest_content.safety import BannedAssetError

TEMPLATE = {
    "3": {"class_type": "KSampler", "inputs": {"seed": "{{SEED}}"}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "pixel art, {{PROMPT}}"}},
    "10": {"class_type": "LoraLoader", "inputs": {"lora_name": "{{LORA}}"}},
}


class FakeTransport:
    def __init__(self) -> None:
        self.posted: dict | None = None

    def post_json(self, url: str, payload: dict) -> dict:
        self.posted = payload
        return {"prompt_id": "pid-1"}

    def get_json(self, url: str) -> dict:
        return {"pid-1": {"outputs": {"9": {"images": [{"filename": "sprite_0001.png", "subfolder": "", "type": "output"}]}}}}

    def get_bytes(self, url: str) -> bytes:
        return b"\x89PNG-data"


def test_fill_workflow_substitutes_placeholders() -> None:
    spec = AssetSpec(id="hero", prompt="a brave knight", lora="pixel_art_a3.safetensors", seed=42)
    wf = fill_workflow(TEMPLATE, spec)
    assert wf["3"]["inputs"]["seed"] == 42
    assert wf["6"]["inputs"]["text"] == "pixel art, a brave knight"
    assert wf["10"]["inputs"]["lora_name"] == "pixel_art_a3.safetensors"


def test_fill_workflow_rejects_banned_lora() -> None:
    spec = AssetSpec(id="x", prompt="p", lora="cris_v1.safetensors")
    with pytest.raises(BannedAssetError):
        fill_workflow(TEMPLATE, spec)


def test_generate_asset_end_to_end_mocked(tmp_path) -> None:
    client = ComfyClient(base_url="http://comfy.test", transport=FakeTransport())
    spec = AssetSpec(id="hero", prompt="a knight", lora="pixel_art_a3.safetensors", seed=1)
    out = client.generate_asset(spec, TEMPLATE, tmp_path, sleep=lambda _: None)
    assert out.name == "hero.png"
    assert out.read_bytes().startswith(b"\x89PNG")


def test_submit_without_prompt_id_raises() -> None:
    class BadTransport(FakeTransport):
        def post_json(self, url: str, payload: dict) -> dict:
            return {}

    client = ComfyClient(base_url="http://comfy.test", transport=BadTransport())
    with pytest.raises(ComfyError):
        client.submit({})
