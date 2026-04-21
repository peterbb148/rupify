"""Machine-oriented downstream planning export for Speckify."""

from __future__ import annotations

from typing import Any


ELEMENT_FAMILY_SPECS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("functional_requirements", ("requirements", "functional_objects")),
    ("non_functional_requirements", ("requirements", "non_functional_objects")),
    ("acceptance_constraints", ("requirements", "acceptance_constraint_objects")),
    ("actors", ("analysis_view", "actors")),
    ("use_cases", ("analysis_view", "use_cases")),
    ("use_case_steps", ("analysis_view", "use_case_step_objects")),
    ("scenarios", ("analysis_view", "scenario_objects")),
    ("ambiguities", ("analysis_view", "ambiguity_objects")),
    ("risks", ("analysis_view", "risk_objects")),
    ("domain_entities", ("logical_view", "domain_entity_objects")),
    ("relationships", ("logical_view", "relationship_objects")),
    ("business_rules", ("logical_view", "business_rule_objects")),
    ("domain_invariants", ("logical_view", "domain_invariant_objects")),
    ("state_entities", ("process_view", "state_entity_objects")),
    ("state_transitions", ("process_view", "state_transition_objects")),
    ("triggers", ("process_view", "trigger_objects")),
    ("state_invariants", ("process_view", "state_invariant_objects")),
    ("guard_conditions", ("process_view", "guard_condition_objects")),
    ("forbidden_transitions", ("process_view", "forbidden_transition_objects")),
    ("components", ("architecture_view", "component_objects")),
    ("interfaces", ("architecture_view", "interface_objects")),
    ("runtime_boundaries", ("architecture_view", "runtime_boundary_objects")),
    ("interaction_realizations", ("interaction_view", "realization_objects")),
    ("interaction_messages", ("interaction_view", "message_objects")),
)


def _get_nested(model: dict[str, Any], path: tuple[str, ...]) -> list[dict[str, Any]]:
    """Return a nested list from the canonical model."""
    current: Any = model
    for key in path:
        if not isinstance(current, dict):
            return []
        current = current.get(key, {})
    return current if isinstance(current, list) else []


def _pick_first_text(item: dict[str, Any]) -> str:
    """Return the most useful text field for one canonical item."""
    for key in (
        "statement",
        "description",
        "summary",
        "goal",
        "text",
        "rule_text",
        "condition_text",
        "name",
    ):
        value = str(item.get(key, "")).strip()
        if value:
            return value
    return ""


def _pick_first_name(item: dict[str, Any]) -> str:
    """Return the most useful name-like field for one canonical item."""
    for key in ("name", "use_case_name", "event_name"):
        value = str(item.get(key, "")).strip()
        if value:
            return value
    return ""


def _export_attributes(item: dict[str, Any]) -> dict[str, Any]:
    """Return machine-friendly family-specific attributes for one element."""
    attribute_keys = (
        "requirement_kind",
        "quality_attribute",
        "linked_use_case_ids",
        "linked_step_ids",
        "primary_actor_id",
        "supporting_actor_ids",
        "scenario_ids",
        "used_use_case_ids",
        "subordinate_use_case_ids",
        "preconditions",
        "postconditions",
        "main_success_scenario",
        "extensions",
        "flow_of_events",
        "scope_entity_ids",
        "state_entity_ids",
        "related_transition_ids",
        "related_transition_id",
        "source_requirement_id",
        "source_business_rule_id",
        "source_trigger_id",
        "applies_to_element_ids",
        "blocking_for_downstream",
        "resolution_status",
        "priority",
        "status",
        "complexity",
        "constraint_kind",
        "ambiguity_type",
        "from_state",
        "to_state",
        "trigger",
        "state_entity_id",
        "source_entity_id",
        "target_entity_id",
        "source_component_id",
        "target_component_id",
        "component_kind",
        "interaction_verb",
        "runtime_environment",
        "boundary_type",
    )
    return {
        key: item[key]
        for key in attribute_keys
        if key in item and item.get(key) not in ("", [], {}, None)
    }


