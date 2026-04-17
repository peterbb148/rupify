"""Markdown rendering for Rupify artifacts."""

from __future__ import annotations

from typing import Any

from .model_metadata import normalize_uncertainty_list
from .ucp import calculate_ucp, render_ucp_markdown


def _bullet_list(items: list[str]) -> str:
    """Render a flat Markdown bullet list.

    Args:
        items: Items to render.

    Returns:
        Markdown text.
    """
    return "\n".join(f"- {item}" for item in items) or "- None"


def _uncertainty_list(items: list[Any]) -> str:
    """Render assumptions or open questions with optional metadata.

    Args:
        items: Raw uncertainty items.

    Returns:
        Markdown text.
    """
    normalized_items = normalize_uncertainty_list(items)
    if not normalized_items:
        return "- None"

    rendered = []
    for item in normalized_items:
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
            rendered.append(f"- {item['text']} ({'; '.join(details)})")
        else:
            rendered.append(f"- {item['text']}")
    return "\n".join(rendered)


def _named_section(title: str, items: list[str]) -> str:
    """Render a markdown section only when items exist."""
    if not items:
        return ""
    return f"""
## {title}

{_bullet_list(items)}
"""


def _object_name_section(
    title: str,
    items: list[dict[str, Any]],
    fallback: list[str],
) -> str:
    """Render a section from named objects, falling back to strings."""
    if items:
        rendered = []
        for item in items:
            line = f"- `{item.get('id', 'item')}` {item.get('name', 'Unnamed')}"
            if item.get("attributes"):
                line = f"{line} [{', '.join(item['attributes'])}]"
            if item.get("states"):
                line = f"{line} {{states: {', '.join(item['states'])}}}"
            if item.get("description"):
                line = f"{line}: {item['description']}"
            if trace := item.get("trace"):
                line = (
                    f"{line} [source: round {trace.get('source_round')} "
                    f"{trace.get('source_key')}]"
                )
            rendered.append(line)
        return f"""
## {title}

{"\n".join(rendered)}
"""
    return _named_section(title, fallback)


def _object_text_section(
    title: str,
    items: list[dict[str, Any]],
    fallback: list[str],
) -> str:
    """Render a section from text objects, falling back to strings."""
    if items:
        rendered_lines = []
        for item in items:
            text = item.get("text") or item.get("description") or item.get("rule_text") or ""
            line = f"- `{item.get('id', 'item')}` {text}"
            if trace := item.get("trace"):
                line = (
                    f"{line} [source: round {trace.get('source_round')} "
                    f"{trace.get('source_key')}]"
                )
            rendered_lines.append(line)
        rendered = "\n".join(rendered_lines)
        return f"""
## {title}

{rendered}
"""
    return _named_section(title, fallback)


def _traceability_section(
    title: str,
    links: list[dict[str, Any]],
) -> str:
    """Render a cross-view traceability section when links exist."""
    if not links:
        return ""

    rendered = []
    for link in links:
        rendered.append(
            f"- `{link.get('id', 'trace')}` {link.get('from_id', 'unknown')} -> "
            f"{link.get('to_id', 'unknown')} ({link.get('basis', 'unspecified basis')})"
        )

    return f"""
## {title}

{"\n".join(rendered)}
"""


def _artifact_lineage_section(
    title: str,
    links: list[dict[str, Any]],
    artifact_name: str,
) -> str:
    """Render artifact-lineage links for one generated artifact."""
    relevant_links = [link for link in links if link.get("to_artifact") == artifact_name]
    if not relevant_links:
        return ""

    rendered = []
    for link in relevant_links:
        rendered.append(
            f"- `{link.get('id', 'trace')}` {link.get('from_id', 'unknown')} -> "
            f"{link.get('to_artifact', artifact_name)}#{link.get('artifact_section', 'unspecified')} "
            f"({link.get('basis', 'unspecified basis')})"
        )

    return f"""
## {title}

{"\n".join(rendered)}
"""


def _relationship_section(
    title: str,
    items: list[dict[str, Any]],
    fallback: list[str],
) -> str:
    """Render relationships with richer class-model semantics when present."""
    if items:
        rendered = []
        for item in items:
            semantic_bits = []
            if item.get("source_multiplicity") or item.get("target_multiplicity"):
                semantic_bits.append(
                    f"multiplicity: {item.get('source_multiplicity', '')} -> {item.get('target_multiplicity', '')}"
                )
            if item.get("source_role_name") or item.get("target_role_name"):
                semantic_bits.append(
                    f"roles: {item.get('source_role_name', '')} / {item.get('target_role_name', '')}"
                )
            line = f"- `{item.get('id', 'item')}` {item.get('description', '')}"
            if semantic_bits:
                line = f"{line} ({'; '.join(semantic_bits)})"
            if trace := item.get("trace"):
                line = (
                    f"{line} [source: round {trace.get('source_round')} "
                    f"{trace.get('source_key')}]"
                )
            rendered.append(line)
        return f"""
## {title}

{"\n".join(rendered)}
"""
    return _named_section(title, fallback)


def _state_transition_section(
    title: str,
    items: list[dict[str, Any]],
    fallback: list[str],
) -> str:
    """Render transitions with richer state-machine semantics when present."""
    if items:
        rendered = []
        for item in items:
            from_state = item.get("from_state", "")
            to_state = item.get("to_state", "")
            if from_state or to_state:
                line = (
                    f"- `{item.get('id', 'item')}` {from_state or '?'} -> {to_state or '?'}"
                )
            else:
                text = item.get("description") or item.get("text") or ""
                line = f"- `{item.get('id', 'item')}` {text}"

            semantic_bits = []
            if item.get("state_entity_name"):
                semantic_bits.append(f"entity: {item['state_entity_name']}")
            if item.get("trigger"):
                semantic_bits.append(f"trigger: {item['trigger']}")
            if item.get("constraint"):
                semantic_bits.append(f"constraint: {item['constraint']}")
            if item.get("is_exception_flow"):
                semantic_bits.append("exception flow")
            if item.get("is_terminal_transition"):
                semantic_bits.append("terminal transition")
            if semantic_bits:
                line = f"{line} ({'; '.join(semantic_bits)})"

            if trace := item.get("trace"):
                line = (
                    f"{line} [source: round {trace.get('source_round')} "
                    f"{trace.get('source_key')}]"
                )
            rendered.append(line)
        return f"""
## {title}

{"\n".join(rendered)}
"""
    return _named_section(title, fallback)


