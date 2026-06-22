"""Render dialogue lines to audio with Piper TTS.

The actual Piper invocation is isolated behind ``PiperRunner`` so unit tests mock
it (no Piper binary, no audio). Re-rendering is idempotent: an existing wav for a
given (dialogue, line index) is left untouched.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class TTSError(RuntimeError):
    pass


class Runner(Protocol):
    def synthesize(self, text: str, voice: str, out_path: Path) -> None: ...


@dataclass
class PiperRunner:
    """Default runner shelling out to the `piper` binary."""

    binary: str = "piper"
    voices_dir: Path | None = None

    def synthesize(self, text: str, voice: str, out_path: Path) -> None:
        model = f"{voice}.onnx"
        if self.voices_dir is not None:
            model = str(self.voices_dir / model)
        try:
            subprocess.run(
                [self.binary, "--model", model, "--output_file", str(out_path)],
                input=text.encode("utf-8"),
                check=True,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:  # pragma: no cover - real IO
            raise TTSError(f"piper failed for voice {voice!r}: {exc}") from exc


@dataclass(frozen=True)
class RenderedLine:
    dialogue_id: str
    index: int
    path: Path


def render_dialogues(
    dialogues: list[dict],
    out_dir: Path,
    runner: Runner,
) -> list[RenderedLine]:
    """Render every dialogue line to ``out_dir/<dialogue_id>_<index>.wav``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[RenderedLine] = []
    for dialogue in dialogues:
        for index, line in enumerate(dialogue.get("lines", [])):
            voice = line.get("voice")
            if not voice:
                raise TTSError(f"dialogue {dialogue.get('id')} line {index} has no voice")
            path = out_dir / f"{dialogue['id']}_{index}.wav"
            if not path.exists():
                runner.synthesize(line["text"], voice, path)
            rendered.append(RenderedLine(dialogue["id"], index, path))
    return rendered
