"""Deterministic normalization from interview replay data into a Rupify model."""

from __future__ import annotations

import hashlib
import json
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


def _text_matches_name(text: str, name: str) -> bool:
    """Return whether a text value explicitly mentions a canonical name."""
    text_slug = _match_slug(text)
    name_slug = _match_slug(name)
    if not text_slug or not name_slug:
        return False
    if text_slug == name_slug:
        return True
    text_tokens = text_slug.split("-")
    name_tokens = name_slug.split("-")
    if len(name_tokens) == 1:
        return name_slug in text_tokens
    phrase = "-".join(name_tokens)
    joined = "-".join(text_tokens)
    return phrase in joined


def _texts_overlap(left: str, right: str) -> bool:
    """Return whether two text values explicitly reference one another."""
    return _text_matches_name(left, right) or _text_matches_name(right, left)


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
        attributes = []
        name_part = normalized_name
        if ":" in normalized_name:
            name_part, attribute_part = normalized_name.split(":", 1)
            normalized_name = name_part.strip()
            attributes = [
                attribute.strip()
                for attribute in attribute_part.split(",")
                if attribute.strip()
            ]
        entities.append(
            {
                "id": f"entity-{_slugify(normalized_name)}",
                "name": normalized_name,
                "entity_type": "domain_entity",
                "model_layer": "analysis",
                "description": "",
                "attributes": attributes,
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
        source_multiplicity = ""
        target_multiplicity = ""
        source_role_name = ""
        target_role_name = ""
        normalized = text.lower()

        if " has many " in normalized:
            source_name, target_name = re.split(r"\bhas many\b", text, maxsplit=1, flags=re.IGNORECASE)
            relationship_type = "has_many"
            source_multiplicity = "1"
            target_multiplicity = "*"
        elif " has a " in normalized:
            source_name, target_name = re.split(r"\bhas a\b", text, maxsplit=1, flags=re.IGNORECASE)
            relationship_type = "has_one"
            source_multiplicity = "1"
            target_multiplicity = "1"
        elif " has an " in normalized:
            source_name, target_name = re.split(r"\bhas an\b", text, maxsplit=1, flags=re.IGNORECASE)
            relationship_type = "has_one"
            source_multiplicity = "1"
            target_multiplicity = "1"
        elif " belongs to " in normalized:
            source_name, target_name = re.split(
                r"\bbelongs to\b",
                text,
                maxsplit=1,
                flags=re.IGNORECASE,
            )
            relationship_type = "belongs_to"
            source_multiplicity = "*"
            target_multiplicity = "1"

        source_name = source_name.strip()
        target_name = target_name.strip()
        if source_name and target_name:
            source_role_name = _slugify(target_name).replace("-", "_")
            target_role_name = _slugify(source_name).replace("-", "_")
        source_match = _best_name_match(source_name, entities) if source_name else None
        target_match = _best_name_match(target_name, entities) if target_name else None
        relationships.append(
            {
                "id": f"relationship-{index}",
                "description": text,
                "relationship_type": relationship_type,
                "model_layer": "analysis",
                "source_name": source_name,
                "source_entity_id": source_match["id"] if source_match else "",
                "target_name": target_name,
                "target_entity_id": target_match["id"] if target_match else "",
                "source_multiplicity": source_multiplicity,
                "target_multiplicity": target_multiplicity,
                "source_role_name": source_role_name,
                "target_role_name": target_role_name,
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
                "model_layer": "analysis",
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
                "model_layer": "analysis",
                "description": "",
                "states": [],
                "trace": {},
            }
        )
    return entities


def _parse_state_transition_prefix(text: str) -> tuple[str, str]:
    """Split a transition string into optional entity prefix and transition body."""
    if ":" not in text:
        return "", text
    prefix, remainder = text.split(":", 1)
    if "->" not in remainder:
        return "", text
    return prefix.strip(), remainder.strip()


def _is_exception_state(state_name: str) -> bool:
    """Return whether a state label clearly represents an exceptional path."""
    normalized = _slugify(state_name)
    return normalized in {
        "rejected",
        "cancelled",
        "canceled",
        "failed",
        "error",
        "exception",
        "escalated",
    }


def _is_terminal_state(state_name: str) -> bool:
    """Return whether a state label clearly represents a terminal lifecycle state."""
    normalized = _slugify(state_name)
    return normalized in {
        "approved",
        "fulfilled",
        "completed",
        "closed",
        "cancelled",
        "canceled",
        "rejected",
        "failed",
        "inactive",
        "archived",
    }


def _normalize_state_transitions(items: list[str]) -> list[dict[str, Any]]:
    """Convert transition strings into structured transition objects."""
    transitions = []
    for item in items:
        text = item.strip()
        entity_name, transition_text = _parse_state_transition_prefix(text)
        if "->" not in transition_text:
            transitions.append(
                {
                    "id": f"state-transition-{len(transitions) + 1}",
                    "description": text,
                    "model_layer": "analysis",
                    "state_entity_id": f"state-entity-{_slugify(entity_name)}" if entity_name else "",
                    "state_entity_name": entity_name,
                    "from_state": "",
                    "to_state": "",
                    "trigger": "",
                    "is_exception_flow": False,
                    "is_terminal_transition": False,
                    "constraint": "",
                    "trace": {},
                }
            )
            continue

        states = [part.strip() for part in transition_text.split("->") if part.strip()]
        for source_state, target_state in zip(states, states[1:]):
            is_last_transition = target_state == states[-1]
            transitions.append(
                {
                    "id": f"state-transition-{len(transitions) + 1}",
                    "description": text,
                    "model_layer": "analysis",
                    "state_entity_id": f"state-entity-{_slugify(entity_name)}" if entity_name else "",
                    "state_entity_name": entity_name,
                    "from_state": source_state,
                    "to_state": target_state,
                    "trigger": "",
                    "is_exception_flow": _is_exception_state(target_state),
                    "is_terminal_transition": is_last_transition and _is_terminal_state(target_state),
                    "constraint": "",
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
                "model_layer": "analysis",
                "approval_required": "approval" in normalized,
                "constraint_type": "approval" if "approval" in normalized else "event",
                "exceptional_behavior": any(
                    marker in normalized
                    for marker in ("reject", "cancel", "fail", "error", "exception", "escalat")
                ),
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
                "model_layer": "design",
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
                "model_layer": "design",
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
                "model_layer": "design",
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
                "model_layer": "analysis",
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
                "model_layer": "analysis",
                "goal": normalized_name,
                "trigger": "",
                "preconditions": [],
                "postconditions": [],
                "priority": "",
                "status": "",
                "complexity": "unclassified",
                "main_success_scenario": [],
                "extensions": [],
                "extension_points": [],
                "used_use_case_ids": [],
                "subordinate_use_case_ids": [],
                "ui_notes": [],
                "participating_analysis_object_ids": [],
                "other_artifact_refs": [],
                "other_requirement_ids": [],
                "scenario_ids": [],
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
                "model_layer": "analysis",
                "linked_use_case_ids": [],
                "fit_criterion": "",
                "trace": {},
            }
        )
    return objects


def _split_structured_parts(item: str) -> list[str]:
    """Split a pipe-delimited structured answer into trimmed parts."""
    return [part.strip() for part in item.split("|") if part.strip()]


def _normalize_risks(items: list[str]) -> list[dict[str, Any]]:
    """Convert structured risk strings into explicit risk objects."""
    risk_objects = []
    for index, item in enumerate(items, 1):
        parts = _split_structured_parts(item)
        if not parts:
            continue
        name = parts[0]
        description = name
        if ":" in name:
            name_part, description_part = name.split(":", 1)
            name = name_part.strip()
            description = description_part.strip() or name

        priority = ""
        status = ""
        mitigation = ""
        for part in parts[1:]:
            if ":" not in part:
                continue
            key, value = part.split(":", 1)
            normalized_key = _slugify(key).replace("-", "_")
            normalized_value = value.strip()
            if normalized_key == "priority":
                priority = normalized_value.lower()
            elif normalized_key == "status":
                status = normalized_value.lower()
            elif normalized_key == "mitigation":
                mitigation = normalized_value

        risk_objects.append(
            {
                "id": f"risk-{_slugify(name) or index}",
                "name": name,
                "description": description,
                "priority": priority,
                "status": status,
                "mitigation": mitigation,
                "model_layer": "analysis",
                "trace": {},
            }
        )

    return risk_objects


def _apply_use_case_details(
    use_cases: list[dict[str, Any]],
    items: list[str],
) -> None:
    """Apply structured use-case detail answers to canonical use cases in place."""
    for item in items:
        parts = _split_structured_parts(item)
        if not parts:
            continue

        match = _best_name_match(parts[0], use_cases)
        if match is None:
            continue

        for part in parts[1:]:
            if ":" not in part:
                continue
            key, value = part.split(":", 1)
            normalized_key = _slugify(key).replace("-", "_")
            normalized_value = value.strip()
            if normalized_key == "priority":
                match["priority"] = normalized_value.lower()
            elif normalized_key == "status":
                match["status"] = normalized_value.lower()
            elif normalized_key == "used":
                used_ids = []
                for name in [segment.strip() for segment in normalized_value.split(";") if segment.strip()]:
                    linked_use_case = _best_name_match(name, use_cases)
                    if linked_use_case is not None:
                        used_ids.append(linked_use_case["id"])
                match["used_use_case_ids"] = used_ids
            elif normalized_key == "subordinate":
                subordinate_ids = []
                for name in [segment.strip() for segment in normalized_value.split(";") if segment.strip()]:
                    linked_use_case = _best_name_match(name, use_cases)
                    if linked_use_case is not None:
                        subordinate_ids.append(linked_use_case["id"])
                match["subordinate_use_case_ids"] = subordinate_ids
            elif normalized_key == "extension_points":
                match["extension_points"] = [
                    segment.strip() for segment in normalized_value.split(";") if segment.strip()
                ]
            elif normalized_key == "flow":
                match["main_success_scenario"] = [
                    segment.strip() for segment in normalized_value.split(";") if segment.strip()
                ]
            elif normalized_key == "extensions":
                match["extensions"] = [
                    segment.strip() for segment in normalized_value.split(";") if segment.strip()
                ]
            elif normalized_key == "preconditions":
                match["preconditions"] = [
                    segment.strip() for segment in normalized_value.split(";") if segment.strip()
                ]
            elif normalized_key == "postconditions":
                match["postconditions"] = [
                    segment.strip() for segment in normalized_value.split(";") if segment.strip()
                ]


def _normalize_scenarios(
    items: list[str],
    use_cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Convert structured scenario strings into explicit scenario objects."""
    scenario_objects = []
    for index, item in enumerate(items, 1):
        parts = _split_structured_parts(item)
        if len(parts) < 3:
            continue

        use_case_name = parts[0]
        scenario_name = parts[1]
        summary = parts[2]
        use_case_match = _best_name_match(use_case_name, use_cases)
        use_case_id = use_case_match["id"] if use_case_match else ""
        resolved_use_case_name = use_case_match["name"] if use_case_match else use_case_name

        priority = ""
        status = ""
        flow_of_events: list[str] = []
        for part in parts[3:]:
            if ":" not in part:
                continue
            key, value = part.split(":", 1)
            normalized_key = _slugify(key).replace("-", "_")
            normalized_value = value.strip()
            if normalized_key == "priority":
                priority = normalized_value.lower()
            elif normalized_key == "status":
                status = normalized_value.lower()
            elif normalized_key == "flow":
                flow_of_events = [
                    segment.strip() for segment in normalized_value.split(";") if segment.strip()
                ]

        scenario_objects.append(
            {
                "id": f"scenario-{_slugify(scenario_name) or index}",
                "name": scenario_name,
                "use_case_id": use_case_id,
                "use_case_name": resolved_use_case_name,
                "model_layer": "analysis",
                "summary": summary,
                "priority": priority,
                "status": status,
                "flow_of_events": flow_of_events,
                "activity_notes": [],
                "sequence_notes": [],
                "other_artifact_refs": [],
                "participating_analysis_object_ids": [],
                "other_requirement_ids": [],
                "trace": {},
            }
        )

    return scenario_objects


def _apply_ui_notes(
    use_cases: list[dict[str, Any]],
    items: list[str],
) -> None:
    """Attach structured UI notes to the matching use cases."""
    for item in items:
        parts = _split_structured_parts(item)
        if len(parts) < 2:
            continue
        match = _best_name_match(parts[0], use_cases)
        if match is None:
            continue
        match["ui_notes"].append(" | ".join(parts[1:]))


def _bind_scenario_links(
    use_cases: list[dict[str, Any]],
    scenario_objects: list[dict[str, Any]],
) -> None:
    """Attach scenario ids back onto their parent use cases."""
    scenario_ids_by_use_case: dict[str, list[str]] = {}
    for scenario in scenario_objects:
        use_case_id = scenario.get("use_case_id", "")
        scenario_id = scenario.get("id", "")
        if not use_case_id or not scenario_id:
            continue
        scenario_ids_by_use_case.setdefault(use_case_id, []).append(scenario_id)

    for use_case in use_cases:
        use_case["scenario_ids"] = scenario_ids_by_use_case.get(use_case.get("id", ""), [])


def _build_use_case_step_objects(use_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build first-class step objects from use-case main and extension flows."""
    step_objects = []
    for use_case in use_cases:
        use_case_id = use_case.get("id", "")
        for index, step_text in enumerate(use_case.get("main_success_scenario", []), 1):
            step_objects.append(
                {
                    "id": f"{use_case_id}-step-{index}",
                    "use_case_id": use_case_id,
                    "use_case_name": use_case.get("name", ""),
                    "step_index": index,
                    "step_kind": "main_success",
                    "text": step_text,
                    "model_layer": "analysis",
                    "trace": use_case.get("trace", {}),
                }
            )
        for index, step_text in enumerate(use_case.get("extensions", []), 1):
            step_objects.append(
                {
                    "id": f"{use_case_id}-extension-{index}",
                    "use_case_id": use_case_id,
                    "use_case_name": use_case.get("name", ""),
                    "step_index": index,
                    "step_kind": "extension",
                    "text": step_text,
                    "model_layer": "analysis",
                    "trace": use_case.get("trace", {}),
                }
            )
    return step_objects


def _build_trace_links(
    requirement_objects: list[dict[str, Any]],
    use_cases: list[dict[str, Any]],
    use_case_step_objects: list[dict[str, Any]],
    domain_entities: list[dict[str, Any]],
    business_rules: list[dict[str, Any]],
    state_entities: list[dict[str, Any]],
    state_transitions: list[dict[str, Any]],
    components: list[dict[str, Any]],
    interaction_messages: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Build conservative cross-view trace links from explicit textual references."""
    requirement_to_use_case = []
    requirement_to_step = []
    use_case_to_analysis = []
    step_to_interaction = []
    step_to_transition = []
    business_rule_to_transition = []
    analysis_to_design = []

    for requirement in requirement_objects:
        linked_use_case_ids = []
        for use_case in use_cases:
            if _text_matches_name(requirement["statement"], use_case["name"]):
                requirement_to_use_case.append(
                    {
                        "id": f"trace-req-uc-{len(requirement_to_use_case) + 1}",
                        "from_id": requirement["id"],
                        "to_id": use_case["id"],
                        "link_type": "requirement_to_use_case",
                        "basis": "requirement statement references use-case name",
                    }
                )
                linked_use_case_ids.append(use_case["id"])
        linked_step_ids = []
        for step_object in use_case_step_objects:
            if _texts_overlap(requirement["statement"], step_object["text"]):
                requirement_to_step.append(
                    {
                        "id": f"trace-req-step-{len(requirement_to_step) + 1}",
                        "from_id": requirement["id"],
                        "to_id": step_object["id"],
                        "link_type": "requirement_to_step",
                        "basis": "requirement statement references use-case step text",
                    }
                )
                linked_step_ids.append(step_object["id"])
        requirement["linked_use_case_ids"] = linked_use_case_ids
        requirement["linked_step_ids"] = linked_step_ids

    analysis_candidates = domain_entities + state_entities
    for use_case in use_cases:
        use_case_text = " ".join(
            [
                use_case.get("name", ""),
                use_case.get("goal", ""),
                *use_case.get("main_success_scenario", []),
            ]
        ).strip()
        for analysis_object in analysis_candidates:
            if _text_matches_name(use_case_text, analysis_object["name"]):
                use_case_to_analysis.append(
                    {
                        "id": f"trace-uc-analysis-{len(use_case_to_analysis) + 1}",
                        "from_id": use_case["id"],
                        "to_id": analysis_object["id"],
                        "link_type": "use_case_to_analysis",
                        "basis": "use-case text references analysis object name",
                    }
                )

    for analysis_object in analysis_candidates:
        for component in components:
            if _text_matches_name(component["name"], analysis_object["name"]):
                analysis_to_design.append(
                    {
                        "id": f"trace-analysis-design-{len(analysis_to_design) + 1}",
                        "from_id": analysis_object["id"],
                        "to_id": component["id"],
                        "link_type": "analysis_to_design",
                        "basis": "design component name references analysis object name",
                    }
                )

    for step_object in use_case_step_objects:
        step_text = step_object.get("text", "")
        for message in interaction_messages:
            message_text = " ".join(
                [
                    message.get("description", ""),
                    message.get("interaction_verb", ""),
                    message.get("source_name", ""),
                    message.get("target_name", ""),
                ]
            ).strip()
            if step_text and _texts_overlap(step_text, message_text):
                step_to_interaction.append(
                    {
                        "id": f"trace-step-interaction-{len(step_to_interaction) + 1}",
                        "from_id": step_object["id"],
                        "to_id": message["id"],
                        "link_type": "step_to_interaction",
                        "basis": "use-case step text references interaction message text",
                    }
                )
        for transition in state_transitions:
            transition_text = " ".join(
                [
                    transition.get("description", ""),
                    transition.get("from_state", ""),
                    transition.get("to_state", ""),
                    transition.get("trigger", ""),
                    transition.get("constraint", ""),
                ]
            ).strip()
            if step_text and _texts_overlap(step_text, transition_text):
                step_to_transition.append(
                    {
                        "id": f"trace-step-transition-{len(step_to_transition) + 1}",
                        "from_id": step_object["id"],
                        "to_id": transition["id"],
                        "link_type": "step_to_transition",
                        "basis": "use-case step text references state transition text",
                    }
                )

    for business_rule in business_rules:
        rule_text = business_rule.get("rule_text", "")
        rule_scope = business_rule.get("scope", "")
        for transition in state_transitions:
            transition_text = " ".join(
                [
                    transition.get("description", ""),
                    transition.get("from_state", ""),
                    transition.get("to_state", ""),
                    transition.get("trigger", ""),
                    transition.get("constraint", ""),
                ]
            ).strip()
            if not transition_text:
                continue
            if rule_text and _texts_overlap(rule_text, transition_text):
                business_rule_to_transition.append(
                    {
                        "id": f"trace-rule-transition-{len(business_rule_to_transition) + 1}",
                        "from_id": business_rule["id"],
                        "to_id": transition["id"],
                        "link_type": "business_rule_to_transition",
                        "basis": "business rule text references state transition text",
                    }
                )
                continue
            if rule_scope and _texts_overlap(rule_scope, transition_text):
                business_rule_to_transition.append(
                    {
                        "id": f"trace-rule-transition-{len(business_rule_to_transition) + 1}",
                        "from_id": business_rule["id"],
                        "to_id": transition["id"],
                        "link_type": "business_rule_to_transition",
                        "basis": "business rule scope references state transition text",
                    }
                )

    return {
        "requirement_to_use_case": requirement_to_use_case,
        "requirement_to_step": requirement_to_step,
        "use_case_to_analysis": use_case_to_analysis,
        "step_to_interaction": step_to_interaction,
        "step_to_transition": step_to_transition,
        "business_rule_to_transition": business_rule_to_transition,
        "analysis_to_design": analysis_to_design,
    }


def _bind_use_case_supporting_links(
    use_cases: list[dict[str, Any]],
    requirement_objects: list[dict[str, Any]],
    traceability: dict[str, list[dict[str, Any]]],
) -> None:
    """Populate deterministic supporting links on use cases from derived trace data."""
    linked_requirements_by_use_case: dict[str, list[str]] = {}
    for requirement in requirement_objects:
        requirement_id = requirement.get("id", "")
        if not requirement_id:
            continue
        for use_case_id in requirement.get("linked_use_case_ids", []):
            linked_requirements_by_use_case.setdefault(use_case_id, []).append(requirement_id)

    participating_analysis_ids_by_use_case: dict[str, list[str]] = {}
    for link in traceability.get("use_case_to_analysis", []):
        use_case_id = str(link.get("from_id", "")).strip()
        analysis_id = str(link.get("to_id", "")).strip()
        if not use_case_id or not analysis_id:
            continue
        participating_analysis_ids_by_use_case.setdefault(use_case_id, []).append(analysis_id)

    for use_case in use_cases:
        use_case_id = use_case.get("id", "")
        use_case["other_requirement_ids"] = linked_requirements_by_use_case.get(use_case_id, [])
        use_case["participating_analysis_object_ids"] = participating_analysis_ids_by_use_case.get(
            use_case_id,
            [],
        )


def _build_artifact_lineage(
    risk_objects: list[dict[str, Any]],
    requirement_objects: list[dict[str, Any]],
    use_cases: list[dict[str, Any]],
    scenario_objects: list[dict[str, Any]],
    domain_entity_objects: list[dict[str, Any]],
    relationship_objects: list[dict[str, Any]],
    business_rule_objects: list[dict[str, Any]],
    state_entity_objects: list[dict[str, Any]],
    state_transition_objects: list[dict[str, Any]],
    trigger_objects: list[dict[str, Any]],
    component_objects: list[dict[str, Any]],
    interface_objects: list[dict[str, Any]],
    runtime_boundary_objects: list[dict[str, Any]],
    realization_objects: list[dict[str, Any]],
    message_objects: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Build conservative lineage links from canonical objects to generated artifacts."""
    lineage_specs = [
        ("system-document.md", "risk factors", risk_objects),
        ("system-document.md", "system-level use cases", use_cases),
        ("system-document.md", "architecture overview", component_objects),
        ("system-document.md", "interfaces and integrations", interface_objects),
        ("system-document.md", "runtime boundaries", runtime_boundary_objects),
        ("requirements-spec.md", "functional requirements", requirement_objects),
        ("use-case-model.md", "use cases", use_cases),
        ("use-case-documents.md", "use-case documents", use_cases),
        ("use-case-documents.md", "scenario summaries", scenario_objects),
        ("scenario-documents.md", "scenario documents", scenario_objects),
        ("domain-model.md", "domain entities", domain_entity_objects),
        ("domain-model.md", "relationships", relationship_objects),
        ("domain-model.md", "business rules", business_rule_objects),
        ("interaction-model.md", "use-case realizations", realization_objects),
        ("interaction-model.md", "message flows", message_objects),
        ("deployment-model.md", "components", component_objects),
        ("deployment-model.md", "interfaces and integrations", interface_objects),
        ("deployment-model.md", "runtime boundaries", runtime_boundary_objects),
        ("state-model.md", "state entities", state_entity_objects),
        ("state-model.md", "state transitions", state_transition_objects),
        ("state-model.md", "triggers and approvals", trigger_objects),
    ]

    artifact_lineage = []
    for artifact_name, artifact_section, objects in lineage_specs:
        artifact_slug = artifact_name.replace(".md", "").replace(".", "-")
        section_slug = _slugify(artifact_section)
        for item in objects:
            source_id = item.get("id", "")
            if not source_id:
                continue
            artifact_lineage.append(
                {
                    "id": f"trace-artifact-{artifact_slug}-{section_slug}-{source_id}",
                    "from_id": source_id,
                    "to_artifact": artifact_name,
                    "artifact_section": artifact_section,
                    "link_type": "artifact_lineage",
                    "basis": f"canonical {artifact_section} object renders into {artifact_name}",
                }
            )

    return artifact_lineage


def _text_or_empty(value: Any) -> str:
    """Normalize a scalar answer into a string."""
    if value is None:
        return ""
    return str(value).strip()


def _stable_semantic_payload(value: Any) -> Any:
    """Build a deterministic semantic payload for hashing."""
    if isinstance(value, dict):
        ignored_keys = {
            "trace",
            "change_metadata",
            "semantic_id",
            "complexity_trace",
            "last_changed_at",
        }
        return {
            key: _stable_semantic_payload(item)
            for key, item in sorted(value.items())
            if key not in ignored_keys
        }
    if isinstance(value, list):
        return [_stable_semantic_payload(item) for item in value]
    return value


def _semantic_hash(semantic_id: str, payload: Any) -> str:
    """Return a deterministic semantic hash for one element."""
    encoded = json.dumps(
        {
            "semantic_id": semantic_id,
            "payload": _stable_semantic_payload(payload),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _default_change_metadata(
    semantic_id: str,
    payload: Any,
    *,
    change_source: str,
) -> dict[str, Any]:
    """Return default change metadata for a canonical element."""
    return {
        "semantic_version": 1,
        "semantic_hash": _semantic_hash(semantic_id, payload),
        "last_changed_at": "",
        "change_source": change_source,
        "regenerated_from_version": "",
        "supersedes": [],
    }


def _stamp_semantic_identity(
    items: list[dict[str, Any]],
    *,
    change_source: str,
) -> list[dict[str, Any]]:
    """Attach semantic identity and change metadata to canonical records."""
    for item in items:
        semantic_id = str(item.get("semantic_id") or item.get("id") or _slugify(str(item))).strip()
        item["semantic_id"] = semantic_id
        item["change_metadata"] = _default_change_metadata(
            semantic_id,
            item,
            change_source=change_source,
        )
    return items


def _build_model_metadata(model: dict[str, Any]) -> dict[str, Any]:
    """Build top-level model metadata for downstream diffing and reconciliation."""
    semantic_id = "rupify-model"
    return {
        "schema_version": 1,
        "semantic_id": semantic_id,
        "change_metadata": _default_change_metadata(
            semantic_id,
            model,
            change_source="normalize_replay_to_model",
        ),
    }


def _requirement_statements_by_kind(
    requirement_objects: list[dict[str, Any]],
    requirement_kind: str,
) -> list[str]:
    """Derive legacy requirement statement lists from canonical requirement objects."""
    return [
        item["statement"]
        for item in requirement_objects
        if item.get("requirement_kind") == requirement_kind and item.get("statement")
    ]


def _derive_logical_view(analysis_view: dict[str, Any]) -> dict[str, Any]:
    """Build the legacy logical view mirror from analysis-layer source data."""
    domain_entity_objects = analysis_view["domain_entity_objects"]
    relationship_objects = analysis_view["relationship_objects"]
    business_rule_objects = analysis_view["business_rule_objects"]
    return {
        "domain_entities": [item["name"] for item in domain_entity_objects],
        "domain_entity_objects": domain_entity_objects,
        "relationships": [item["description"] for item in relationship_objects],
        "relationship_objects": relationship_objects,
        "business_rules": [item["rule_text"] for item in business_rule_objects],
        "business_rule_objects": business_rule_objects,
    }


def _derive_process_view(analysis_view: dict[str, Any]) -> dict[str, Any]:
    """Build the legacy process view mirror from analysis-layer source data."""
    state_entity_objects = analysis_view["state_entity_objects"]
    state_transition_objects = analysis_view["state_transition_objects"]
    trigger_objects = analysis_view["trigger_objects"]
    return {
        "state_entities": [item["name"] for item in state_entity_objects],
        "state_entity_objects": state_entity_objects,
        "states_and_transitions": [item["description"] for item in state_transition_objects],
        "state_transition_objects": state_transition_objects,
        "triggers_and_approvals": [item["description"] for item in trigger_objects],
        "trigger_objects": trigger_objects,
    }


def _derive_architecture_view(design_view: dict[str, Any]) -> dict[str, Any]:
    """Build the legacy architecture view mirror from design-layer source data."""
    component_objects = design_view["component_objects"]
    interface_objects = design_view["interface_objects"]
    runtime_boundary_objects = design_view["runtime_boundary_objects"]
    return {
        "components_and_services": [item["name"] for item in component_objects],
        "component_objects": component_objects,
        "interfaces_and_integrations": [item["description"] for item in interface_objects],
        "interface_objects": interface_objects,
        "runtime_boundaries": [item["description"] for item in runtime_boundary_objects],
        "runtime_boundary_objects": runtime_boundary_objects,
    }


def _build_interaction_view(
    use_cases: list[dict[str, Any]],
    actors: list[dict[str, Any]],
    interface_objects: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a conservative interaction view from use-case and interface data."""
    actor_name_to_id = {
        item.get("name", ""): item.get("id", "")
        for item in actors
        if item.get("name") and item.get("id")
    }

    realization_objects = []
    for index, use_case in enumerate(use_cases, 1):
        participant_ids = []
        participant_names = []
        primary_actor_name = use_case.get("primary_actor", "")
        primary_actor_id = use_case.get("primary_actor_id", "") or actor_name_to_id.get(primary_actor_name, "")
        if primary_actor_id:
            participant_ids.append(primary_actor_id)
        if primary_actor_name and primary_actor_name != "Unspecified":
            participant_names.append(primary_actor_name)

        for actor_id in use_case.get("supporting_actor_ids", []):
            if actor_id and actor_id not in participant_ids:
                participant_ids.append(actor_id)

        step_objects = []
        for step_index, step_text in enumerate(use_case.get("main_success_scenario", []), 1):
            step_objects.append(
                {
                    "id": f"{use_case.get('id', '')}-realization-step-{step_index}",
                    "use_case_id": use_case.get("id", ""),
                    "use_case_name": use_case.get("name", ""),
                    "step_index": step_index,
                    "text": step_text,
                    "model_layer": "analysis",
                    "trace": use_case.get("trace", {}),
                }
            )

        realization_objects.append(
            {
                "id": f"interaction-realization-{index}",
                "use_case_id": use_case.get("id", ""),
                "use_case_name": use_case.get("name", ""),
                "participant_ids": participant_ids,
                "participant_names": participant_names,
                "steps": list(use_case.get("main_success_scenario", [])),
                "step_objects": step_objects,
                "model_layer": "analysis",
                "trace": use_case.get("trace", {}),
            }
        )

    message_objects = []
    for index, interface in enumerate(interface_objects, 1):
        message_objects.append(
            {
                "id": f"interaction-message-{index}",
                "source_name": interface.get("source_component_name", ""),
                "source_id": interface.get("source_component_id", ""),
                "target_name": interface.get("target_component_name", ""),
                "target_id": interface.get("target_component_id", ""),
                "interaction_verb": interface.get("interaction_verb", ""),
                "description": interface.get("description", ""),
                "model_layer": "design",
                "trace": interface.get("trace", {}),
            }
        )

    return {
        "realization_objects": realization_objects,
        "message_objects": message_objects,
        "realization_ids": [item["id"] for item in realization_objects],
        "message_ids": [item["id"] for item in message_objects],
    }


def _bind_state_semantics(
    state_entity_objects: list[dict[str, Any]],
    state_transition_objects: list[dict[str, Any]],
    trigger_objects: list[dict[str, Any]],
) -> None:
    """Link transitions to explicit lifecycle owners and derive entity state lists."""
    entity_id_by_name = {
        _match_slug(item.get("name", "")): item.get("id", "")
        for item in state_entity_objects
        if item.get("name") and item.get("id")
    }

    for transition in state_transition_objects:
        state_entity_name = transition.get("state_entity_name", "")
        if state_entity_name and not transition.get("state_entity_id"):
            transition["state_entity_id"] = entity_id_by_name.get(_match_slug(state_entity_name), "")

        if not transition.get("state_entity_id") and len(state_entity_objects) == 1:
            transition["state_entity_id"] = state_entity_objects[0]["id"]
            transition["state_entity_name"] = state_entity_objects[0]["name"]

        trigger_text = " ".join(
            part for part in (transition.get("description", ""), transition.get("constraint", "")) if part
        )
        normalized_trigger_text = trigger_text.lower()
        for trigger in trigger_objects:
            event_name = trigger.get("event_name", "")
            if event_name and event_name.lower() in normalized_trigger_text:
                transition["trigger"] = event_name
                break

    states_by_entity_id: dict[str, list[str]] = {
        item.get("id", ""): [] for item in state_entity_objects if item.get("id")
    }
    for transition in state_transition_objects:
        entity_id = transition.get("state_entity_id", "")
        if not entity_id or entity_id not in states_by_entity_id:
            continue
        for state_name in (transition.get("from_state", ""), transition.get("to_state", "")):
            if state_name and state_name not in states_by_entity_id[entity_id]:
                states_by_entity_id[entity_id].append(state_name)

    for entity in state_entity_objects:
        entity["states"] = states_by_entity_id.get(entity.get("id", ""), [])


def normalize_replay_to_model(replay: dict[str, Any]) -> dict[str, Any]:
    """Normalize replay output into a canonical Rupify model shape.

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
    round_12 = merged_answers.get("round_12", {})
    round_13 = merged_answers.get("round_13", {})
    constraints = _ensure_list(round_2.get("constraints"))
    normalized_actors = _with_trace(_normalize_actors(_ensure_list(round_3.get("actors"))), 3, "actors")
    normalized_use_cases = _with_trace(
        _normalize_use_cases(_ensure_list(round_3.get("use_cases"))),
        3,
        "use_cases",
    )
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
    risk_objects = _with_trace(
        _normalize_risks(_ensure_list(round_12.get("risks"))),
        12,
        "risks",
    )

    domain_entity_objects = _with_trace(
        _normalize_domain_entities(_ensure_list(round_5.get("domain_entities"))),
        5,
        "domain_entities",
    )
    relationship_objects = _with_trace(
        _normalize_relationships(_ensure_list(round_5.get("relationships")), domain_entity_objects),
        5,
        "relationships",
    )
    business_rule_objects = _with_trace(
        _normalize_business_rules(_ensure_list(round_5.get("business_rules"))),
        5,
        "business_rules",
    )
    state_entity_objects = _with_trace(
        _normalize_state_entities(_ensure_list(round_6.get("state_entities"))),
        6,
        "state_entities",
    )
    state_transition_objects = _with_trace(
        _normalize_state_transitions(_ensure_list(round_6.get("states_and_transitions"))),
        6,
        "states_and_transitions",
    )
    trigger_objects = _with_trace(
        _normalize_triggers(_ensure_list(round_6.get("triggers_and_approvals"))),
        6,
        "triggers_and_approvals",
    )
    _bind_state_semantics(
        state_entity_objects,
        state_transition_objects,
        trigger_objects,
    )
    component_objects = _with_trace(
        _normalize_components(_ensure_list(round_7.get("components_and_services"))),
        7,
        "components_and_services",
    )
    interface_objects = _with_trace(
        _normalize_interfaces(_ensure_list(round_7.get("interfaces_and_integrations")), component_objects),
        7,
        "interfaces_and_integrations",
    )
    runtime_boundary_objects = _with_trace(
        _normalize_runtime_boundaries(_ensure_list(round_7.get("runtime_boundaries"))),
        7,
        "runtime_boundaries",
    )
    _apply_use_case_details(
        normalized_use_cases,
        _ensure_list(round_13.get("use_case_details")),
    )
    scenario_objects = _with_trace(
        _normalize_scenarios(_ensure_list(round_13.get("scenarios")), normalized_use_cases),
        13,
        "scenarios",
    )
    _apply_ui_notes(
        normalized_use_cases,
        _ensure_list(round_13.get("ui_notes")),
    )
    _bind_scenario_links(
        normalized_use_cases,
        scenario_objects,
    )
    use_case_step_objects = _build_use_case_step_objects(normalized_use_cases)
    _stamp_semantic_identity(normalized_actors, change_source="round_3")
    _stamp_semantic_identity(normalized_use_cases, change_source="round_3")
    _stamp_semantic_identity(use_case_step_objects, change_source="derived_use_case_steps")
    _stamp_semantic_identity(scenario_objects, change_source="round_13")
    _stamp_semantic_identity(risk_objects, change_source="round_12")
    _stamp_semantic_identity(domain_entity_objects, change_source="round_5")
    _stamp_semantic_identity(relationship_objects, change_source="round_5")
    _stamp_semantic_identity(business_rule_objects, change_source="round_5")
    _stamp_semantic_identity(state_entity_objects, change_source="round_6")
    _stamp_semantic_identity(state_transition_objects, change_source="round_6")
    _stamp_semantic_identity(trigger_objects, change_source="round_6")
    _stamp_semantic_identity(component_objects, change_source="round_7")
    _stamp_semantic_identity(interface_objects, change_source="round_7")
    _stamp_semantic_identity(runtime_boundary_objects, change_source="round_7")
    all_requirement_objects = functional_requirement_objects + non_functional_requirement_objects
    _stamp_semantic_identity(functional_requirement_objects, change_source="round_4")
    _stamp_semantic_identity(non_functional_requirement_objects, change_source="round_2_or_4")
    _stamp_semantic_identity(all_requirement_objects, change_source="requirements")
    analysis_view = {
        "actor_ids": [item["id"] for item in normalized_actors],
        "use_case_ids": [item["id"] for item in normalized_use_cases],
        "use_case_step_ids": [item["id"] for item in use_case_step_objects],
        "scenario_ids": [item["id"] for item in scenario_objects],
        "risk_ids": [item["id"] for item in risk_objects],
        "requirement_ids": [item["id"] for item in all_requirement_objects],
        "actors": normalized_actors,
        "use_cases": normalized_use_cases,
        "use_case_step_objects": use_case_step_objects,
        "scenario_objects": scenario_objects,
        "risk_objects": risk_objects,
        "requirement_objects": all_requirement_objects,
        "domain_entity_objects": domain_entity_objects,
        "relationship_objects": relationship_objects,
        "business_rule_objects": business_rule_objects,
        "state_entity_objects": state_entity_objects,
        "state_transition_objects": state_transition_objects,
        "trigger_objects": trigger_objects,
        "domain_entity_ids": [item["id"] for item in domain_entity_objects],
        "relationship_ids": [item["id"] for item in relationship_objects],
        "business_rule_ids": [item["id"] for item in business_rule_objects],
        "state_entity_ids": [item["id"] for item in state_entity_objects],
        "state_transition_ids": [item["id"] for item in state_transition_objects],
        "trigger_ids": [item["id"] for item in trigger_objects],
    }
    design_view = {
        "component_objects": component_objects,
        "interface_objects": interface_objects,
        "runtime_boundary_objects": runtime_boundary_objects,
        "component_ids": [item["id"] for item in component_objects],
        "interface_ids": [item["id"] for item in interface_objects],
        "runtime_boundary_ids": [item["id"] for item in runtime_boundary_objects],
    }
    logical_view = _derive_logical_view(analysis_view)
    process_view = _derive_process_view(analysis_view)
    architecture_view = _derive_architecture_view(design_view)
    interaction_view = _build_interaction_view(
        normalized_use_cases,
        normalized_actors,
        interface_objects,
    )
    _stamp_semantic_identity(
        interaction_view["realization_objects"],
        change_source="derived_interaction_view",
    )
    for realization in interaction_view["realization_objects"]:
        _stamp_semantic_identity(
            realization.get("step_objects", []),
            change_source="derived_interaction_view",
        )
    _stamp_semantic_identity(
        interaction_view["message_objects"],
        change_source="derived_interaction_view",
    )
    traceability = _build_trace_links(
        all_requirement_objects,
        normalized_use_cases,
        use_case_step_objects,
        domain_entity_objects,
        business_rule_objects,
        state_entity_objects,
        state_transition_objects,
        component_objects,
        interaction_view["message_objects"],
    )
    _bind_use_case_supporting_links(
        normalized_use_cases,
        all_requirement_objects,
        traceability,
    )
    traceability["artifact_lineage"] = _build_artifact_lineage(
        risk_objects,
        all_requirement_objects,
        normalized_use_cases,
        scenario_objects,
        domain_entity_objects,
        relationship_objects,
        business_rule_objects,
        state_entity_objects,
        state_transition_objects,
        trigger_objects,
        component_objects,
        interface_objects,
        runtime_boundary_objects,
        interaction_view["realization_objects"],
        interaction_view["message_objects"],
    )
    _stamp_semantic_identity(
        traceability["requirement_to_use_case"],
        change_source="derived_traceability",
    )
    _stamp_semantic_identity(
        traceability["requirement_to_step"],
        change_source="derived_traceability",
    )
    _stamp_semantic_identity(
        traceability["use_case_to_analysis"],
        change_source="derived_traceability",
    )
    _stamp_semantic_identity(
        traceability["step_to_interaction"],
        change_source="derived_traceability",
    )
    _stamp_semantic_identity(
        traceability["step_to_transition"],
        change_source="derived_traceability",
    )
    _stamp_semantic_identity(
        traceability["business_rule_to_transition"],
        change_source="derived_traceability",
    )
    _stamp_semantic_identity(
        traceability["analysis_to_design"],
        change_source="derived_traceability",
    )
    _stamp_semantic_identity(
        traceability["artifact_lineage"],
        change_source="derived_traceability",
    )

    model = {
        "project": {
            "name": _text_or_empty(round_1.get("idea")) or "Unnamed Project",
            "domain": "Unspecified",
            "problem_statement": _text_or_empty(round_1.get("problem")) or "Unspecified",
            "system_scope": _text_or_empty(round_1.get("in_scope")) or "Unspecified",
        },
        "business_goals": _ensure_list(round_2.get("outcomes")),
        "success_criteria": _ensure_list(round_2.get("success_criteria")),
        "risks": risk_objects,
        "actors": normalized_actors,
        "use_cases": normalized_use_cases,
        "scenarios": scenario_objects,
        "requirements": {
            "functional": _requirement_statements_by_kind(all_requirement_objects, "functional"),
            "functional_objects": functional_requirement_objects,
            "non_functional": _requirement_statements_by_kind(all_requirement_objects, "non_functional"),
            "non_functional_objects": non_functional_requirement_objects,
        },
        "analysis_view": analysis_view,
        "traceability": traceability,
        "logical_view": logical_view,
        "process_view": process_view,
        "architecture_view": architecture_view,
        "design_view": design_view,
        "interaction_view": interaction_view,
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
    model["model_metadata"] = _build_model_metadata(model)
    return model
