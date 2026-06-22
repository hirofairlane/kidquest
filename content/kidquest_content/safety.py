"""Content-safety guardrails for image generation.

KidQuest is for children. Image generation is restricted to an explicit ALLOWLIST
of family-safe pixel-art LoRAs; anything not on the list is rejected. This is a
deny-by-default policy on purpose: a newly added LoRA must be vetted before it can
ever be used, rather than relying on a blocklist that a new asset could slip past.
"""
from __future__ import annotations

from pathlib import PurePath

# Family-safe pixel-art LoRAs vetted for KidQuest content. Matched by filename stem
# (no directory, no extension) so the same entry covers .safetensors / .pt variants.
ALLOWED_LORA_STEMS: frozenset[str] = frozenset(
    {
        "pixel_art_a3",
        "pixelart-1",
        "PX64NOCAP_epoch_10",
        "pxx4_v1_alpha",
        "z-image-pixel-hard_000002400",
        "ElinSpriteNoobLocon_byKonan",
    }
)


class BannedAssetError(ValueError):
    """Raised when a LoRA outside the safe allowlist is requested."""


def _stem(lora: str) -> str:
    """Filename stem of a LoRA reference (strip directory and extension)."""
    return PurePath(lora).name.rsplit(".", 1)[0]


def is_allowed_lora(lora: str) -> bool:
    """True only if the LoRA's filename stem is on the vetted allowlist."""
    return _stem(lora) in ALLOWED_LORA_STEMS


def assert_lora_allowed(lora: str) -> None:
    """Raise BannedAssetError unless the LoRA is explicitly allowlisted."""
    if not is_allowed_lora(lora):
        raise BannedAssetError(
            f"LoRA {lora!r} is not on the family-safe allowlist and must not be used"
        )
