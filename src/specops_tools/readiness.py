"""Readiness and staleness reporting for SpecOps interview state."""

from __future__ import annotations

from typing import Any


VIEW_REQUIREMENTS = {
    "discovery": {1, 2},
    "use_case": {3, 4},
    "logical": {5},
    "process": {6},
    "ucp": {7, 8, 9, 10},
}

VIEW_ARTIFACTS = {
    "discovery": ["requirements-spec.md"],
    "use_case": ["requirements-spec.md", "use-case-model.md"],
    "logical": ["requirements-spec.md"],
    "process": ["requirements-spec.md", "use-case-model.md"],
    "ucp": ["ucp-estimate.md"],
}


def _view_status(required_rounds: set[int], answered_rounds: set[int]) -> str:
    """Return the readiness state for one view."""
    answered_required = required_rounds & answered_rounds
    if answered_required == required_rounds:
        return "ready"
    if answered_required:
        return "partial"
    return "blocked"


def evaluate_readiness(round_inputs: list[dict[str, Any]]) -> dict[str, str]:
    """Evaluate readiness by view from replay rounds.

    Args:
        round_inputs: Canonical replay round inputs.

    Returns:
        Mapping of view name to readiness status.
    """
    answered_rounds = {int(item["round"]) for item in round_inputs}
    return {
        view_name: _view_status(required_rounds, answered_rounds)
        for view_name, required_rounds in VIEW_REQUIREMENTS.items()
    }


def identify_stale_artifacts(updates: list[dict[str, Any]]) -> list[str]:
    """Identify downstream artifacts impacted by updated interview rounds.

    Args:
        updates: Round update items.

    Returns:
        Sorted stale artifact names.
    """
    updated_rounds = {int(item["round"]) for item in updates}
    stale_artifacts: set[str] = set()
    for view_name, required_rounds in VIEW_REQUIREMENTS.items():
        if updated_rounds & required_rounds:
            stale_artifacts.update(VIEW_ARTIFACTS[view_name])
    return sorted(stale_artifacts)