def _trigger_section(
    title: str,
    items: list[dict[str, Any]],
    fallback: list[str],
) -> str:
    """Render lifecycle constraints and triggers with explicit process semantics."""
    if items:
        rendered = []
        for item in items:
            text = (
                item.get("description")
                or item.get("text")
                or item.get("outcome")
                or item.get("event_name")
                or ""
            )
            line = f"- `{item.get('id', 'item')}` {text}"
            semantic_bits = []
            if item.get("event_name"):
                semantic_bits.append(f"event: {item['event_name']}")
            if item.get("constraint_type"):
                semantic_bits.append(f"type: {item['constraint_type']}")
            if item.get("approval_required"):
                semantic_bits.append("approval required")
            if item.get("exceptional_behavior"):
                semantic_bits.append("exceptional behavior")
            if semantic_bits:
                line = f"{line} ({'; '.join(semantic_bits)})"
            if trace := item.get("trace"):
                line = (
                    f"{line} [source: round {trace.get('source_round')} "
                    f"{trace.get('source_key')}]"
                )
            rendered.append(line)
        return f"""
## {title}

{"\n".join(rendered)}
"""
    return _named_section(title, fallback)


def _filter_trace_links(
    links: list[dict[str, Any]],
    relevant_ids: set[str],
) -> list[dict[str, Any]]:
    """Keep only trace links that reference the relevant ids."""
    return [
        link
        for link in links
        if link.get("from_id") in relevant_ids or link.get("to_id") in relevant_ids
    ]


def _component_line(component: dict[str, Any]) -> str:
    """Render one component or subsystem line."""
    line = f"- `{component.get('id', 'component')}` {component.get('name', 'Unnamed')}"
    if component.get("description"):
        line = f"{line}: {component['description']}"
    if trace := component.get("trace"):
        line = (
            f"{line} [source: round {trace.get('source_round')} "
            f"{trace.get('source_key')}]"
        )
    return line


def _lookup_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Return a lookup keyed by canonical object id."""
    return {
        str(item.get("id", "")).strip(): item
        for item in items
        if str(item.get("id", "")).strip()
    }


def _name_list_from_ids(
    ids: list[str],
    lookup: dict[str, dict[str, Any]],
) -> list[str]:
    """Resolve object ids to their names, falling back to the raw id."""
    names = []
    for item_id in ids:
        match = lookup.get(item_id, {})
        names.append(match.get("name") or match.get("statement") or item_id)
    return names


def _supporting_actor_names(
    use_case: dict[str, Any],
    actor_lookup: dict[str, dict[str, Any]],
) -> list[str]:
    """Resolve supporting actor ids into display names."""
    names = _name_list_from_ids(use_case.get("supporting_actor_ids", []), actor_lookup)
    if names:
        return names
    return []


def _scenario_section(scenario: dict[str, Any]) -> str:
    """Render one scenario summary block."""
    overview_bits = []
    if scenario.get("priority"):
        overview_bits.append(f"Priority: {scenario['priority']}")
    if scenario.get("status"):
        overview_bits.append(f"Status: {scenario['status']}")
    overview = "\n".join(f"- {item}" for item in overview_bits) or "- None"
    flow = "\n".join(
        f"{index}. {step}" for index, step in enumerate(scenario.get("flow_of_events", []), 1)
    ) or "1. No scenario flow documented."

    return f"""#### {scenario.get("name", "Unnamed Scenario")}

- Summary: {scenario.get("summary", "Unspecified")}
{overview}

##### Flow of Events

{flow}

##### Activity Notes

{_bullet_list(scenario.get("activity_notes", []))}

##### Sequence Notes

{_bullet_list(scenario.get("sequence_notes", []))}
"""


def render_system_document(model: dict[str, Any]) -> str:
    """Render the system/subsystem document artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Markdown content.
    """
    project = model.get("project", {})
    analysis_view = model.get("analysis_view", {})
    design_view = model.get("design_view", {})
    architecture_view = model.get("architecture_view", {})
    traceability = model.get("traceability", {})
    use_cases = analysis_view.get("use_cases", model.get("use_cases", []))
    risks = analysis_view.get("risk_objects", model.get("risks", []))
    component_objects = design_view.get(
        "component_objects",
        architecture_view.get("component_objects", []),
    )
    interface_objects = design_view.get(
        "interface_objects",
        architecture_view.get("interface_objects", []),
    )
    runtime_boundary_objects = design_view.get(
        "runtime_boundary_objects",
        architecture_view.get("runtime_boundary_objects", []),
    )

    brief_description_parts = [
        project.get("problem_statement", "").strip(),
        project.get("system_scope", "").strip(),
    ]
    brief_description = "\n\n".join(part for part in brief_description_parts if part) or "Unspecified"

    risk_lines = []
    for risk in risks:
        line = f"- `{risk.get('id', 'risk')}` {risk.get('name', 'Unnamed risk')}"
        details = []
        if risk.get("priority"):
            details.append(f"priority: {risk['priority']}")
        if risk.get("status"):
            details.append(f"status: {risk['status']}")
        if details:
            line = f"{line} ({'; '.join(details)})"
        if risk.get("description") and risk.get("description") != risk.get("name"):
            line = f"{line}: {risk['description']}"
        if risk.get("mitigation"):
            line = f"{line} Mitigation: {risk['mitigation']}."
        if trace := risk.get("trace"):
            line = (
                f"{line} [source: round {trace.get('source_round')} "
                f"{trace.get('source_key')}]"
            )
        risk_lines.append(line)
    risk_block = "\n".join(risk_lines) or "- None"

    use_case_lines = []
    for use_case in use_cases:
        line = f"- `{use_case.get('id', 'use-case')}` {use_case.get('name', 'Unnamed Use Case')}"
        details = []
        if use_case.get("primary_actor"):
            details.append(f"actor: {use_case['primary_actor']}")
        if use_case.get("priority"):
            details.append(f"priority: {use_case['priority']}")
        if use_case.get("status"):
            details.append(f"status: {use_case['status']}")
        if details:
            line = f"{line} ({'; '.join(details)})"
        if use_case.get("goal"):
            line = f"{line}: {use_case['goal']}"
        use_case_lines.append(line)
    use_case_block = "\n".join(use_case_lines) or "- None"
    subsystem_lines = "\n".join(_component_line(component) for component in component_objects) or "- None"

    return f"""# System / Subsystem Document

