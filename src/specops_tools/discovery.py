"""Deterministic normalization from interview replay data into a SpecOps model."""

from __future__ import annotations

from typing import Any

TECHNICAL_FACTOR_ALIASES = {
    "distributed system": "distributed_system",
    "response time": "response_time",
    "end-user efficiency": "end_user_efficiency",
    "end user efficiency": "end_user_efficiency",
    "complex internal processing": "complex_internal_processing",
    "reusability": "reusable_code",
    "reusable code": "reusable_code",
    "ease of installation": "easy_to_install",
    "easy to install": "easy_to_install",
    "ease of use": "easy_to_use",
    "easy to use": "easy_to_use",
    "portability": "portability",
    "ease of change": "easy_to_change",
    "easy to change": "easy_to_change",
    "concurrency": "concurrency",
    "security": "special_security",
    "special security": "special_security",
    "third-party access": "third_party_access",
    "third party access": "third_party_access",
    "special user training": "special_user_training",
}

ENVIRONMENTAL_FACTOR_ALIASES = {
    "team familiarity": "familiar_with_process",
    "familiar with process": "familiar_with_process",
    "application experience": "application_experience",
    "architecture experience": "object_oriented_experience",
    "object oriented experience": "object_oriented_experience",
    "analyst capability": "lead_analyst_capability",
    "lead analyst capability": "lead_analyst_capability",
    "motivation": "motivation",
    "requirements stability": "stable_requirements",
    "stable requirements": "stable_requirements",
    "part-time staffing": "part_time_staff",
    "part time staffing": "part_time_staff",
    "platform difficulty": "difficult_programming_language",
    "difficult programming language": "difficult_programming_language",
}


def _slugify(value: str) -> str:
    """Create a stable slug-like identifier."""
    cleaned = []
    for char in value.strip().lower():
        if char.isalnum():
            cleaned.append(char)
        else:
            cleaned.append("-")
    result = "".join(cleaned).strip("-")
    while "--" in result:
        result = result.replace("--", "-")
    return result or "item"


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


def _string_items_to_named_items(items: list[str], kind: str) -> list[dict[str, str]]:
    """Convert string items into simple structured objects."""
    return [
        {
            "id": f"{kind}-{_slugify(item)}",
            "name": item,
        }
        for item in items
    ]


def _string_items_to_described_items(items: list[str], kind: str) -> list[dict[str, str]]:
    """Convert string items into structured objects with text descriptions."""
    return [
        {
            "id": f"{kind}-{index}",
            "text": item,
        }
        for index, item in enumerate(items, 1)
    ]


