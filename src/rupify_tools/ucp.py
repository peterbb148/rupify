"""Deterministic Use Case Point calculation for Rupify."""

from __future__ import annotations

from typing import Any

from .model_metadata import normalize_uncertainty_list

ACTOR_WEIGHTS = {
    "simple": 1,
    "average": 2,
    "complex": 3,
}

USE_CASE_WEIGHTS = {
    "simple": 5,
    "average": 10,
    "complex": 15,
}

TECHNICAL_FACTOR_WEIGHTS = {
    "distributed_system": 2.0,
    "response_time": 1.0,
    "end_user_efficiency": 1.0,
    "complex_internal_processing": 1.0,
    "reusable_code": 1.0,
    "easy_to_install": 0.5,
    "easy_to_use": 0.5,
    "portability": 2.0,
    "easy_to_change": 1.0,
    "concurrency": 1.0,
    "special_security": 1.0,
    "third_party_access": 1.0,
    "special_user_training": 1.0,
}

ENVIRONMENTAL_FACTOR_WEIGHTS = {
    "familiar_with_process": 1.5,
    "application_experience": 0.5,
    "object_oriented_experience": 1.0,
    "lead_analyst_capability": 0.5,
    "motivation": 1.0,
    "stable_requirements": 2.0,
    "part_time_staff": -1.0,
    "difficult_programming_language": -1.0,
}


def _validate_complexity(name: str, value: str, weights: dict[str, int]) -> None:
    """Validate a complexity value.

    Args:
        name: Human-readable item name.
        value: Complexity value from the model.
        weights: Weight mapping.

    Raises:
        ValueError: If the complexity value is unsupported.
    """
    if value not in weights:
        allowed = ", ".join(weights)
        raise ValueError(f"{name} has invalid complexity '{value}'. Expected one of: {allowed}.")


def _weighted_count(items: list[dict[str, Any]], weights: dict[str, int], label: str) -> int:
    """Return a weighted count for actors or use cases.

    Args:
        items: Items with a `complexity` field.
        weights: Weight mapping.
        label: Category label used in error messages.

    Returns:
        Weighted total.

    Raises:
        ValueError: If an item is missing complexity or contains an invalid value.
    """
    total = 0
    for item in items:
        name = item.get("name") or item.get("id") or label
        complexity = item.get("complexity")
        if not complexity:
            raise ValueError(f"{label} '{name}' is missing a complexity value.")
        _validate_complexity(name, complexity, weights)
        total += weights[complexity]
    return total


def _weighted_factor_sum(
    factors: dict[str, Any],
    weights: dict[str, float],
    category: str,
) -> float:
    """Return the weighted factor sum for TCF or EF.

    Args:
        factors: Input factor values keyed by factor name.
        weights: Weight mapping.
        category: Human-readable category name.

    Returns:
        Weighted factor sum.

    Raises:
        ValueError: If a factor is missing or outside the allowed range.
    """
    total = 0.0
    for factor_name, factor_weight in weights.items():
        if factor_name not in factors:
            raise ValueError(f"Missing {category} factor '{factor_name}'.")
        value = factors[factor_name]
        if not isinstance(value, (int, float)) or not 0 <= value <= 5:
            raise ValueError(
                f"{category} factor '{factor_name}' must be a number between 0 and 5."
            )
        total += value * factor_weight
    return total


def calculate_ucp(model: dict[str, Any]) -> dict[str, Any]:
    """Calculate deterministic UCP results from a Rupify model.

    Args:
        model: Canonical Rupify model data.

    Returns:
        A dictionary containing intermediate totals and final outputs.

    Raises:
        ValueError: If required fields are missing or invalid.
    """
    actors = model.get("actors", [])
    use_cases = model.get("use_cases", [])
    ucp_section = model.get("ucp", {})

    if not actors:
        raise ValueError("Model does not contain any actors.")
    if not use_cases:
        raise ValueError("Model does not contain any use cases.")

    actor_total = _weighted_count(actors, ACTOR_WEIGHTS, "Actor")
    use_case_total = _weighted_count(use_cases, USE_CASE_WEIGHTS, "Use case")
    unadjusted_ucp = actor_total + use_case_total

    technical_factors = ucp_section.get("technical_factors", {})
    environmental_factors = ucp_section.get("environmental_factors", {})
    technical_total = _weighted_factor_sum(
        technical_factors,
        TECHNICAL_FACTOR_WEIGHTS,
        "technical",
    )
    environmental_total = _weighted_factor_sum(
        environmental_factors,
        ENVIRONMENTAL_FACTOR_WEIGHTS,
        "environmental",
    )

    technical_complexity_factor = 0.6 + (0.01 * technical_total)
    environmental_factor = 1.4 + (-0.03 * environmental_total)
    use_case_points = unadjusted_ucp * technical_complexity_factor * environmental_factor

    productivity_hours = ucp_section.get("productivity_hours_per_ucp", 20)
    if not isinstance(productivity_hours, (int, float)) or productivity_hours <= 0:
        raise ValueError("productivity_hours_per_ucp must be a positive number.")

    effort_hours = use_case_points * productivity_hours

    return {
        "actor_total": actor_total,
        "use_case_total": use_case_total,
        "unadjusted_ucp": unadjusted_ucp,
        "technical_total": technical_total,
        "environmental_total": environmental_total,
        "technical_complexity_factor": technical_complexity_factor,
        "environmental_factor": environmental_factor,
        "use_case_points": use_case_points,
        "productivity_hours_per_ucp": productivity_hours,
        "effort_hours": effort_hours,
        "open_questions": model.get("open_questions", []),
        "assumptions": model.get("assumptions", []),
    }


def render_ucp_markdown(model: dict[str, Any], results: dict[str, Any]) -> str:
    """Render a Markdown UCP estimate report.

    Args:
        model: Canonical Rupify model.
        results: Result of `calculate_ucp`.

    Returns:
        Markdown report content.
    """
    project_name = model.get("project", {}).get("name", "Unnamed Project")
    assumptions = "\n".join(
        _render_uncertainty_item(item) for item in normalize_uncertainty_list(results["assumptions"])
    ) or "- None"
    open_questions = "\n".join(
        _render_uncertainty_item(item)
        for item in normalize_uncertainty_list(results["open_questions"])
    ) or "- None"

    return f"""# UCP Estimate

## Project

{project_name}

## Summary

- `UAW`: {results["actor_total"]:.2f}
- `UUCW`: {results["use_case_total"]:.2f}
- `UUCP`: {results["unadjusted_ucp"]:.2f}
- `TCF`: {results["technical_complexity_factor"]:.3f}
- `EF`: {results["environmental_factor"]:.3f}
- `UCP`: {results["use_case_points"]:.3f}
- `Effort Hours`: {results["effort_hours"]:.2f}

## Inputs

- Technical factor weighted sum: {results["technical_total"]:.2f}
- Environmental factor weighted sum: {results["environmental_total"]:.2f}
- Productivity hours per UCP: {results["productivity_hours_per_ucp"]:.2f}

## Assumptions

{assumptions}

## Open Questions

{open_questions}
"""


def _render_uncertainty_item(item: dict[str, str]) -> str:
    """Render a normalized uncertainty item into one Markdown bullet."""
    details = []
    if item["status"]:
        details.append(f"status: {item['status']}")
    if item["source"]:
        details.append(f"source: {item['source']}")
    if item["last_updated"]:
        details.append(f"last updated: {item['last_updated']}")
    if item["notes"]:
        details.append(f"notes: {item['notes']}")

    if details:
        return f"- {item['text']} ({'; '.join(details)})"
    return f"- {item['text']}"