## System Name

{project.get("name", "Unnamed Project")}

## Brief Description

{brief_description}

## Risk Factors

{risk_block}

## System-Level Use Cases

{use_case_block}

## System-Level Diagram References

- `use-case-model.md` for the detailed system-level use-case view
- `deployment-model.md` for the detailed architecture and runtime view

{_object_name_section(
    "Architecture Overview",
    component_objects,
    architecture_view.get("components_and_services", []),
)}
{_object_text_section(
    "Interfaces and Integrations",
    interface_objects,
    architecture_view.get("interfaces_and_integrations", []),
)}
{_object_text_section(
    "Runtime Boundaries",
    runtime_boundary_objects,
    architecture_view.get("runtime_boundaries", []),
)}
## Subsystem Descriptions

{subsystem_lines}
{_artifact_lineage_section(
    "Artifact Lineage",
    traceability.get("artifact_lineage", []),
    "system-document.md",
)}
"""


def render_requirements_spec(model: dict[str, Any]) -> str:
    """Render the requirements specification artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Markdown content.
    """
    project = model.get("project", {})
    requirements = model.get("requirements", {})
    analysis_view = model.get("analysis_view", {})
    design_view = model.get("design_view", {})
    logical_view = model.get("logical_view", {})
    process_view = model.get("process_view", {})
    architecture_view = model.get("architecture_view", {})
    traceability = model.get("traceability", {})
    domain_entity_objects = analysis_view.get("domain_entity_objects", logical_view.get("domain_entity_objects", []))
    relationship_objects = analysis_view.get("relationship_objects", logical_view.get("relationship_objects", []))
    business_rule_objects = analysis_view.get("business_rule_objects", logical_view.get("business_rule_objects", []))
    state_entity_objects = analysis_view.get("state_entity_objects", process_view.get("state_entity_objects", []))
    state_transition_objects = analysis_view.get(
        "state_transition_objects",
        process_view.get("state_transition_objects", []),
    )
    trigger_objects = analysis_view.get("trigger_objects", process_view.get("trigger_objects", []))
    component_objects = design_view.get("component_objects", architecture_view.get("component_objects", []))
    interface_objects = design_view.get("interface_objects", architecture_view.get("interface_objects", []))
    runtime_boundary_objects = design_view.get(
        "runtime_boundary_objects",
        architecture_view.get("runtime_boundary_objects", []),
    )
    return f"""# Requirements Specification

## Project

- Name: {project.get("name", "Unnamed Project")}
- Domain: {project.get("domain", "Unspecified")}
- Scope: {project.get("system_scope", "Unspecified")}

## Problem Statement

{project.get("problem_statement", "Unspecified")}

## Business Goals

{_bullet_list(model.get("business_goals", []))}

## Success Criteria

{_bullet_list(model.get("success_criteria", []))}

## Functional Requirements

{_bullet_list(requirements.get("functional", []))}

## Non-Functional Requirements

{_bullet_list(requirements.get("non_functional", []))}
{_object_name_section(
    "Logical View",
    domain_entity_objects,
    logical_view.get("domain_entities", []),
)}
{_object_text_section(
    "Relationships",
    relationship_objects,
    logical_view.get("relationships", []),
)}
{_object_text_section(
    "Business Rules",
    business_rule_objects,
    logical_view.get("business_rules", []),
)}
{_object_name_section(
    "Process View",
    state_entity_objects,
    process_view.get("state_entities", []),
)}
{_object_text_section(
    "States and Transitions",
    state_transition_objects,
    process_view.get("states_and_transitions", []),
)}
{_object_text_section(
    "Triggers and Approvals",
    trigger_objects,
    process_view.get("triggers_and_approvals", []),
)}
{_object_name_section(
    "Architecture View",
    component_objects,
    architecture_view.get("components_and_services", []),
)}
{_object_text_section(
    "Interfaces and Integrations",
    interface_objects,
    architecture_view.get("interfaces_and_integrations", []),
)}
{_object_text_section(
    "Runtime Boundaries",
    runtime_boundary_objects,
    architecture_view.get("runtime_boundaries", []),
)}
{_traceability_section(
    "Requirement To Use-Case Traceability",
    traceability.get("requirement_to_use_case", []),
)}
{_traceability_section(
    "Use-Case To Analysis Traceability",
    traceability.get("use_case_to_analysis", []),
)}
{_traceability_section(
    "Analysis To Design Traceability",
    traceability.get("analysis_to_design", []),
)}

## Assumptions

{_uncertainty_list(model.get("assumptions", []))}

## Open Questions

{_uncertainty_list(model.get("open_questions", []))}
"""


def render_use_case_model(model: dict[str, Any]) -> str:
    """Render the use-case model artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Markdown content.
    """
    analysis_view = model.get("analysis_view", {})
    design_view = model.get("design_view", {})
    actors = analysis_view.get("actors", model.get("actors", []))
    use_cases = analysis_view.get("use_cases", model.get("use_cases", []))
    actor_lines = []
    for actor in actors:
        line = (
            f"- `{actor.get('id', 'actor')}` {actor.get('name', 'Unnamed')} "
            f"({actor.get('type', 'unspecified')}, {actor.get('complexity', 'unclassified')}): "
            f"{actor.get('description', 'No description')}"
        )
        if trace := actor.get("trace"):
            line = (
                f"{line} [source: round {trace.get('source_round')} "
                f"{trace.get('source_key')}]"
            )
        actor_lines.append(line)

    use_case_sections = []
    for use_case in use_cases:
        main_flow = "\n".join(
            f"{index}. {step}" for index, step in enumerate(use_case.get("main_success_scenario", []), 1)
        ) or "1. No main success scenario documented."
        extensions = "\n".join(f"- {item}" for item in use_case.get("extensions", [])) or "- None"
        use_case_sections.append(
            f"""### {use_case.get("name", "Unnamed Use Case")}

- ID: `{use_case.get("id", "use-case")}`
- Primary actor: {use_case.get("primary_actor", "Unspecified")}
- Complexity: {use_case.get("complexity", "unclassified")}
- Goal: {use_case.get("goal", "Unspecified")}
- Source: round {use_case.get("trace", {}).get("source_round", "n/a")} {use_case.get("trace", {}).get("source_key", "")}

#### Main Success Scenario

{main_flow}

#### Extensions

