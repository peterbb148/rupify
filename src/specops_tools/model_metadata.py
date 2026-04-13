"""Helpers for metadata-aware SpecOps model fields."""

from __future__ import annotations

from typing import Any


def normalize_uncertainty_item(item: Any) -> dict[str, str]:
    """Normalize one assumption or open-question item.

    Args:
        item: Raw item from the model.

    Returns:
        Normalized item with stable keys.

    Raises:
        TypeError: If the item shape is unsupported.
        ValueError: If a mapping item is missing required text.
    """
    if isinstance(item, str):
        return {
            "text": item,
            "status": "",
            "source": "",
            "last_updated": "",
            "notes": "",
        }

    if not isinstance(item, dict):
        raise TypeError("Uncertainty items must be strings or mappings.")

    text = str(item.get("text", "")).strip()
    if not text:
        raise ValueError("Structured uncertainty items must include non-empty `text`.")

    return {
        "text": text,
        "status": str(item.get("status", "")).strip(),
        "source": str(item.get("source", "")).strip(),
        "last_updated": str(item.get("last_updated", "")).strip(),
        "notes": str(item.get("notes", "")).strip(),
    }


def normalize_uncertainty_list(items: list[Any]) -> list[dict[str, str]]:
    """Normalize a list of assumptions or open questions.

    Args:
        items: Raw list from the model.

    Returns:
        Normalized items.
    """
    return [normalize_uncertainty_item(item) for item in items]
