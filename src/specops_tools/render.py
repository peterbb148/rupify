"""Markdown rendering for SpecOps artifacts."""

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
            line = f"- `{item.get('id', 'item')}` {item.get('text', '')}"
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


def render_requirements_spec(model: dict[str, Any]) -> str:
    """Render the requirements specification artifact.

    Args:
        model: Canonical SpecOps model.

    Returns:
        Markdown content.
    """
    project = model.get("project", {})
    requirements = model.get("requirements", {})
    logical_view = model.get("logical_view", {})
    process_view = model.get("process_view", {})
    architecture_view = model.get("architecture_view", {})
    traceability = model.get("traceability", {})
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
    logical_view.get("domain_entity_objects", []),
    logical_view.get("domain_entities", []),
)}
{_object_text_section(
    "Relationships",
    logical_view.get("relationship_objects", []),
    logical_view.get("relationships", []),
)}
{_object_text_section(
    "Business Rules",
    logical_view.get("business_rule_objects", []),
    logical_view.get("business_rules", []),
)}
{_object_name_section(
    "Process View",
    process_view.get("state_entity_objects", []),
    process_view.get("state_entities", []),
)}
{_object_text_section(
    "States and Transitions",
    process_view.get("state_transition_objects", []),
    process_view.get("states_and_transitions", []),
)}
{_object_text_section(
    "Triggers and Approvals",
    process_view.get("trigger_objects", []),
    process_view.get("triggers_and_approvals", []),
)}
{_object_name_section(
    "Architecture View",
    architecture_view.get("component_objects", []),
    architecture_view.get("components_and_services", []),
)}
{_object_text_section(
    "Interfaces and Integrations",
    architecture_view.get("interface_objects", []),
    architecture_view.get("interfaces_and_integrations", []),
)}
{_object_text_section(
    "Runtime Boundaries",
    architecture_view.get("runtime_boundary_objects", []),
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
        model: Canonical SpecOps model.

    Returns:
        Markdown content.
    """
    actor_lines = []
    for actor in model.get("actors", []):
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
    for use_case in model.get("use_cases", []):
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

    return f"""# Use-Case Model

## Actors

{actor_block}

## Use Cases

{use_case_block}
{_object_text_section(
    "States and Transitions",
    process_view.get("state_transition_objects", []),
    process_view.get("states_and_transitions", []),
)}
{_object_text_section(
    "Triggers and Approvals",
    process_view.get("trigger_objects", []),
    process_view.get("triggers_and_approvals", []),
)}
{_object_text_section(
    "Interfaces and Integrations",
    architecture_view.get("interface_objects", []),
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


def render_all(model: dict[str, Any]) -> dict[str, str]:
    """Render all primary artifacts for a model.

    Args:
        model: Canonical SpecOps model.

    Returns:
        Mapping of filename to rendered content.
    """
    ucp_results = calculate_ucp(model)
    return {
        "requirements-spec.md": render_requirements_spec(model),
        "use-case-model.md": render_use_case_model(model),
        "ucp-estimate.md": render_ucp_markdown(model, ucp_results),
    }
