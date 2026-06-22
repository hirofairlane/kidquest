"""Author the educational ChallengeSet for one day's map and learner.

The AI produces curriculum-tagged Sphinx riddles (plus signs/events) themed on a
historical era of the Iberian peninsula. Pure prompt building + a mockable
generate step; auto-repair fixes the structural slips local models make so the
output always validates. Reuses the same Ollama structured-output path as the
rest of the pipeline.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Callable

from jsonschema import Draft202012Validator

from .safety import find_unsafe_terms

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = _REPO_ROOT / "shared" / "schemas" / "challenge_set.schema.json"

# Historical-era themes for the Spanish-geography campaign arc.
ERA_THEMES: dict[str, str] = {
    "greek_colonies": "Ancient Greek colonies of Iberia (Emporion/Ampurias, ~575 BC): "
    "Mediterranean coast, traders, amphorae, the founding of trading posts.",
    "phoenician_carthaginian": "Phoenician & Carthaginian Iberia (Gadir/Cadiz, Carthago Nova): "
    "seafaring, Hannibal, the Punic presence.",
    "roman_hispania": "Roman Hispania: roads, aqueducts, legions, provinces, Latin.",
    "visigothic": "Visigothic kingdom of Toledo after Rome.",
    "al_andalus": "Al-Andalus: Cordoba, the Caliphate, science and irrigation.",
    "christian_kingdoms": "Christian kingdoms and the Reconquista.",
}


class ChallengeSetInvalidError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class UnsafeChallengeError(ValueError):
    pass


def load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text())


def build_challenge_prompt(profile: dict, curriculum: dict, era: str, num_sphinxes: int) -> str:
    lines: list[str] = []
    lines.append("You write educational riddles for KidQuest, a Heroes of Might & Magic map for children.")
    lines.append(
        f"Learner profile '{profile['profile_id']}' (age {profile.get('age', '?')}, "
        f"difficulty {profile.get('difficulty_modifier', 1.0)})."
    )
    lines.append(f"Map era/theme: {ERA_THEMES.get(era, era)}")
    lines.append(f"Return ONLY a JSON object matching the schema, with exactly {num_sphinxes} sphinxes. No prose.")

    reinforce = profile.get("reinforce_concepts", [])
    if reinforce:
        lines.append("")
        lines.append("PRIORITY — reinforce these previously failed concepts first:")
        for c in reinforce:
            lines.append(f"  - {c['concept_id']} ({c['subject']})")

    lines.append("")
    lines.append("Curriculum to draw from:")
    for subject in curriculum.get("subjects", []):
        concept_ids = ", ".join(c["concept_id"] for c in subject.get("concepts", []))
        lines.append(f"  - {subject['subject']} [in {subject['language']}]: {concept_ids}")

    lines.append("")
    lines.append(
        "Each Sphinx riddle: present it in its subject's language; tag concept_tags; give a modest "
        "resource reward (mostly gold). CRITICAL: fheroes2 matches answers EXACTLY against the list, "
        "so enumerate tolerant variants (lowercase, Capitalized, UPPERCASE, accented/unaccented, and "
        "es/en synonyms). Keep everything age-appropriate and safe for children."
    )
    return "\n".join(lines)


def _safe_int(value: object, default: int = 0) -> int:
    return value if isinstance(value, int) and value >= 0 else default


def repair_challenge_set(cs: dict, profile_id: str, era: str, num_sphinxes: int) -> dict:
    """Fix the common structural slips so the result validates and is usable."""
    cs = copy.deepcopy(cs)
    cs["schema_version"] = "1"
    cs["profile_id"] = profile_id
    cs["era"] = era if era in ERA_THEMES else "greek_colonies"
    cs.setdefault("language_default", "es")

    sphinxes = cs.get("sphinxes")
    if not isinstance(sphinxes, list):
        sphinxes = []
    for s in sphinxes:
        s.setdefault("subject", "history")
        if not s.get("concept_tags"):
            s["concept_tags"] = ["general"]
        if not isinstance(s.get("riddle"), dict):
            s["riddle"] = {"text": "Riddle", "language": cs["language_default"]}
        s["riddle"].setdefault("language", cs["language_default"])
        answers = [a for a in s.get("answers", []) if isinstance(a, str) and a]
        s["answers"] = answers or ["?"]
        reward = s.get("reward") if isinstance(s.get("reward"), dict) else {}
        s["reward"] = {k: _safe_int(v) for k, v in reward.items() if k in _REWARD_KEYS}
        s["reward"].setdefault("gold", 1000)
    # keep at most num_sphinxes; pad is not possible (no content), so just trim
    cs["sphinxes"] = sphinxes[:num_sphinxes] if sphinxes else sphinxes
    return cs


_REWARD_KEYS = {"gold", "wood", "ore", "mercury", "sulfur", "crystal", "gems"}


def validate_challenge_set(cs: dict, schema: dict | None = None) -> None:
    schema = schema or load_schema()
    errors = [
        f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
        for e in sorted(Draft202012Validator(schema).iter_errors(cs), key=lambda e: list(e.path))
    ]
    if errors:
        raise ChallengeSetInvalidError(errors)


def assert_challenge_text_safe(cs: dict) -> None:
    fragments: list[str] = []
    for s in cs.get("sphinxes", []):
        fragments.append(s.get("riddle", {}).get("text", ""))
        fragments.extend(s.get("answers", []))
        if s.get("hint"):
            fragments.append(s["hint"].get("text", ""))
    for sign in cs.get("signs", []):
        fragments.append(sign.get("text", ""))
    for ev in cs.get("events", []):
        fragments.append(ev.get("message", {}).get("text", ""))
    hits = sorted({t for frag in fragments for t in find_unsafe_terms(frag)})
    if hits:
        raise UnsafeChallengeError(f"challenge set contains banned terms: {', '.join(hits)}")


Generate = Callable[[str, dict], dict]


def generate_challenge_set(
    profile: dict,
    curriculum: dict,
    era: str,
    *,
    generate: Generate,
    num_sphinxes: int = 4,
    max_attempts: int = 3,
) -> dict:
    """Build the prompt, generate, repair→validate (retrying), and safety-check."""
    schema = load_schema()
    prompt = build_challenge_prompt(profile, curriculum, era, num_sphinxes)
    last: ChallengeSetInvalidError | None = None
    for _ in range(max_attempts):
        candidate = repair_challenge_set(generate(prompt, schema), profile["profile_id"], era, num_sphinxes)
        try:
            validate_challenge_set(candidate, schema)
        except ChallengeSetInvalidError as exc:
            last = exc
            prompt = f"{prompt}\n\nPrevious answer was invalid: {'; '.join(exc.errors)}\nReturn corrected JSON."
            continue
        assert_challenge_text_safe(candidate)
        return candidate
    raise ChallengeSetInvalidError([f"no valid challenge set after {max_attempts} attempts: {last}"])
