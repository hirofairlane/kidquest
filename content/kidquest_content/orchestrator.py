"""Daily content generation orchestrator (run on the GPU box, on demand).

Pipeline: build prompt → generate (LLM, schema-constrained) → validate, retrying
with the validation errors fed back in → check text safety → render TTS audio →
publish. It NEVER publishes a level that fails validation: after the retry budget
is spent it raises, leaving the content store untouched.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from .llm_client import DEFAULT_MODEL, generate_json
from .prompt_builder import build_prompt
from .publisher import publish
from .safety import assert_level_text_safe
from .schema_validator import LevelInvalidError, load_schema, validate_level
from .tts_piper import PiperRunner, Runner, render_dialogues

Generate = Callable[[str, dict], dict]


class GenerationError(RuntimeError):
    pass


def generate_daily(
    profile: dict,
    curriculum: dict,
    store: Path,
    date_str: str,
    *,
    generate: Generate | None = None,
    runner: Runner | None = None,
    model: str = DEFAULT_MODEL,
    max_attempts: int = 3,
    force: bool = False,
) -> Path:
    schema = load_schema()
    runner = runner or PiperRunner()
    if generate is None:
        def generate(prompt: str, schema: dict) -> dict:  # noqa: ANN001 - local default
            return generate_json(prompt, schema, model=model)

    base_prompt = build_prompt(profile, curriculum)
    prompt = base_prompt
    last_error: LevelInvalidError | None = None

    level: dict | None = None
    for _ in range(max_attempts):
        candidate = generate(prompt, schema)
        try:
            validate_level(candidate, schema)
        except LevelInvalidError as exc:
            last_error = exc
            prompt = (
                f"{base_prompt}\n\nYour previous answer was INVALID:\n"
                f"{'; '.join(exc.errors)}\nReturn a corrected JSON object."
            )
            continue
        level = candidate
        break

    if level is None:
        raise GenerationError(
            f"could not generate a valid level after {max_attempts} attempts: {last_error}"
        )

    assert_level_text_safe(level)

    audio_dir = store / profile["profile_id"] / date_str / "audio"
    rendered = render_dialogues(level.get("dialogues", []), audio_dir, runner)
    audio_files = [r.path for r in rendered]

    return publish(store, profile["profile_id"], date_str, level, audio_files, force=force)
