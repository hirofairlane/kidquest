"""Piper TTS rendering with a mocked runner (no Piper binary, no audio)."""
from __future__ import annotations

from pathlib import Path

import pytest
from kidquest_content.tts_piper import TTSError, render_dialogues


class FakeRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Path]] = []

    def synthesize(self, text: str, voice: str, out_path: Path) -> None:
        self.calls.append((text, voice, out_path))
        out_path.write_bytes(b"WAV")


DIALOGUES = [
    {"id": "d1", "speaker": "Xana", "lines": [
        {"text": "Hello", "language": "en", "voice": "en_GB"},
        {"text": "Hola", "language": "es", "voice": "es_ES"},
    ]},
]


def test_renders_one_file_per_line(tmp_path) -> None:
    runner = FakeRunner()
    rendered = render_dialogues(DIALOGUES, tmp_path, runner)
    assert len(rendered) == 2
    assert all(r.path.exists() for r in rendered)
    assert len(runner.calls) == 2


def test_missing_voice_raises(tmp_path) -> None:
    runner = FakeRunner()
    with pytest.raises(TTSError):
        render_dialogues([{"id": "d", "lines": [{"text": "hi", "language": "en", "voice": ""}]}], tmp_path, runner)


def test_rerender_is_idempotent(tmp_path) -> None:
    runner = FakeRunner()
    render_dialogues(DIALOGUES, tmp_path, runner)
    render_dialogues(DIALOGUES, tmp_path, runner)  # second pass
    # files already existed → no extra synthesize calls on the second pass
    assert len(runner.calls) == 2