{extensions}
"""
        )

    actor_block = "\n".join(actor_lines) or "- None"
    use_case_block = "\n".join(use_case_sections) or "No use cases documented."
    process_view = model.get("process_view", {})
    architecture_view = model.get("architecture_view", {})
    traceability = model.get("traceability", {})
    state_transition_objects = analysis_view.get(
        "state_transition_objects",
        process_view.get("state_transition_objects", []),
    )
    trigger_objects = analysis_view.get("trigger_objects", process_view.get("trigger_objects", []))
    interface_objects = design_view.get("interface_objects", architecture_view.get("interface_objects", []))

    return f"""# Use-Case Model

## Actors

{actor_block}

## Use Cases

{use_case_block}
{_object_text_section(
    "States and Transitions",
    state_transition_objects,
    process_view.get("states_and_transitions", []),
)}
{_object_text_section(
    "Triggers and Approvals",
    trigger_objects,
    process_view.get("triggers_and_approvals", []),
)}
{_object_text_section(
    "Interfaces and Integrations",
    interface_objects,
    architecture_view.get("interfaces_and_integrations", []),
)}
{_traceability_section(
    "Requirement To Use-Case Traceability",
    traceability.get("requirement_to_use_case", []),
)}
{_traceability_section(
    "Use-Case To Analysis Traceability",
    traceability.get("use_case_to_analysis", []),
)}
"""


def render_use_case_documents(model: dict[str, Any]) -> str:
    """Render the compiled template-driven use-case document artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Markdown content.
    """
    analysis_view = model.get("analysis_view", {})
    logical_view = model.get("logical_view", {})
    process_view = model.get("process_view", {})
    interaction_view = model.get("interaction_view", {})
    use_cases = analysis_view.get("use_cases", model.get("use_cases", []))
    actors = analysis_view.get("actors", model.get("actors", []))
    scenarios = analysis_view.get("scenario_objects", model.get("scenarios", []))
    requirement_objects = analysis_view.get(
        "requirement_objects",
        model.get("requirements", {}).get("functional_objects", [])
        + model.get("requirements", {}).get("non_functional_objects", []),
    )
    domain_entity_objects = analysis_view.get(
        "domain_entity_objects",
        logical_view.get("domain_entity_objects", []),
    )
    relationship_objects = analysis_view.get(
        "relationship_objects",
        logical_view.get("relationship_objects", []),
    )
    state_entity_objects = analysis_view.get(
        "state_entity_objects",
        process_view.get("state_entity_objects", []),
    )
    realization_objects = interaction_view.get("realization_objects", [])
    traceability = model.get("traceability", {})

    if not use_cases:
        return "# Use-Case Documents\n\nNo use cases documented."

    actor_lookup = _lookup_by_id(actors)
    use_case_lookup = _lookup_by_id(use_cases)
    scenario_lookup = _lookup_by_id(scenarios)
    requirement_lookup = _lookup_by_id(requirement_objects)
    participating_lookup = _lookup_by_id(
        domain_entity_objects + relationship_objects + state_entity_objects
    )
    realizations_by_use_case: dict[str, list[dict[str, Any]]] = {}
    for realization in realization_objects:
        use_case_id = str(realization.get("use_case_id", "")).strip()
        if use_case_id:
            realizations_by_use_case.setdefault(use_case_id, []).append(realization)

    sections = []
    for use_case in use_cases:
        use_case_id = use_case.get("id", "")
        scenario_sections = [
            _scenario_section(scenario_lookup[scenario_id])
            for scenario_id in use_case.get("scenario_ids", [])
            if scenario_id in scenario_lookup
        ]
        realization_sections = []
        for realization in realizations_by_use_case.get(use_case_id, []):
            steps = "\n".join(
                f"{index}. {step}" for index, step in enumerate(realization.get("steps", []), 1)
            ) or "1. No realization steps documented."
            participants = ", ".join(realization.get("participant_names", [])) or "Unspecified"
            realization_sections.append(
                f"""#### {realization.get("use_case_name", use_case.get("name", "Unnamed Use Case"))}

- Participants: {participants}

##### Realization Steps

{steps}
"""
            )

        supporting_actors = _supporting_actor_names(use_case, actor_lookup)
        linked_requirements = [
            requirement_lookup[requirement_id]
            for requirement_id in use_case.get("other_requirement_ids", [])
            if requirement_id in requirement_lookup
        ]
        participating_objects = [
            participating_lookup[item_id]
            for item_id in use_case.get("participating_analysis_object_ids", [])
            if item_id in participating_lookup
        ]
        relevant_trace_links = _filter_trace_links(
            traceability.get("use_case_to_analysis", []),
            {use_case_id} | set(use_case.get("participating_analysis_object_ids", [])),
        )
        participating_block = (
            "\n".join(_component_line(item) for item in participating_objects)
            if participating_objects
            else "- None"
        )
        linked_requirement_lines = []
        for requirement in linked_requirements:
            line = (
                f"- `{requirement.get('id', 'requirement')}` "
                f"{requirement.get('statement', 'Unspecified requirement')}"
            )
            if trace := requirement.get("trace"):
                line = (
                    f"{line} [source: round {trace.get('source_round')} "
                    f"{trace.get('source_key')}]"
                )
            linked_requirement_lines.append(line)
        linked_requirements_block = "\n".join(linked_requirement_lines) or "- None"

        sections.append(
            f"""## {use_case.get("name", "Unnamed Use Case")}

- ID: `{use_case_id or "use-case"}`
- Primary Actor: {use_case.get("primary_actor", "Unspecified")}
- Supporting Actors: {", ".join(supporting_actors) or "None"}
- Priority: {use_case.get("priority", "") or "Unspecified"}
- Status: {use_case.get("status", "") or "Unspecified"}
- Complexity: {use_case.get("complexity", "unclassified")}
- Goal: {use_case.get("goal", "Unspecified")}
- Trigger: {use_case.get("trigger", "") or "Unspecified"}
- Source: round {use_case.get("trace", {}).get("source_round", "n/a")} {use_case.get("trace", {}).get("source_key", "")}

### Brief Description

{use_case.get("goal", "Unspecified")}

### Preconditions

{_bullet_list(use_case.get("preconditions", []))}

### Postconditions

{_bullet_list(use_case.get("postconditions", []))}

### Extension Points

{_bullet_list(use_case.get("extension_points", []))}

### Used Use Cases

{_bullet_list(_name_list_from_ids(use_case.get("used_use_case_ids", []), use_case_lookup))}

### Subordinate Use Cases

