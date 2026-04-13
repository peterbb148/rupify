"""Readiness, staleness, and traceability reporting for SpecOps interview state."""

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


def _linked_source_ids(links: list[dict[str, Any]]) -> set[str]:
    """Return source ids participating in a trace link collection."""
    return {
        str(link.get("from_id"))
        for link in links
        if str(link.get("from_id", "")).strip()
    }


def _trace_family_result(
    expected_from_ids: list[str],
    links: list[dict[str, Any]],
    family: str,
) -> dict[str, Any]:
    """Return validation details for one trace family."""
    expected = [item for item in expected_from_ids if item]
    linked = _linked_source_ids(links)
    missing = [item for item in expected if item not in linked]

    if not expected:
        status = "blocked"
    elif not missing:
        status = "ready"
    elif len(missing) == len(expected):
        status = "blocked"
    else:
        status = "partial"

    return {
        "status": status,
        "expected_from_ids": expected,
        "linked_from_ids": sorted(linked),
        "missing_from_ids": missing,
        "link_count": len(links),
        "family": family,
    }


def evaluate_traceability(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Evaluate cross-view traceability coverage from the canonical model."""
    traceability = model.get("traceability", {})
    requirement_objects = model.get("requirements", {}).get("functional_objects", [])
    use_cases = model.get("use_cases", [])
    analysis_objects = (
        model.get("logical_view", {}).get("domain_entity_objects", [])
        + model.get("process_view", {}).get("state_entity_objects", [])
    )
    design_objects = model.get("architecture_view", {}).get("component_objects", [])

    return {
        "requirement_to_use_case": _trace_family_result(
            [item.get("id", "") for item in requirement_objects],
            traceability.get("requirement_to_use_case", []),
            "requirement_to_use_case",
        ),
        "use_case_to_analysis": _trace_family_result(
            [item.get("id", "") for item in use_cases] if analysis_objects else [],
            traceability.get("use_case_to_analysis", []),
            "use_case_to_analysis",
        ),
        "analysis_to_design": _trace_family_result(
            [item.get("id", "") for item in analysis_objects] if design_objects else [],
            traceability.get("analysis_to_design", []),
            "analysis_to_design",
        ),
    }