def _export_obligations(item: dict[str, Any]) -> list[dict[str, Any]]:
    """Return exported sub-obligation records for one canonical element."""
    return [
        {
            "id": obligation.get("id", ""),
            "title": obligation.get("title", ""),
            "summary": obligation.get("summary", ""),
            "acceptance": obligation.get("acceptance", ""),
            "parent_requirement_id": obligation.get("parent_requirement_id", ""),
            "parent_requirement_semantic_id": obligation.get(
                "parent_requirement_semantic_id",
                "",
            ),
        }
        for obligation in item.get("sub_obligations", [])
        if isinstance(obligation, dict)
    ]


def _export_element(item: dict[str, Any], family: str) -> dict[str, Any]:
    """Convert one canonical element into the planning export shape."""
    readiness = item.get("readiness", {})
    trace = item.get("trace", {})
    exported = {
        "id": item.get("id", ""),
        "semantic_id": item.get("semantic_id", item.get("id", "")),
        "family": family,
        "name": _pick_first_name(item),
        "text": _pick_first_text(item),
        "content_semantics": item.get("content_semantics", ""),
        "readiness_status": readiness.get("status", ""),
        "normative_ready": readiness.get("normative_ready", False),
        "missing_fields": list(readiness.get("missing_fields", [])),
        "blocking_ambiguity_ids": list(readiness.get("blocking_ambiguity_ids", [])),
        "source_round": trace.get("source_round", ""),
        "source_key": trace.get("source_key", ""),
        "change_metadata": item.get("change_metadata", {}),
        "attributes": _export_attributes(item),
    }
    obligations = _export_obligations(item)
    if obligations:
        exported["obligations"] = obligations
    return exported


def _export_trace_link(link: dict[str, Any], family: str) -> dict[str, Any]:
    """Convert one canonical trace link into the planning export shape."""
    return {
        "id": link.get("id", ""),
        "semantic_id": link.get("semantic_id", link.get("id", "")),
        "family": family,
        "from_id": link.get("from_id", ""),
        "to_id": link.get("to_id", ""),
        "to_artifact": link.get("to_artifact", ""),
        "artifact_section": link.get("artifact_section", ""),
        "link_type": link.get("link_type", ""),
        "basis": link.get("basis", ""),
        "change_metadata": link.get("change_metadata", {}),
    }


def build_planning_export(model: dict[str, Any]) -> dict[str, Any]:
    """Build the strict downstream planning export consumed by Speckify."""
    elements = []
    for family, path in ELEMENT_FAMILY_SPECS:
        elements.extend(_export_element(item, family) for item in _get_nested(model, path))
    elements.sort(key=lambda item: (item["family"], item["semantic_id"], item["id"]))

    trace_links = []
    for family, links in sorted(model.get("traceability", {}).items()):
        if not isinstance(links, list):
            continue
        trace_links.extend(_export_trace_link(link, family) for link in links)
    trace_links.sort(key=lambda item: (item["family"], item["semantic_id"], item["id"]))

    ready_normative_elements = [
        item
        for item in elements
        if item["content_semantics"] == "normative" and item["readiness_status"] == "ready"
    ]
    blocking_ambiguities = [
        item
        for item in elements
        if item["family"] == "ambiguities" and item["attributes"].get("blocking_for_downstream")
    ]

    return {
        "export_metadata": {
            "schema_version": 1,
            "export_kind": "speckify_planning_export",
            "source_model_semantic_id": model.get("model_metadata", {}).get("semantic_id", ""),
            "source_model_change_metadata": model.get("model_metadata", {}).get("change_metadata", {}),
        },
        "summary": {
            "element_count": len(elements),
            "trace_link_count": len(trace_links),
            "ready_normative_count": len(ready_normative_elements),
            "blocking_ambiguity_count": len(blocking_ambiguities),
            "ready_normative_ids": [item["id"] for item in ready_normative_elements],
            "partial_or_blocked_normative_ids": [
                item["id"]
                for item in elements
                if item["content_semantics"] == "normative" and item["readiness_status"] != "ready"
            ],
            "blocking_ambiguity_ids": [item["id"] for item in blocking_ambiguities],
        },
        "elements": elements,
        "ready_normative_elements": ready_normative_elements,
        "blocking_ambiguities": blocking_ambiguities,
        "trace_links": trace_links,
    }
