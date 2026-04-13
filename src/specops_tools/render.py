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


def render_requirements_spec(model: dict[str, Any]) -> str:
    """Render the requirements specification artifact.

    Args:
        model: Canonical SpecOps model.

    Returns:
        Markdown content.
    """
    project = model.get("project", {})
    requirements = model.get("requirements", {})
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
        actor_lines.append(
            f"- `{actor.get('id', 'actor')}` {actor.get('name', 'Unnamed')} "
            f"({actor.get('type', 'unspecified')}, {actor.get('complexity', 'unclassified')}): "
            f"{actor.get('description', 'No description')}"
        )

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

#### Main Success Scenario

{main_flow}

#### Extensions

{extensions}
"""
        )

    actor_block = "\n".join(actor_lines) or "- None"
    use_case_block = "\n".join(use_case_sections) or "No use cases documented."

    return f"""# Use-Case Model

## Actors

{actor_block}

## Use Cases

{use_case_block}
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
