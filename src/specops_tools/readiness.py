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

MODEL_GATES = {
    "use_case": (
        ("actors", "actor objects"),
        ("use_cases", "use-case objects"),
        ("requirements.functional_objects", "functional requirement objects"),
    ),
    "logical": (
        ("logical_view.domain_entity_objects", "domain entity objects"),
        ("logical_view.relationship_objects", "relationship objects"),
    ),
    "process": (
        ("process_view.state_entity_objects", "state entity objects"),
        ("process_view.state_transition_objects", "state transition objects"),
    ),
    "architecture": (
        ("architecture_view.component_objects", "component objects"),
        ("architecture_view.interface_objects", "interface objects"),
    ),
    "ucp": (
        ("ucp.technical_factors", "technical factors"),
        ("ucp.environmental_factors", "environmental factors"),
    ),
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
    model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return detailed gate status for one view."""
    gate = VIEW_GATES[view_name]
    required = set(gate["required"])
    supporting = set(gate["supporting"])
    required_present = sorted(required & answered_keys)
    required_missing = sorted(required - answered_keys)
    supporting_present = sorted(supporting & answered_keys)
    supporting_missing = sorted(supporting - answered_keys)
    model_present: list[str] = []
    model_missing: list[str] = []

    if model is not None:
        for path, label in MODEL_GATES.get(view_name, ()):
            if _model_has_content(model, path):
                model_present.append(label)
            else:
                model_missing.append(label)

    if not required_missing and not model_missing:
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
        "model_present": model_present,
        "model_missing": model_missing,
    }


def _get_model_value(model: dict[str, Any], path: str) -> Any:
    """Resolve a dotted path from the canonical model."""
    current: Any = model
    for segment in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(segment)
    return current


def _model_has_content(model: dict[str, Any], path: str) -> bool:
    """Return whether a canonical model path contains meaningful data."""
    value = _get_model_value(model, path)
    if value is None:
        return False
    if isinstance(value, dict):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return str(value).strip() != ""


def evaluate_readiness_details(
    round_inputs: list[dict[str, Any]],
    model: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Evaluate detailed readiness by view from replay rounds."""
    answered_keys = _answered_keys(round_inputs)
    return {
        view_name: _view_detail(view_name, answered_keys, model)
        for view_name in VIEW_GATES
    }


def evaluate_readiness(
    round_inputs: list[dict[str, Any]],
    model: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Evaluate readiness by view from replay rounds."""
    return {
        view_name: detail["status"]
        for view_name, detail in evaluate_readiness_details(round_inputs, model).items()
    }


def identify_stale_artifacts(updates: list[dict[str, Any]]) -> list[str]:
    """Identify downstream artifacts impacted by updated interview rounds."""
    updated_keys = _answered_keys(updates)
    stale_artifacts: set[str] = set()
    for view_name, gate in VIEW_GATES.items():
        if updated_keys & (set(gate["required"]) | set(gate["supporting"])):
            stale_artifacts.update(VIEW_ARTIFACTS[view_name])
    return sorted(stale_artifacts)