{_bullet_list(_name_list_from_ids(use_case.get("subordinate_use_case_ids", []), use_case_lookup))}

### Flow of Events

{"\n".join(f"{index}. {step}" for index, step in enumerate(use_case.get("main_success_scenario", []), 1)) or "1. No main success scenario documented."}

### Extensions

{_bullet_list(use_case.get("extensions", []))}

### Secondary Scenarios

{"\n\n".join(scenario_sections) or "No named scenarios documented."}

### User Interface

{_bullet_list(use_case.get("ui_notes", []))}

### View of Participating Classes

{participating_block}

### Sequence and Interaction Notes

{"\n\n".join(realization_sections) or "No interaction realization documented."}

### Linked Requirements

{linked_requirements_block}

### Other Artifacts

{_bullet_list(use_case.get("other_artifact_refs", []))}

{_traceability_section("Use-Case To Analysis Traceability", relevant_trace_links)}
"""
        )

    return f"""# Use-Case Documents

{"\n\n".join(sections)}
{_artifact_lineage_section(
    "Artifact Lineage",
    traceability.get("artifact_lineage", []),
    "use-case-documents.md",
)}
"""


def render_scenario_documents(model: dict[str, Any]) -> str:
    """Render the compiled template-driven scenario document artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Markdown content.
    """
    analysis_view = model.get("analysis_view", {})
    logical_view = model.get("logical_view", {})
    process_view = model.get("process_view", {})
    interaction_view = model.get("interaction_view", {})
    scenarios = analysis_view.get("scenario_objects", model.get("scenarios", []))
    use_cases = analysis_view.get("use_cases", model.get("use_cases", []))
    requirement_objects = analysis_view.get(
        "requirement_objects",
        model.get("requirements", {}).get("functional_objects", [])
        + model.get("requirements", {}).get("non_functional_objects", []),
    )
    domain_entity_objects = analysis_view.get(
        "domain_entity_objects",
        logical_view.get("domain_entity_objects", []),
    )
    relationship_objects = analysis_view.get(
        "relationship_objects",
        logical_view.get("relationship_objects", []),
    )
    state_entity_objects = analysis_view.get(
        "state_entity_objects",
        process_view.get("state_entity_objects", []),
    )
    traceability = model.get("traceability", {})

    if not scenarios:
        return "# Scenario Documents\n\nNo scenarios documented."

    use_case_lookup = _lookup_by_id(use_cases)
    requirement_lookup = _lookup_by_id(requirement_objects)
    participating_lookup = _lookup_by_id(
        domain_entity_objects + relationship_objects + state_entity_objects
    )
    realizations_by_use_case: dict[str, list[dict[str, Any]]] = {}
    for realization in interaction_view.get("realization_objects", []):
        use_case_id = str(realization.get("use_case_id", "")).strip()
        if use_case_id:
            realizations_by_use_case.setdefault(use_case_id, []).append(realization)

    sections = []
    for scenario in scenarios:
        parent_use_case = use_case_lookup.get(scenario.get("use_case_id", ""), {})
        parent_use_case_name = parent_use_case.get("name") or scenario.get("use_case_name", "Unspecified")
        participating_objects = [
            participating_lookup[item_id]
            for item_id in scenario.get("participating_analysis_object_ids", [])
            if item_id in participating_lookup
        ]
        linked_requirements = [
            requirement_lookup[requirement_id]
            for requirement_id in scenario.get("other_requirement_ids", [])
            if requirement_id in requirement_lookup
        ]
        participating_block = (
            "\n".join(_component_line(item) for item in participating_objects)
            if participating_objects
            else "- None"
        )
        linked_requirement_lines = []
        for requirement in linked_requirements:
            line = (
                f"- `{requirement.get('id', 'requirement')}` "
                f"{requirement.get('statement', 'Unspecified requirement')}"
            )
            if trace := requirement.get("trace"):
                line = (
                    f"{line} [source: round {trace.get('source_round')} "
                    f"{trace.get('source_key')}]"
                )
            linked_requirement_lines.append(line)
        linked_requirements_block = "\n".join(linked_requirement_lines) or "- None"

        sequence_sections = []
        for realization in realizations_by_use_case.get(scenario.get("use_case_id", ""), []):
            participants = ", ".join(realization.get("participant_names", [])) or "Unspecified"
            steps = "\n".join(
                f"{index}. {step}" for index, step in enumerate(realization.get("steps", []), 1)
            ) or "1. No realization steps documented."
            sequence_sections.append(
                f"""#### {realization.get("use_case_name", parent_use_case_name)}

- Participants: {participants}

##### Realization Steps

{steps}
"""
            )

        relevant_trace_links = _filter_trace_links(
            traceability.get("use_case_to_analysis", []),
            {scenario.get("use_case_id", "")}
            | set(scenario.get("participating_analysis_object_ids", [])),
        )
        flow = "\n".join(
            f"{index}. {step}" for index, step in enumerate(scenario.get("flow_of_events", []), 1)
        ) or "1. No scenario flow documented."

        sections.append(
            f"""## {scenario.get("name", "Unnamed Scenario")}

- ID: `{scenario.get("id", "scenario")}`
- Parent Use Case: {parent_use_case_name}
- Priority: {scenario.get("priority", "") or "Unspecified"}
- Status: {scenario.get("status", "") or "Unspecified"}
- Source: round {scenario.get("trace", {}).get("source_round", "n/a")} {scenario.get("trace", {}).get("source_key", "")}

### Brief Description

{scenario.get("summary", "Unspecified")}

### Flow of Events

{flow}

### Activity Notes

{_bullet_list(scenario.get("activity_notes", []))}

### Sequence Notes

{_bullet_list(scenario.get("sequence_notes", []))}

### Interaction Realizations

{"\n\n".join(sequence_sections) or "No interaction realization documented."}

### Participating Analysis Objects

{participating_block}

### Linked Requirements

{linked_requirements_block}

### Other Artifacts

{_bullet_list(scenario.get("other_artifact_refs", []))}

{_traceability_section("Scenario Supporting Traceability", relevant_trace_links)}
"""
        )

    return f"""# Scenario Documents

