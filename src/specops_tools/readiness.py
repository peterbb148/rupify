"""Readiness and staleness reporting for SpecOps interview state."""

from __future__ import annotations

from typing import Any


VIEW_GATES = {
    "discovery": {
        "required": ("idea", "problem", "in_scope", "outcomes"),
        "supporting": ("users", "out_of_scope", "success_criteria", "required_data", "constraints"),
    },
    "use_case": {
        "required": ("actors", "use_cases", "workflow_scope"),
        "supporting": ("integrations", "metadata_fields", "non_functional_requirements"),
    },
    "logical": {
        "required": ("domain_entities", "relationships"),
        "supporting": ("business_rules",),
    },
    "process": {
        "required": ("state_entities", "states_and_transitions"),
        "supporting": ("triggers_and_approvals",),
    },
    "architecture": {
        "required": ("components_and_services", "interfaces_and_integrations"),
        "supporting": ("runtime_boundaries",),
    },
    "ucp": {
        "required": ("actor_complexity", "use_case_complexity", "technical", "environmental"),
        "supporting": (),
    },
}

VIEW_ARTIFACTS = {
    "discovery": ["requirements-spec.md"],
    "use_case": ["requirements-spec.md", "use-case-model.md"],
    "logical": ["requirements-spec.md"],
    "process": ["requirements-spec.md", "use-case-model.md"],
    "architecture": ["requirements-spec.md", "use-case-model.md"],
    "ucp": ["ucp-estimate.md"],
}


def _has_answer(value: Any) -> bool:
    """Return whether a replay answer should count as filled."""
    return str(value).strip() != ""


def _answered_keys(round_inputs: list[dict[str, Any]]) -> set[str]:
    """Return all question keys that currently have non-empty answers."""
    answered = set()
    for item in round_inputs:
        for response in item.get("responses", []):
            if _has_answer(response.get("answer", "")):
                answered.add(str(response["key"]))
    return answered


def _view_detail(
    view_name: str,
    answered_keys: set[str],
) -> dict[str, Any]:
    """Return detailed gate status for one view."""
    gate = VIEW_GATES[view_name]
    required = set(gate["required"])
    supporting = set(gate["supporting"])
    required_present = sorted(required & answered_keys)
    required_missing = sorted(required - answered_keys)
    supporting_present = sorted(supporting & answered_keys)
    supporting_missing = sorted(supporting - answered_keys)

    if not required_missing:
        status = "ready"
    elif required_present or supporting_present:
        status = "partial"
    else:
        status = "blocked"

    return {
        "status": status,
        "required_present": required_present,
        "required_missing": required_missing,
        "supporting_present": supporting_present,
        "supporting_missing": supporting_missing,
    }


def evaluate_readiness_details(round_inputs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Evaluate detailed readiness by view from replay rounds."""
    answered_keys = _answered_keys(round_inputs)
    return {
        view_name: _view_detail(view_name, answered_keys)
        for view_name in VIEW_GATES
    }


def evaluate_readiness(round_inputs: list[dict[str, Any]]) -> dict[str, str]:
    """Evaluate readiness by view from replay rounds."""
    return {
        view_name: detail["status"]
        for view_name, detail in evaluate_readiness_details(round_inputs).items()
    }


def identify_stale_artifacts(updates: list[dict[str, Any]]) -> list[str]:
    """Identify downstream artifacts impacted by updated interview rounds."""
    updated_keys = _answered_keys(updates)
    stale_artifacts: set[str] = set()
    for view_name, gate in VIEW_GATES.items():
        if updated_keys & (set(gate["required"]) | set(gate["supporting"])):
            stale_artifacts.update(VIEW_ARTIFACTS[view_name])
    return sorted(stale_artifacts)
