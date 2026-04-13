"""Deterministic normalization from interview replay data into a SpecOps model."""

from __future__ import annotations

import re
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


def _match_slug(value: str) -> str:
    """Create a looser deterministic slug for reference matching."""
    tokens = [token for token in _slugify(value).split("-") if token not in {"a", "an", "the"}]
    normalized_tokens = []
    for token in tokens:
        if len(token) > 3 and token.endswith("s"):
            normalized_tokens.append(token[:-1])
        else:
            normalized_tokens.append(token)
    return "-".join(normalized_tokens)


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
            "trace": {},
        }
        for item in items
    ]


def _string_items_to_described_items(items: list[str], kind: str) -> list[dict[str, str]]:
    """Convert string items into structured objects with text descriptions."""
    return [
        {
            "id": f"{kind}-{index}",
            "text": item,
            "trace": {},
        }
        for index, item in enumerate(items, 1)
    ]


def _normalize_domain_entities(items: list[str]) -> list[dict[str, Any]]:
    """Convert domain entity strings into explicit analysis objects."""
    entities = []
    for item in items:
        normalized_name = item.strip()
        entities.append(
            {
                "id": f"entity-{_slugify(normalized_name)}",
                "name": normalized_name,
                "entity_type": "domain_entity",
                "description": "",
                "attributes": [],
                "responsibilities": [],
                "trace": {},
            }
        )
    return entities