{"\n\n".join(sections)}
{_artifact_lineage_section(
    "Artifact Lineage",
    traceability.get("artifact_lineage", []),
    "scenario-documents.md",
)}
"""


def render_domain_model(model: dict[str, Any]) -> str:
    """Render the formal domain-model artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Markdown content.
    """
    project = model.get("project", {})
    analysis_view = model.get("analysis_view", {})
    logical_view = model.get("logical_view", {})
    traceability = model.get("traceability", {})
    domain_entity_objects = analysis_view.get(
        "domain_entity_objects",
        logical_view.get("domain_entity_objects", []),
    )
    relationship_objects = analysis_view.get(
        "relationship_objects",
        logical_view.get("relationship_objects", []),
    )
    business_rule_objects = analysis_view.get(
        "business_rule_objects",
        logical_view.get("business_rule_objects", []),
    )
    domain_entity_ids = {item.get("id", "") for item in domain_entity_objects if item.get("id")}

    return f"""# Domain Model

## Project

- Name: {project.get("name", "Unnamed Project")}
- Domain: {project.get("domain", "Unspecified")}

## Scope

{project.get("system_scope", "Unspecified")}
{_object_name_section(
    "Domain Entities",
    domain_entity_objects,
    logical_view.get("domain_entities", []),
)}
{_relationship_section(
    "Relationships",
    relationship_objects,
    logical_view.get("relationships", []),
)}
{_object_text_section(
    "Business Rules",
    business_rule_objects,
    logical_view.get("business_rules", []),
)}
{_traceability_section(
    "Use-Case To Domain Traceability",
    _filter_trace_links(traceability.get("use_case_to_analysis", []), domain_entity_ids),
)}
{_artifact_lineage_section(
    "Artifact Lineage",
    traceability.get("artifact_lineage", []),
    "domain-model.md",
)}
"""


def _mermaid_class_name(name: str, fallback_id: str) -> str:
    """Return a Mermaid-safe class identifier."""
    candidate = "".join(char if char.isalnum() else "_" for char in name.strip())
    if not candidate.strip("_"):
        candidate = "".join(char if char.isalnum() else "_" for char in fallback_id)
    if candidate and candidate[0].isdigit():
        candidate = f"Entity_{candidate}"
    return candidate or "Entity"


def _mermaid_relationship_line(
    relationship: dict[str, Any],
    entity_class_names: dict[str, str],
) -> str | None:
    """Render one Mermaid class relationship when source and target are known."""
    source_id = relationship.get("source_entity_id", "")
    target_id = relationship.get("target_entity_id", "")
    if not source_id or not target_id:
        return None

    source_class = entity_class_names.get(source_id)
    target_class = entity_class_names.get(target_id)
    if not source_class or not target_class:
        return None

    source_multiplicity = relationship.get("source_multiplicity", "") or '"1"'
    target_multiplicity = relationship.get("target_multiplicity", "") or '"1"'
    relationship_label = relationship.get("relationship_type", "") or relationship.get("description", "")
    relationship_label = relationship_label.replace('"', "'")
    return (
        f'{source_class} "{source_multiplicity}" --> "{target_multiplicity}" '
        f'{target_class} : {relationship_label}'
    )


def render_domain_mermaid(model: dict[str, Any]) -> str:
    """Render a Mermaid class diagram from the canonical domain model.

    Args:
        model: Canonical Rupify model.

    Returns:
        Mermaid classDiagram text.
    """
    analysis_view = model.get("analysis_view", {})
    logical_view = model.get("logical_view", {})
    domain_entity_objects = analysis_view.get(
        "domain_entity_objects",
        logical_view.get("domain_entity_objects", []),
    )
    relationship_objects = analysis_view.get(
        "relationship_objects",
        logical_view.get("relationship_objects", []),
    )

    lines = ["classDiagram"]
    entity_class_names: dict[str, str] = {}

    for entity in domain_entity_objects:
        entity_id = entity.get("id", "")
        class_name = _mermaid_class_name(entity.get("name", ""), entity_id)
        entity_class_names[entity_id] = class_name
        lines.append(f"class {class_name} {{")
        for attribute in entity.get("attributes", []):
            lines.append(f"  +{attribute}")
        lines.append("}")

    for relationship in relationship_objects:
        relationship_line = _mermaid_relationship_line(relationship, entity_class_names)
        if relationship_line:
            lines.append(relationship_line)

    return "\n".join(lines)


def render_interaction_model(model: dict[str, Any]) -> str:
    """Render the formal interaction-model artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Markdown content.
    """
    project = model.get("project", {})
    interaction_view = model.get("interaction_view", {})
    traceability = model.get("traceability", {})
    realization_objects = interaction_view.get("realization_objects", [])
    message_objects = interaction_view.get("message_objects", [])

    realizations = []
    for realization in realization_objects:
        steps = "\n".join(
            f"{index}. {step}" for index, step in enumerate(realization.get("steps", []), 1)
        ) or "1. No interaction steps documented."
        participant_names = ", ".join(realization.get("participant_names", [])) or "Unspecified"
        line = f"""### {realization.get("use_case_name", "Unnamed Use Case")}

- Realization ID: `{realization.get("id", "interaction-realization")}`
- Use case ID: `{realization.get("use_case_id", "use-case")}`
- Participants: {participant_names}

#### Steps

{steps}
"""
        if trace := realization.get("trace"):
            line = (
                f"{line}\n- Source: round {trace.get('source_round', 'n/a')} "
                f"{trace.get('source_key', '')}"
            )
        realizations.append(line)

    message_lines = []
    for message in message_objects:
        line = (
            f"- `{message.get('id', 'interaction-message')}` "
            f"{message.get('source_name', 'Unknown')} -> {message.get('target_name', 'Unknown')}"
        )
        if message.get("interaction_verb"):
            line = f"{line} ({message['interaction_verb']})"
        if message.get("description"):
            line = f"{line}: {message['description']}"
        if trace := message.get("trace"):
            line = (
                f"{line} [source: round {trace.get('source_round')} "
                f"{trace.get('source_key')}]"
            )
        message_lines.append(line)

    return f"""# Interaction Model

## Project

- Name: {project.get("name", "Unnamed Project")}
- Domain: {project.get("domain", "Unspecified")}

## Scope

{project.get("system_scope", "Unspecified")}

## Use-Case Realizations

{"\n\n".join(realizations) or "No interaction realizations documented."}

## Message Flows

