"""Readiness, staleness, and traceability reporting for Rupify interview state."""

from __future__ import annotations

from typing import Any


VIEW_GATES = {
    "discovery": {
        "required": ("idea", "problem", "in_scope", "outcomes"),
        "supporting": ("users", "out_of_scope", "success_criteria", "required_data", "constraints", "risks"),
    },
    "use_case": {
        "required": ("actors", "use_cases", "workflow_scope"),
        "supporting": (
            "integrations",
            "metadata_fields",
            "non_functional_requirements",
            "use_case_details",
            "scenarios",
            "ui_notes",
        ),
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
    "discovery": ["requirements-spec.md", "system-document.md"],
    "use_case": [
        "interaction-model.md",
        "requirements-spec.md",
        "scenario-documents.md",
        "system-document.md",
        "use-case-documents.md",
        "use-case-model.md",
    ],
    "logical": ["domain-model.md", "requirements-spec.md", "scenario-documents.md", "use-case-documents.md"],
    "process": [
        "requirements-spec.md",
        "scenario-documents.md",
        "use-case-documents.md",
        "use-case-model.md",
        "state-model.md",
    ],
    "architecture": [
        "deployment-model.md",
        "interaction-model.md",
        "requirements-spec.md",
        "scenario-documents.md",
        "system-document.md",
        "use-case-documents.md",
        "use-case-model.md",
    ],
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


def _linked_source_ids(
    links: list[dict[str, Any]],
    source_key: str = "from_id",
) -> set[str]:
    """Return source ids participating in a trace link collection."""
    return {
        str(link.get(source_key))
        for link in links
        if str(link.get(source_key, "")).strip()
    }


def _trace_family_result(
    expected_from_ids: list[str],
    links: list[dict[str, Any]],
    family: str,
    *,
    source_key: str = "from_id",
) -> dict[str, Any]:
    """Return validation details for one trace family."""
    expected = [item for item in expected_from_ids if item]
    linked = _linked_source_ids(links, source_key)
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
    artifact_source_objects = (
        requirement_objects
        + model.get("requirements", {}).get("acceptance_constraint_objects", [])
        + model.get("analysis_view", {}).get("ambiguity_objects", [])
        + use_cases
        + model.get("logical_view", {}).get("domain_entity_objects", [])
        + model.get("logical_view", {}).get("relationship_objects", [])
        + model.get("logical_view", {}).get("business_rule_objects", [])
        + model.get("logical_view", {}).get("domain_invariant_objects", [])
        + model.get("process_view", {}).get("state_entity_objects", [])
        + model.get("process_view", {}).get("state_transition_objects", [])
        + model.get("process_view", {}).get("trigger_objects", [])
        + model.get("process_view", {}).get("state_invariant_objects", [])
        + model.get("process_view", {}).get("guard_condition_objects", [])
        + model.get("process_view", {}).get("forbidden_transition_objects", [])
        + model.get("architecture_view", {}).get("component_objects", [])
        + model.get("architecture_view", {}).get("interface_objects", [])
        + model.get("architecture_view", {}).get("runtime_boundary_objects", [])
        + model.get("interaction_view", {}).get("realization_objects", [])
        + model.get("interaction_view", {}).get("message_objects", [])
    )

    return {
        "requirement_to_use_case": _trace_family_result(
            [item.get("id", "") for item in requirement_objects],
            traceability.get("requirement_to_use_case", []),
            "requirement_to_use_case",
        ),
        "requirement_to_step": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("analysis_view", {}).get("use_case_step_objects", [])
            ],
            traceability.get("requirement_to_step", []),
            "requirement_to_step",
            source_key="to_id",
        ),
        "use_case_to_analysis": _trace_family_result(
            [item.get("id", "") for item in use_cases] if analysis_objects else [],
            traceability.get("use_case_to_analysis", []),
            "use_case_to_analysis",
        ),
        "step_to_interaction": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("analysis_view", {}).get("use_case_step_objects", [])
            ]
            if model.get("interaction_view", {}).get("message_objects", [])
            else [],
            traceability.get("step_to_interaction", []),
            "step_to_interaction",
        ),
        "step_to_transition": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("analysis_view", {}).get("use_case_step_objects", [])
            ]
            if model.get("process_view", {}).get("state_transition_objects", [])
            else [],
            traceability.get("step_to_transition", []),
            "step_to_transition",
        ),
        "business_rule_to_transition": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("logical_view", {}).get("business_rule_objects", [])
            ]
            if model.get("process_view", {}).get("state_transition_objects", [])
            else [],
            traceability.get("business_rule_to_transition", []),
            "business_rule_to_transition",
        ),
        "domain_invariant_to_entity": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("logical_view", {}).get("domain_invariant_objects", [])
            ]
            if model.get("logical_view", {}).get("domain_entity_objects", [])
            else [],
            traceability.get("domain_invariant_to_entity", []),
            "domain_invariant_to_entity",
        ),
        "state_invariant_to_state": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("process_view", {}).get("state_invariant_objects", [])
            ]
            if model.get("process_view", {}).get("state_entity_objects", [])
            else [],
            traceability.get("state_invariant_to_state", []),
            "state_invariant_to_state",
        ),
        "guard_to_transition": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("process_view", {}).get("guard_condition_objects", [])
            ]
            if model.get("process_view", {}).get("state_transition_objects", [])
            else [],
            traceability.get("guard_to_transition", []),
            "guard_to_transition",
        ),
        "forbidden_transition_to_transition": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("process_view", {}).get("forbidden_transition_objects", [])
            ]
            if model.get("process_view", {}).get("state_transition_objects", [])
            else [],
            traceability.get("forbidden_transition_to_transition", []),
            "forbidden_transition_to_transition",
        ),
        "acceptance_constraint_to_requirement": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("requirements", {}).get("acceptance_constraint_objects", [])
                if item.get("source_requirement_id", "")
            ],
            traceability.get("acceptance_constraint_to_requirement", []),
            "acceptance_constraint_to_requirement",
        ),
        "ambiguity_to_element": _trace_family_result(
            [
                item.get("id", "")
                for item in model.get("analysis_view", {}).get("ambiguity_objects", [])
                if item.get("applies_to_element_ids", [])
            ],
            traceability.get("ambiguity_to_element", []),
            "ambiguity_to_element",
        ),
        "analysis_to_design": _trace_family_result(
            [item.get("id", "") for item in analysis_objects] if design_objects else [],
            traceability.get("analysis_to_design", []),
            "analysis_to_design",
        ),
        "artifact_lineage": _trace_family_result(
            [item.get("id", "") for item in artifact_source_objects],
            traceability.get("artifact_lineage", []),
            "artifact_lineage",
        ),
    }


