"""Build the daily-level generation prompt from a player profile + curriculum.

Pure and deterministic (same inputs → same string) so it can be unit-tested
without any model. Concepts the player failed are listed FIRST so the model
prioritizes reinforcing them (REQ-GAM-01). Per-subject language is honoured (e.g.
the 6-year-old's science is taught in English).
"""
from __future__ import annotations


def build_prompt(profile: dict, curriculum: dict) -> str:
    lines: list[str] = []
    lines.append("You are the content generator for KidQuest, an educational RPG for children.")
    lines.append(
        f"Design today's level for profile '{profile['profile_id']}' "
        f"(age {profile.get('age', '?')}, difficulty {profile.get('difficulty_modifier', 1.0)})."
    )
    lines.append("Return ONLY a JSON object matching the provided schema. No prose.")

    reinforce = profile.get("reinforce_concepts", [])
    if reinforce:
        lines.append("")
        lines.append("PRIORITY — reinforce these previously failed concepts first:")
        for c in reinforce:
            lines.append(f"  - {c['concept_id']} ({c['subject']}), failed {c['failures']}x")

    lines.append("")
    lines.append("Curriculum to cover:")
    for subject in curriculum.get("subjects", []):
        concept_ids = ", ".join(c["concept_id"] for c in subject.get("concepts", []))
        lines.append(
            f"  - {subject['subject']} [present in {subject['language']}]: {concept_ids}"
        )

    lines.append("")
    lines.append(
        "Puzzles must tag the concepts they test via concept_tags. Keep language and "
        "difficulty age-appropriate. All content must be safe for children."
    )
    return "\n".join(lines)