{"\n".join(message_lines) or "- None"}
{_artifact_lineage_section(
    "Artifact Lineage",
    traceability.get("artifact_lineage", []),
    "interaction-model.md",
)}
"""


def render_interaction_mermaid(model: dict[str, Any]) -> str:
    """Render a Mermaid sequence diagram from the canonical interaction model.

    Args:
        model: Canonical Rupify model.

    Returns:
        Mermaid sequenceDiagram text.
    """
    interaction_view = model.get("interaction_view", {})
    realization_objects = interaction_view.get("realization_objects", [])
    message_objects = interaction_view.get("message_objects", [])

    lines = ["sequenceDiagram"]
    participant_names: list[str] = []

    def add_participant(name: str) -> None:
        if name and name not in participant_names:
            participant_names.append(name)

    for realization in realization_objects:
        for participant_name in realization.get("participant_names", []):
            add_participant(participant_name)
    for message in message_objects:
        add_participant(message.get("source_name", ""))
        add_participant(message.get("target_name", ""))

    for participant_name in participant_names:
        safe_name = _mermaid_class_name(participant_name, participant_name)
        lines.append(f'participant {safe_name} as "{participant_name}"')

    for realization in realization_objects:
        participant_ids = [
            _mermaid_class_name(name, name) for name in realization.get("participant_names", [])
        ]
        if participant_ids:
            lines.append(
                f"Note over {', '.join(participant_ids)}: "
                f"{realization.get('use_case_name', 'Unnamed Use Case')}"
            )
        if len(participant_ids) >= 2:
            source = participant_ids[0]
            target = participant_ids[1]
            for step in realization.get("steps", []):
                lines.append(f"{source}->>{target}: {step}")
        elif len(participant_ids) == 1:
            participant = participant_ids[0]
            for step in realization.get("steps", []):
                lines.append(f"{participant}->>{participant}: {step}")

    for message in message_objects:
        source_name = message.get("source_name", "")
        target_name = message.get("target_name", "")
        if not source_name or not target_name:
            continue
        source = _mermaid_class_name(source_name, source_name)
        target = _mermaid_class_name(target_name, target_name)
        description = (
            message.get("description", "")
            or message.get("interaction_verb", "")
            or "message"
        )
        lines.append(f"{source}->>{target}: {description}")

    return "\n".join(lines)


def render_deployment_model(model: dict[str, Any]) -> str:
    """Render the formal deployment-model artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Markdown content.
    """
    project = model.get("project", {})
    design_view = model.get("design_view", {})
    architecture_view = model.get("architecture_view", {})
    traceability = model.get("traceability", {})
    component_objects = design_view.get(
        "component_objects",
        architecture_view.get("component_objects", []),
    )
    interface_objects = design_view.get(
        "interface_objects",
        architecture_view.get("interface_objects", []),
    )
    runtime_boundary_objects = design_view.get(
        "runtime_boundary_objects",
        architecture_view.get("runtime_boundary_objects", []),
    )

    return f"""# Deployment Model

## Project

- Name: {project.get("name", "Unnamed Project")}
- Domain: {project.get("domain", "Unspecified")}

## Scope

{project.get("system_scope", "Unspecified")}
{_object_name_section(
    "Components",
    component_objects,
    architecture_view.get("components_and_services", []),
)}
{_object_text_section(
    "Interfaces and Integrations",
    interface_objects,
    architecture_view.get("interfaces_and_integrations", []),
)}
{_object_text_section(
    "Runtime Boundaries",
    runtime_boundary_objects,
    architecture_view.get("runtime_boundaries", []),
)}
{_artifact_lineage_section(
    "Artifact Lineage",
    traceability.get("artifact_lineage", []),
    "deployment-model.md",
)}
"""


def render_deployment_mermaid(model: dict[str, Any]) -> str:
    """Render a Mermaid deployment/architecture diagram from the canonical design model.

    Args:
        model: Canonical Rupify model.

    Returns:
        Mermaid flowchart text.
    """
    design_view = model.get("design_view", {})
    architecture_view = model.get("architecture_view", {})
    component_objects = design_view.get(
        "component_objects",
        architecture_view.get("component_objects", []),
    )
    interface_objects = design_view.get(
        "interface_objects",
        architecture_view.get("interface_objects", []),
    )
    runtime_boundary_objects = design_view.get(
        "runtime_boundary_objects",
        architecture_view.get("runtime_boundary_objects", []),
    )

    lines = ["flowchart LR"]
    component_ids: dict[str, str] = {}

    for component in component_objects:
        component_name = component.get("name", "Component")
        component_id = _mermaid_class_name(component_name, component.get("id", "component"))
        component_ids[component_name] = component_id
        lines.append(f'{component_id}["{component_name}"]')

    for interface in interface_objects:
        source_name = interface.get("source_name", "") or interface.get("source_component_name", "")
        target_name = interface.get("target_name", "") or interface.get("target_component_name", "")
        if not source_name or not target_name:
            continue
        source_id = component_ids.get(source_name, _mermaid_class_name(source_name, source_name))
        target_id = component_ids.get(target_name, _mermaid_class_name(target_name, target_name))
        description = interface.get("description", "") or "integrates with"
        lines.append(f'{source_id} -->|"{description}"| {target_id}')

    for index, runtime_boundary in enumerate(runtime_boundary_objects, 1):
        boundary_id = f"RuntimeBoundary_{index}"
        description = runtime_boundary.get("description", "") or runtime_boundary.get("text", "")
        lines.append(f'{boundary_id}["{description or "Runtime boundary"}"]')

    return "\n".join(lines)


def render_state_model(model: dict[str, Any]) -> str:
    """Render the formal state-model artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Markdown content.
    """
    project = model.get("project", {})
    analysis_view = model.get("analysis_view", {})
    process_view = model.get("process_view", {})
    design_view = model.get("design_view", {})
    traceability = model.get("traceability", {})
    state_entity_objects = analysis_view.get(
        "state_entity_objects",
        process_view.get("state_entity_objects", []),
    )
    state_transition_objects = analysis_view.get(
        "state_transition_objects",
        process_view.get("state_transition_objects", []),
    )
    trigger_objects = analysis_view.get(
        "trigger_objects",
        process_view.get("trigger_objects", []),
    )
    component_objects = design_view.get("component_objects", [])
    state_entity_ids = {item.get("id", "") for item in state_entity_objects if item.get("id")}
    component_ids = {item.get("id", "") for item in component_objects if item.get("id")}

    return f"""# State Model

## Project

- Name: {project.get("name", "Unnamed Project")}
- Domain: {project.get("domain", "Unspecified")}

## Scope

