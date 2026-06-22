"""Safety guardrail tests — the banned NSFW LoRA must always be rejected."""
from __future__ import annotations

import pytest
from kidquest_content.safety import (
    BannedAssetError,
    assert_lora_allowed,
    is_allowed_lora,
)


def test_allowlisted_pixel_art_lora_passes() -> None:
    assert is_allowed_lora("pixel_art_a3.safetensors")
    assert is_allowed_lora("/home/sergio/AI/ComfyUI/models/loras/pxx4_v1_alpha.safetensors")
    assert_lora_allowed("pixelart-1.pt")  # must not raise


@pytest.mark.parametrize("banned", ["cris_v1.safetensors", "cris_v1_old.safetensors"])
def test_nsfw_cristina_lora_is_banned(banned: str) -> None:
    assert not is_allowed_lora(banned)
    with pytest.raises(BannedAssetError):
        assert_lora_allowed(banned)


def test_unknown_lora_is_denied_by_default() -> None:
    with pytest.raises(BannedAssetError):
        assert_lora_allowed("some_new_unvetted_lora.safetensors")