def _unresolved_ambiguity_ids_by_element(model: dict[str, Any]) -> dict[str, list[str]]:
    """Return unresolved ambiguity ids grouped by the element ids they block."""
    ambiguity_lookup = {
        item.get("id", ""): item
        for item in model.get("analysis_view", {}).get("ambiguity_objects", [])
        if item.get("id")
    }
    unresolved_by_element: dict[str, list[str]] = {}
    for link in model.get("traceability", {}).get("ambiguity_to_element", []):
        ambiguity_id = str(link.get("from_id", "")).strip()
        element_id = str(link.get("to_id", "")).strip()
        ambiguity = ambiguity_lookup.get(ambiguity_id, {})
        resolution_status = str(ambiguity.get("resolution_status", "")).strip().lower()
        if not ambiguity_id or not element_id or resolution_status in {"resolved", "closed"}:
            continue
        unresolved_by_element.setdefault(element_id, []).append(ambiguity_id)
    return unresolved_by_element


def _base_element_result(
    item: dict[str, Any],
    family: str,
    required_fields: list[tuple[str, Any]],
    unresolved_ambiguities: dict[str, list[str]],
) -> dict[str, Any]:
    """Build one element-level readiness result."""
    item_id = str(item.get("id", "")).strip()
    missing_fields = []
    for field_name, value in required_fields:
        if isinstance(value, list):
            if not value:
                missing_fields.append(field_name)
            continue
        if not str(value).strip():
            missing_fields.append(field_name)

    blocking_ambiguity_ids = unresolved_ambiguities.get(item_id, [])
    if missing_fields:
        status = "blocked"
    elif blocking_ambiguity_ids:
        status = "partial"
    else:
        status = "ready"

    return {
        "id": item_id,
        "family": family,
        "content_semantics": item.get("content_semantics", ""),
        "status": status,
        "missing_fields": missing_fields,
        "blocking_ambiguity_ids": blocking_ambiguity_ids,
        "normative_ready": item.get("content_semantics") == "normative" and status == "ready",
    }


