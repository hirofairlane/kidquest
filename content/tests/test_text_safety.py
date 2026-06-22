"""Defence-in-depth text safety on generated levels."""
from __future__ import annotations

import pytest
from kidquest_content.safety import UnsafeTextError, assert_level_text_safe, find_unsafe_terms


def test_clean_level_passes(valid_level) -> None:
    assert_level_text_safe(valid_level)


def test_banned_term_in_dialogue_is_rejected(valid_level) -> None:
    valid_level["dialogues"][0]["lines"][0]["text"] = "this is NSFW content"
    with pytest.raises(UnsafeTextError):
        assert_level_text_safe(valid_level)


def test_find_unsafe_terms_is_case_insensitive() -> None:
    assert "gore" in find_unsafe_terms("lots of GORE here")
    assert find_unsafe_terms("a friendly meadow") == []