def _best_name_match(name: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find the best deterministic name match for a complexity entry."""
    target_slug = _slugify(name)
    for candidate in candidates:
        if _slugify(candidate.get("name", "")) == target_slug:
            return candidate

    target_tokens = set(target_slug.split("-"))
    best_match = None
    best_score = 0
    for candidate in candidates:
        candidate_tokens = set(_slugify(candidate.get("name", "")).split("-"))
        score = len(target_tokens & candidate_tokens)
        if score > best_score and score >= 2:
            best_score = score
            best_match = candidate
    return best_match


def _apply_complexity_answers(items: list[dict[str, Any]], answers: list[str]) -> None:
    """Apply `Name: complexity` answers to normalized objects in place."""
    for answer in answers:
        if ":" not in answer:
            continue
        name, complexity = answer.split(":", 1)
        match = _best_name_match(name.strip(), items)
        if match is not None:
            match["complexity"] = complexity.strip().lower()


def _normalize_factor_map(
    answers: dict[str, Any],
    aliases: dict[str, str],
) -> dict[str, int]:
    """Normalize parsed factor answers using alias maps."""
    normalized = {}
    for raw_key, value in answers.items():
        canonical_key = aliases.get(raw_key.replace("_", " ").lower())
        if canonical_key is None:
            continue
        try:
            normalized[canonical_key] = int(str(value).strip())
        except ValueError:
            continue
    return normalized


def _normalize_actors(items: list[str]) -> list[dict[str, str]]:
    """Convert actor strings into simple canonical actor objects."""
    actors = []
    for item in items:
        normalized_name = item.strip()
        actor_type = "system" if any(
            marker in normalized_name.lower()
            for marker in (
                "system",
                "api",
                "service",
                "integration",
                "consumer",
                "gateway",
                "platform",
            )
        ) else "human"
        actors.append(
            {
                "id": _slugify(normalized_name),
                "name": normalized_name,
                "type": actor_type,
                "description": "",
                "complexity": "unclassified",
            }
        )
    return actors


def _normalize_use_cases(items: list[str]) -> list[dict[str, Any]]:
    """Convert use-case strings into simple canonical use-case objects."""
    use_cases = []
    for item in items:
        normalized_name = item.strip()
        use_cases.append(
            {
                "id": _slugify(normalized_name),
                "name": normalized_name,
                "primary_actor": "Unspecified",
                "goal": normalized_name,
                "complexity": "unclassified",
                "main_success_scenario": [],
                "extensions": [],
            }
        )
    return use_cases


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
    round_7 = merged_answers.get("round_7", {})
    round_8 = merged_answers.get("round_8", {})
    round_9 = merged_answers.get("round_9", {})
    round_10 = merged_answers.get("round_10", {})
    round_11 = merged_answers.get("round_11", {})
    actors = _ensure_list(round_3.get("actors"))
    use_cases = _ensure_list(round_3.get("use_cases"))

    functional_requirements = []
    if workflow_scope := _text_or_empty(round_4.get("workflow_scope")):
        functional_requirements.append(workflow_scope)
    if integrations := _text_or_empty(round_3.get("integrations")):
        functional_requirements.append(integrations)

    constraints = _ensure_list(round_2.get("constraints"))
    non_functional = _ensure_list(round_4.get("non_functional_requirements"))
    if constraints:
        non_functional = constraints + non_functional

    domain_entities = _ensure_list(round_5.get("domain_entities"))
    relationships = _ensure_list(round_5.get("relationships"))
    business_rules = _ensure_list(round_5.get("business_rules"))
    state_entities = _ensure_list(round_6.get("state_entities"))
    states_and_transitions = _ensure_list(round_6.get("states_and_transitions"))
    triggers_and_approvals = _ensure_list(round_6.get("triggers_and_approvals"))
    components_and_services = _ensure_list(round_7.get("components_and_services"))
    interfaces_and_integrations = _ensure_list(round_7.get("interfaces_and_integrations"))
    runtime_boundaries = _ensure_list(round_7.get("runtime_boundaries"))
    normalized_actors = _normalize_actors(actors)
    normalized_use_cases = _normalize_use_cases(use_cases)
    _apply_complexity_answers(normalized_actors, _ensure_list(round_8.get("actor_complexity")))
    _apply_complexity_answers(normalized_use_cases, _ensure_list(round_9.get("use_case_complexity")))
    technical_factors = _normalize_factor_map(round_10, TECHNICAL_FACTOR_ALIASES)
    environmental_factors = _normalize_factor_map(round_11, ENVIRONMENTAL_FACTOR_ALIASES)

    return {
        "project": {
            "name": _text_or_empty(round_1.get("idea")) or "Unnamed Project",
            "domain": "Unspecified",
            "problem_statement": _text_or_empty(round_1.get("problem")) or "Unspecified",
            "system_scope": _text_or_empty(round_1.get("in_scope")) or "Unspecified",
        },
        "business_goals": _ensure_list(round_2.get("outcomes")),
        "success_criteria": _ensure_list(round_2.get("success_criteria")),
        "actors": normalized_actors,
        "use_cases": normalized_use_cases,
        "requirements": {
            "functional": functional_requirements,
            "non_functional": non_functional,
        },
        "logical_view": {
            "domain_entities": domain_entities,
            "domain_entity_objects": _string_items_to_named_items(domain_entities, "entity"),
            "relationships": relationships,
            "relationship_objects": _string_items_to_described_items(relationships, "relationship"),
            "business_rules": business_rules,
            "business_rule_objects": _string_items_to_described_items(
                business_rules,
                "business-rule",
            ),
        },
        "process_view": {
            "state_entities": state_entities,
            "state_entity_objects": _string_items_to_named_items(state_entities, "state-entity"),
            "states_and_transitions": states_and_transitions,
            "state_transition_objects": _string_items_to_described_items(
                states_and_transitions,
                "state-transition",
            ),
            "triggers_and_approvals": triggers_and_approvals,
            "trigger_objects": _string_items_to_described_items(
                triggers_and_approvals,
                "trigger",
            ),
        },
        "architecture_view": {
            "components_and_services": components_and_services,
            "component_objects": _string_items_to_named_items(
                components_and_services,
                "component",
            ),
            "interfaces_and_integrations": interfaces_and_integrations,
            "interface_objects": _string_items_to_described_items(
                interfaces_and_integrations,
                "interface",
            ),
            "runtime_boundaries": runtime_boundaries,
            "runtime_boundary_objects": _string_items_to_described_items(
                runtime_boundaries,
                "runtime-boundary",
            ),
        },
        "metadata_fields": _ensure_list(round_4.get("metadata_fields")),
        "assumptions": [],
        "open_questions": [],
        "ucp": {
            "technical_factors": technical_factors,
            "environmental_factors": environmental_factors,
            "productivity_hours_per_ucp": 20,
        },
        "future_placeholders": {
            "uml": [],
            "formal_specification": [],
        },
    }
