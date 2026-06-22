"""Tracker 'medal' artifacts.

Each solved Sphinx grants a unique HoMM2 artifact, so the hero's artifact bag
becomes a record of mastered concepts (read back later from the save file). We
use low-impact, positive artifacts (morale medals, luck charms, gold purses) by
their fheroes2 artifact-enum id, so a medal is a benign reward AND a marker.
"""
from __future__ import annotations

# (fheroes2 artifact id, human label). Distinct, benign, thematically "medal/luck".
MEDAL_POOL: list[tuple[int, str]] = [
    (13, "Medalla del Valor"),
    (14, "Medalla del Coraje"),
    (15, "Medalla del Honor"),
    (16, "Medalla de la Distinción"),
    (36, "Pata de Conejo"),
    (37, "Herradura Dorada"),
    (38, "Moneda de la Suerte"),
    (39, "Trébol de Cuatro Hojas"),
    (31, "Saco Inagotable de Oro"),
    (32, "Bolsa Inagotable de Oro"),
    (33, "Monedero Inagotable de Oro"),
]


class MedalError(ValueError):
    pass


def assign_medals(count: int) -> list[tuple[int, str]]:
    """Return `count` distinct (artifact_id, label) medals."""
    if count > len(MEDAL_POOL):
        raise MedalError(f"need {count} medals but only {len(MEDAL_POOL)} in the pool")
    return MEDAL_POOL[:count]