{project.get("system_scope", "Unspecified")}
{_object_name_section(
    "State Entities",
    state_entity_objects,
    process_view.get("state_entities", []),
)}
{_state_transition_section(
    "State Transitions",
    state_transition_objects,
    process_view.get("states_and_transitions", []),
)}
{_trigger_section(
    "Triggers and Approvals",
    trigger_objects,
    process_view.get("triggers_and_approvals", []),
)}
{_traceability_section(
    "Use-Case To State Traceability",
    _filter_trace_links(traceability.get("use_case_to_analysis", []), state_entity_ids),
)}
{_traceability_section(
    "State To Design Traceability",
    _filter_trace_links(
        traceability.get("analysis_to_design", []),
        state_entity_ids | component_ids,
    ),
)}
{_artifact_lineage_section(
    "Artifact Lineage",
    traceability.get("artifact_lineage", []),
    "state-model.md",
)}
"""


def render_state_mermaid(model: dict[str, Any]) -> str:
    """Render a Mermaid state diagram from the canonical state model.

    Args:
        model: Canonical Rupify model.

    Returns:
        Mermaid stateDiagram-v2 text.
    """
    analysis_view = model.get("analysis_view", {})
    process_view = model.get("process_view", {})
    state_entity_objects = analysis_view.get(
        "state_entity_objects",
        process_view.get("state_entity_objects", []),
    )
    state_transition_objects = analysis_view.get(
        "state_transition_objects",
        process_view.get("state_transition_objects", []),
    )

    lines = ["stateDiagram-v2"]
    if not state_transition_objects and not state_entity_objects:
        return "\n".join(lines)

    if len(state_entity_objects) == 1:
        state_entity = state_entity_objects[0]
        entity_name = state_entity.get("name", "State Entity")
        lines.append(f'state "{entity_name}" as lifecycle {{')

        for state_name in state_entity.get("states", []):
            safe_state = _mermaid_class_name(state_name, state_name)
            lines.append(f'  state "{state_name}" as {safe_state}')

        for transition in state_transition_objects:
            from_state = transition.get("from_state", "")
            to_state = transition.get("to_state", "")
            if not from_state or not to_state:
                continue

            safe_from = _mermaid_class_name(from_state, from_state)
            safe_to = _mermaid_class_name(to_state, to_state)
            label_bits = []
            if transition.get("trigger"):
                label_bits.append(transition["trigger"])
            if transition.get("constraint"):
                label_bits.append(transition["constraint"])
            if transition.get("is_exception_flow"):
                label_bits.append("exception")
            if transition.get("is_terminal_transition"):
                label_bits.append("terminal")

            if label_bits:
                lines.append(f"  {safe_from} --> {safe_to} : {' | '.join(label_bits)}")
            else:
                lines.append(f"  {safe_from} --> {safe_to}")

        lines.append("}")
        return "\n".join(lines)

    for transition in state_transition_objects:
        from_state = transition.get("from_state", "")
        to_state = transition.get("to_state", "")
        if not from_state or not to_state:
            continue

        safe_from = _mermaid_class_name(from_state, from_state)
        safe_to = _mermaid_class_name(to_state, to_state)
        lines.append(f'state "{from_state}" as {safe_from}')
        lines.append(f'state "{to_state}" as {safe_to}')

        label_bits = []
        if transition.get("state_entity_name"):
            label_bits.append(transition["state_entity_name"])
        if transition.get("trigger"):
            label_bits.append(transition["trigger"])
        if transition.get("constraint"):
            label_bits.append(transition["constraint"])
        if transition.get("is_exception_flow"):
            label_bits.append("exception")
        if transition.get("is_terminal_transition"):
            label_bits.append("terminal")

        if label_bits:
            lines.append(f"{safe_from} --> {safe_to} : {' | '.join(label_bits)}")
        else:
            lines.append(f"{safe_from} --> {safe_to}")

    return "\n".join(lines)


def render_all(model: dict[str, Any]) -> dict[str, str]:
    """Render all primary artifacts for a model.

    Args:
        model: Canonical Rupify model.

    Returns:
        Mapping of filename to rendered content.
    """
    outputs = render_formal_artifacts(model)
    outputs.update(render_ucp_artifact(model))
    return outputs


def render_formal_artifacts(model: dict[str, Any]) -> dict[str, str]:
    """Render the formal artifact family without UCP output.

    Args:
        model: Canonical Rupify model.

    Returns:
        Mapping of filename to rendered content.
    """
    return {
        "system-document.md": render_system_document(model),
        "requirements-spec.md": render_requirements_spec(model),
        "use-case-model.md": render_use_case_model(model),
        "use-case-documents.md": render_use_case_documents(model),
        "scenario-documents.md": render_scenario_documents(model),
        "domain-model.md": render_domain_model(model),
        "interaction-model.md": render_interaction_model(model),
        "deployment-model.md": render_deployment_model(model),
        "state-model.md": render_state_model(model),
    }


def render_ucp_artifact(model: dict[str, Any]) -> dict[str, str]:
    """Render only the strict UCP estimate artifact.

    Args:
        model: Canonical Rupify model.

    Returns:
        Mapping of filename to rendered content.
    """
    ucp_results = calculate_ucp(model)
    return {
        "ucp-estimate.md": render_ucp_markdown(model, ucp_results),
    }


def render_artifact_family(model: dict[str, Any], artifact_family: str) -> dict[str, str]:
    """Render one explicit artifact family.

    Args:
        model: Canonical Rupify model.
        artifact_family: One of `all`, `formal`, `ucp`, `domain-mermaid`, `state-mermaid`, `interaction-mermaid`, or `deployment-mermaid`.

    Returns:
        Mapping of filename to rendered content.

    Raises:
        ValueError: If the requested family is unsupported.
    """
    if artifact_family == "all":
        return render_all(model)
    if artifact_family == "formal":
        return render_formal_artifacts(model)
    if artifact_family == "ucp":
        return render_ucp_artifact(model)
    if artifact_family == "domain-mermaid":
        return {
            "domain-model.mmd": render_domain_mermaid(model),
        }
    if artifact_family == "state-mermaid":
        return {
            "state-model.mmd": render_state_mermaid(model),
        }
    if artifact_family == "interaction-mermaid":
        return {
            "interaction-model.mmd": render_interaction_mermaid(model),
        }
    if artifact_family == "deployment-mermaid":
        return {
            "deployment-model.mmd": render_deployment_mermaid(model),
        }
    raise ValueError(f"Unsupported artifact family '{artifact_family}'.")