def _normalize_relationships(
    items: list[str],
    entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Convert relationship strings into structured relationship objects."""
    relationships = []
    for index, item in enumerate(items, 1):
        text = item.strip()
        source_name = ""
        target_name = ""
        relationship_type = ""
        normalized = text.lower()

        if " has many " in normalized:
            source_name, target_name = re.split(r"\bhas many\b", text, maxsplit=1, flags=re.IGNORECASE)
            relationship_type = "has_many"
        elif " has a " in normalized:
            source_name, target_name = re.split(r"\bhas a\b", text, maxsplit=1, flags=re.IGNORECASE)
            relationship_type = "has_one"
        elif " has an " in normalized:
            source_name, target_name = re.split(r"\bhas an\b", text, maxsplit=1, flags=re.IGNORECASE)
            relationship_type = "has_one"
        elif " belongs to " in normalized:
            source_name, target_name = re.split(
                r"\bbelongs to\b",
                text,
                maxsplit=1,
                flags=re.IGNORECASE,
            )
            relationship_type = "belongs_to"

        source_name = source_name.strip()
        target_name = target_name.strip()
        source_match = _best_name_match(source_name, entities) if source_name else None
        target_match = _best_name_match(target_name, entities) if target_name else None
        relationships.append(
            {
                "id": f"relationship-{index}",
                "description": text,
                "relationship_type": relationship_type,
                "source_name": source_name,
                "source_entity_id": source_match["id"] if source_match else "",
                "target_name": target_name,
                "target_entity_id": target_match["id"] if target_match else "",
                "trace": {},
            }
        )
    return relationships


def _normalize_business_rules(items: list[str]) -> list[dict[str, Any]]:
    """Convert business-rule strings into explicit rule objects."""
    rules = []
    for index, item in enumerate(items, 1):
        text = item.strip()
        normalized = text.lower()
        scope = ""
        if " requires " in normalized:
            scope = text.split(" requires ", 1)[0].strip()
        elif " must " in normalized:
            scope = text.split(" must ", 1)[0].strip()
        rules.append(
            {
                "id": f"business-rule-{index}",
                "name": f"Rule {index}",
                "rule_text": text,
                "scope": scope,
                "trace": {},
            }
        )
    return rules


def _normalize_state_entities(items: list[str]) -> list[dict[str, Any]]:
    """Convert state-entity strings into explicit lifecycle owner objects."""
    entities = []
    for item in items:
        normalized_name = item.strip()
        entities.append(
            {
                "id": f"state-entity-{_slugify(normalized_name)}",
                "name": normalized_name,
                "entity_type": "stateful_entity",
                "description": "",
                "states": [],
                "trace": {},
            }
        )
    return entities


def _normalize_state_transitions(items: list[str]) -> list[dict[str, Any]]:
    """Convert transition strings into structured transition objects."""
    transitions = []
    for item in items:
        text = item.strip()
        if "->" not in text:
            transitions.append(
                {
                    "id": f"state-transition-{len(transitions) + 1}",
                    "description": text,
                    "state_entity_id": "",
                    "state_entity_name": "",
                    "from_state": "",
                    "to_state": "",
                    "trigger": "",
                    "trace": {},
                }
            )
            continue

        states = [part.strip() for part in text.split("->") if part.strip()]
        for source_state, target_state in zip(states, states[1:]):
            transitions.append(
                {
                    "id": f"state-transition-{len(transitions) + 1}",
                    "description": text,
                    "state_entity_id": "",
                    "state_entity_name": "",
                    "from_state": source_state,
                    "to_state": target_state,
                    "trigger": "",
                    "trace": {},
                }
            )
    return transitions


def _normalize_triggers(items: list[str]) -> list[dict[str, Any]]:
    """Convert trigger strings into structured process event objects."""
    triggers = []
    for index, item in enumerate(items, 1):
        text = item.strip()
        event_name = ""
        outcome = ""
        normalized = text.lower()
        if " triggers " in normalized:
            event_name, outcome = re.split(r"\btriggers\b", text, maxsplit=1, flags=re.IGNORECASE)
        elif " requires " in normalized:
            event_name, outcome = re.split(r"\brequires\b", text, maxsplit=1, flags=re.IGNORECASE)
        triggers.append(
            {
                "id": f"trigger-{index}",
                "event_name": event_name.strip(),
                "outcome": outcome.strip(),
                "description": text,
                "approval_required": "approval" in normalized,
                "trace": {},
            }
        )
    return triggers


def _normalize_components(items: list[str]) -> list[dict[str, Any]]:
    """Convert component strings into explicit architecture objects."""
    components = []
    for item in items:
        normalized_name = item.strip()
        lowered = normalized_name.lower()
        component_kind = "component"
        if "api" in lowered:
            component_kind = "api"
        elif "service" in lowered:
            component_kind = "service"
        elif "web" in lowered or "ui" in lowered or "portal" in lowered:
            component_kind = "application"
        components.append(
            {
                "id": f"component-{_slugify(normalized_name)}",
                "name": normalized_name,
                "component_kind": component_kind,
                "responsibility": "",
                "runtime_environment": "",
                "trace": {},
            }
        )
    return components


def _normalize_interfaces(
    items: list[str],
    components: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Convert interface strings into structured interface objects."""
    interfaces = []
    for index, item in enumerate(items, 1):
        text = item.strip()
        source_name = ""
        target_name = ""
        interaction_verb = ""
        normalized = text.lower()

        if " calls " in normalized:
            source_name, target_name = re.split(r"\bcalls\b", text, maxsplit=1, flags=re.IGNORECASE)
            interaction_verb = "calls"
        elif " sends " in normalized:
            source_name, target_name = re.split(r"\bsends\b", text, maxsplit=1, flags=re.IGNORECASE)
            interaction_verb = "sends"
        elif " receives " in normalized:
            source_name, target_name = re.split(r"\breceives\b", text, maxsplit=1, flags=re.IGNORECASE)
            interaction_verb = "receives"

        source_name = source_name.strip()
        target_name = target_name.strip()
        source_match = _best_name_match(source_name, components) if source_name else None
        target_match = _best_name_match(target_name, components) if target_name else None
        interfaces.append(
            {
                "id": f"interface-{index}",
                "description": text,
                "source_component_name": source_name,
                "source_component_id": source_match["id"] if source_match else "",
                "target_component_name": target_name,
                "target_component_id": target_match["id"] if target_match else "",
                "interaction_verb": interaction_verb,
                "protocol": "",
                "trace": {},
            }
        )
    return interfaces


def _normalize_runtime_boundaries(items: list[str]) -> list[dict[str, Any]]:
    """Convert runtime boundary strings into explicit deployment boundary objects."""
    boundaries = []
    for index, item in enumerate(items, 1):
        text = item.strip()
        normalized = text.lower()
        boundary_type = "runtime_separation" if "separate" in normalized else ""
        boundaries.append(
            {
                "id": f"runtime-boundary-{index}",
                "name": f"Runtime Boundary {index}",
                "boundary_type": boundary_type,
                "description": text,
                "deployment_nodes": [],
                "trace": {},
            }
        )
    return boundaries


def _with_trace(
    items: list[dict[str, Any]],
    source_round: int,
    source_key: str,
) -> list[dict[str, Any]]:
    """Attach deterministic source trace metadata to normalized objects."""
    traced_items = []
    for item in items:
        traced_item = dict(item)
        traced_item["trace"] = {
            "source_round": source_round,
            "source_key": source_key,
        }
        traced_items.append(traced_item)
    return traced_items


def _best_name_match(name: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find the best deterministic name match for a complexity entry."""
    target_slug = _match_slug(name)
    for candidate in candidates:
        if _match_slug(candidate.get("name", "")) == target_slug:
            return candidate

    target_tokens = set(target_slug.split("-"))
    best_match = None
    best_score = 0
    for candidate in candidates:
        candidate_tokens = set(_match_slug(candidate.get("name", "")).split("-"))
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
            match["complexity_trace"] = {
                "source_round": None,
                "source_key": "",
            }


def _apply_complexity_answers_with_trace(
    items: list[dict[str, Any]],
    answers: list[str],
    source_round: int,
    source_key: str,
) -> None:
    """Apply complexity answers and attach their trace metadata."""
    _apply_complexity_answers(items, answers)
    for answer in answers:
        if ":" not in answer:
            continue
        name, _complexity = answer.split(":", 1)
        match = _best_name_match(name.strip(), items)
        if match is not None:
            match["complexity_trace"] = {
                "source_round": source_round,
                "source_key": source_key,
            }


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
                "interaction_style": "user_interface" if actor_type == "human" else "system_interface",
                "responsibilities": [],
                "complexity": "unclassified",
                "trace": {},
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
                "primary_actor_id": "",
                "supporting_actor_ids": [],
                "goal": normalized_name,
                "trigger": "",
                "preconditions": [],
                "postconditions": [],
                "complexity": "unclassified",
                "main_success_scenario": [],
                "extensions": [],
                "trace": {},
            }
        )
    return use_cases


def _normalize_requirement_objects(
    items: list[str],
    requirement_kind: str,
) -> list[dict[str, Any]]:
    """Convert requirement strings into explicit canonical requirement objects."""
    objects = []
    for index, item in enumerate(items, 1):
        text = item.strip()
        quality_attribute = ""
        if requirement_kind == "non_functional" and ":" in text:
            quality_attribute = text.split(":", 1)[0].strip()
        objects.append(
            {
                "id": f"{requirement_kind}-requirement-{index}",
                "statement": text,
                "requirement_kind": requirement_kind,
                "quality_attribute": quality_attribute,
                "linked_use_case_ids": [],
                "fit_criterion": "",
                "trace": {},
            }
        )
    return objects


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
    normalized_actors = _with_trace(_normalize_actors(actors), 3, "actors")
    normalized_use_cases = _with_trace(_normalize_use_cases(use_cases), 3, "use_cases")
    _apply_complexity_answers_with_trace(
        normalized_actors,
        _ensure_list(round_8.get("actor_complexity")),
        8,
        "actor_complexity",
    )
    _apply_complexity_answers_with_trace(
        normalized_use_cases,
        _ensure_list(round_9.get("use_case_complexity")),
        9,
        "use_case_complexity",
    )
    technical_factors = _normalize_factor_map(round_10, TECHNICAL_FACTOR_ALIASES)
    environmental_factors = _normalize_factor_map(round_11, ENVIRONMENTAL_FACTOR_ALIASES)
    functional_requirement_objects = []
    if workflow_scope := _text_or_empty(round_4.get("workflow_scope")):
        functional_requirement_objects.extend(
            _with_trace(
                _normalize_requirement_objects([workflow_scope], "functional"),
                4,
                "workflow_scope",
            )
        )
    if integrations := _text_or_empty(round_3.get("integrations")):
        functional_requirement_objects.extend(
            _with_trace(
                _normalize_requirement_objects([integrations], "functional"),
                3,
                "integrations",
            )
        )

    non_functional_requirement_objects = []
    if constraints:
        non_functional_requirement_objects.extend(
            _with_trace(
                _normalize_requirement_objects(constraints, "non_functional"),
                2,
                "constraints",
            )
        )
    round_4_non_functional = _ensure_list(round_4.get("non_functional_requirements"))
    if round_4_non_functional:
        non_functional_requirement_objects.extend(
            _with_trace(
                _normalize_requirement_objects(round_4_non_functional, "non_functional"),
                4,
                "non_functional_requirements",
            )
        )

    domain_entity_objects = _with_trace(_normalize_domain_entities(domain_entities), 5, "domain_entities")
    relationship_objects = _with_trace(
        _normalize_relationships(relationships, domain_entity_objects),
        5,
        "relationships",
    )
    business_rule_objects = _with_trace(
        _normalize_business_rules(business_rules),
        5,
        "business_rules",
    )
    state_entity_objects = _with_trace(_normalize_state_entities(state_entities), 6, "state_entities")
    state_transition_objects = _with_trace(
        _normalize_state_transitions(states_and_transitions),
        6,
        "states_and_transitions",
    )
    trigger_objects = _with_trace(
        _normalize_triggers(triggers_and_approvals),
        6,
        "triggers_and_approvals",
    )
    component_objects = _with_trace(
        _normalize_components(components_and_services),
        7,
        "components_and_services",
    )
    interface_objects = _with_trace(
        _normalize_interfaces(interfaces_and_integrations, component_objects),
        7,
        "interfaces_and_integrations",
    )
    runtime_boundary_objects = _with_trace(
        _normalize_runtime_boundaries(runtime_boundaries),
        7,
        "runtime_boundaries",
    )

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
            "functional_objects": functional_requirement_objects,
            "non_functional": non_functional,
            "non_functional_objects": non_functional_requirement_objects,
        },
        "logical_view": {
            "domain_entities": domain_entities,
            "domain_entity_objects": domain_entity_objects,
            "relationships": relationships,
            "relationship_objects": relationship_objects,
            "business_rules": business_rules,
            "business_rule_objects": business_rule_objects,
        },
        "process_view": {
            "state_entities": state_entities,
            "state_entity_objects": state_entity_objects,
            "states_and_transitions": states_and_transitions,
            "state_transition_objects": state_transition_objects,
            "triggers_and_approvals": triggers_and_approvals,
            "trigger_objects": trigger_objects,
        },
        "architecture_view": {
            "components_and_services": components_and_services,
            "component_objects": component_objects,
            "interfaces_and_integrations": interfaces_and_integrations,
            "interface_objects": interface_objects,
            "runtime_boundaries": runtime_boundaries,
            "runtime_boundary_objects": runtime_boundary_objects,
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
