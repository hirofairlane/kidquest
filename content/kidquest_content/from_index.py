"""Build a ChallengeSet from a curated content index (author-verified Q&A).

This bypasses the LLM's factual hallucination entirely: the questions and the
correct answers come from a human-curated YAML, so the content is correct by
construction. The LLM is not needed (it may later be used only to reword
questions for flavour, keeping the verified answers).
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .challenges import validate_challenge_set


def load_index(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text())


def index_to_challenge_set(index: dict, era: str = "greek_colonies") -> dict:
    """Flatten a content index into a (schema-valid) ChallengeSet."""
    sphinxes: list[dict] = []
    for subject in index.get("subjects", []):
        language = subject["language"]
        for item in subject.get("items", []):
            sphinxes.append(
                {
                    "subject": subject["subject"],
                    "concept_tags": [item.get("concept", subject["subject"])],
                    "riddle": {"text": item["question"], "language": language},
                    "answers": list(item["answers"]),
                    "reward": {"gold": int(item.get("gold", 500))},
                }
            )
    cs = {
        "schema_version": "1",
        "profile_id": index["profile_id"],
        "era": era,
        "language_default": "es",
        "sphinxes": sphinxes,
    }
    validate_challenge_set(cs)
    return cs
