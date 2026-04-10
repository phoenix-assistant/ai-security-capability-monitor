"""Taxonomy utilities — tier lookups and score-to-tier mapping."""

from __future__ import annotations

from typing import Any

from .config import load_taxonomy


_taxonomy: dict[str, Any] | None = None


def get_taxonomy() -> dict[str, Any]:
    global _taxonomy
    if _taxonomy is None:
        _taxonomy = load_taxonomy()
    return _taxonomy


def get_categories() -> list[str]:
    return list(get_taxonomy()["categories"].keys())


def score_to_tier(category: str, score: float) -> str:
    """Map a 0-1 score to the appropriate tier for a category."""
    tiers = get_taxonomy()["categories"][category]["tiers"]
    matched = "L1"
    for tier_name, tier_data in sorted(tiers.items()):
        if score >= tier_data["threshold_score"]:
            matched = tier_name
    return matched


def get_tier_info(category: str, tier: str) -> dict[str, Any]:
    return get_taxonomy()["categories"][category]["tiers"][tier]


def tier_to_int(tier: str) -> int:
    return int(tier[1])
