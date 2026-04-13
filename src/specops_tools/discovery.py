"""Deterministic normalization from interview replay data into a SpecOps model."""

from __future__ import annotations

from typing import Any


def _ensure_list(value: Any) -> list[str]:
    """Normalize a scalar or list answer into a clean string list."""
    def _clean(item: Any) -> str:
        text = str(item).strip()
        if text.startswith("- "):
            text = text[2:].strip()
        return text

    if value is None:
        return []
    if isinstance(value, list):
        return [_clean(item) for item in value if _clean(item)]
    text = _clean(value)
    return [text] if text else []


def _text_or_empty(value: Any) -> str:
    """Normalize a scalar answer into a string."""
    if value is None:
        return ""
    return str(value).strip()


def normalize_replay_to_model(replay: dict[str, Any]) -> dict[str, Any]:
    """Normalize replay output into a canonical SpecOps model shape.

    This keeps the transformation deterministic and conservative. It maps interview answers into
    stable model sections without inventing actors, use cases, or requirements that were not stated.

    Args:
        replay: Output from `replay_session()` or `replay_session_with_updates()`.

    Returns:
        Canonical model dictionary.
    """
    merged_answers = replay.get("merged_answers", {})
    round_1 = merged_answers.get("round_1", {})
    round_2 = merged_answers.get("round_2", {})
    round_3 = merged_answers.get("round_3", {})
    round_4 = merged_answers.get("round_4", {})
    round_5 = merged_answers.get("round_5", {})
    round_6 = merged_answers.get("round_6", {})

    functional_requirements = []
    if workflow_scope := _text_or_empty(round_4.get("workflow_scope")):
        functional_requirements.append(workflow_scope)
    if integrations := _text_or_empty(round_3.get("integrations")):
        functional_requirements.append(integrations)

    constraints = _ensure_list(round_2.get("constraints"))
    non_functional = _ensure_list(round_4.get("non_functional_requirements"))
    if constraints:
        non_functional = constraints + non_functional

    return {
        "project": {
            "name": _text_or_empty(round_1.get("idea")) or "Unnamed Project",
            "domain": "Unspecified",
            "problem_statement": _text_or_empty(round_1.get("problem")) or "Unspecified",
            "system_scope": _text_or_empty(round_1.get("in_scope")) or "Unspecified",
        },
        "business_goals": _ensure_list(round_2.get("outcomes")),
        "success_criteria": _ensure_list(round_2.get("success_criteria")),
        "actors": [],
        "use_cases": [],
        "requirements": {
            "functional": functional_requirements,
            "non_functional": non_functional,
        },
        "logical_view": {
            "domain_entities": _ensure_list(round_5.get("domain_entities")),
            "relationships": _ensure_list(round_5.get("relationships")),
            "business_rules": _ensure_list(round_5.get("business_rules")),
        },
        "process_view": {
            "state_entities": _ensure_list(round_6.get("state_entities")),
            "states_and_transitions": _ensure_list(round_6.get("states_and_transitions")),
            "triggers_and_approvals": _ensure_list(round_6.get("triggers_and_approvals")),
        },
        "architecture_view": {
            "components_and_services": _ensure_list(
                merged_answers.get("round_7", {}).get("components_and_services")
            ),
            "interfaces_and_integrations": _ensure_list(
                merged_answers.get("round_7", {}).get("interfaces_and_integrations")
            ),
            "runtime_boundaries": _ensure_list(
                merged_answers.get("round_7", {}).get("runtime_boundaries")
            ),
        },
        "metadata_fields": _ensure_list(round_4.get("metadata_fields")),
        "assumptions": [],
        "open_questions": [],
        "ucp": {
            "technical_factors": {},
            "environmental_factors": {},
            "productivity_hours_per_ucp": 20,
        },
        "future_placeholders": {
            "uml": [],
            "formal_specification": [],
        },
    }