def evaluate_element_readiness(model: dict[str, Any]) -> dict[str, Any]:
    """Evaluate readiness on individual canonical elements that downstream tools consume."""
    analysis_view = model.get("analysis_view", {})
    process_view = model.get("process_view", {})
    unresolved_ambiguities = _unresolved_ambiguity_ids_by_element(model)

    family_specs = {
        "requirements": (
            model.get("requirements", {}).get("functional_objects", [])
            + model.get("requirements", {}).get("non_functional_objects", []),
            lambda item: [("statement", item.get("statement", ""))],
        ),
        "acceptance_constraints": (
            model.get("requirements", {}).get("acceptance_constraint_objects", []),
            lambda item: [("description", item.get("description", ""))],
        ),
        "use_cases": (
            analysis_view.get("use_cases", model.get("use_cases", [])),
            lambda item: [
                ("name", item.get("name", "")),
                ("goal", item.get("goal", "")),
                ("main_success_scenario", item.get("main_success_scenario", [])),
            ],
        ),
        "scenarios": (
            analysis_view.get("scenario_objects", model.get("scenarios", [])),
            lambda item: [
                ("name", item.get("name", "")),
                ("summary", item.get("summary", "")),
                ("flow_of_events", item.get("flow_of_events", [])),
            ],
        ),
        "use_case_steps": (
            analysis_view.get("use_case_step_objects", []),
            lambda item: [("text", item.get("text", ""))],
        ),
        "state_transitions": (
            process_view.get("state_transition_objects", []),
            lambda item: [("description", item.get("description", ""))],
        ),
        "domain_invariants": (
            model.get("logical_view", {}).get("domain_invariant_objects", []),
            lambda item: [
                ("description", item.get("description", "")),
                ("scope_entity_ids", item.get("scope_entity_ids", [])),
            ],
        ),
        "state_invariants": (
            process_view.get("state_invariant_objects", []),
            lambda item: [
                ("description", item.get("description", "")),
                ("state_entity_ids", item.get("state_entity_ids", [])),
            ],
        ),
        "guard_conditions": (
            process_view.get("guard_condition_objects", []),
            lambda item: [
                ("description", item.get("description", "")),
                ("related_transition_ids", item.get("related_transition_ids", [])),
            ],
        ),
        "forbidden_transitions": (
            process_view.get("forbidden_transition_objects", []),
            lambda item: [("description", item.get("description", ""))],
        ),
        "ambiguities": (
            analysis_view.get("ambiguity_objects", model.get("ambiguities", [])),
            lambda item: [("description", item.get("description", ""))],
        ),
    }

    by_family: dict[str, list[dict[str, Any]]] = {}
    all_items = []
    for family, (items, requirement_builder) in family_specs.items():
        family_results = [
            _base_element_result(item, family, requirement_builder(item), unresolved_ambiguities)
            for item in items
        ]
        by_family[family] = family_results
        all_items.extend(family_results)

    return {
        "by_family": by_family,
        "summary": {
            "ready_normative_ids": [
                item["id"]
                for item in all_items
                if item["content_semantics"] == "normative" and item["status"] == "ready"
            ],
            "partial_normative_ids": [
                item["id"]
                for item in all_items
                if item["content_semantics"] == "normative" and item["status"] == "partial"
            ],
            "blocked_normative_ids": [
                item["id"]
                for item in all_items
                if item["content_semantics"] == "normative" and item["status"] == "blocked"
            ],
            "informative_ids": [
                item["id"] for item in all_items if item["content_semantics"] == "informative"
            ],
        },
    }
