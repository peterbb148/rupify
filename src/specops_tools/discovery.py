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
                    "model_layer": "analysis",
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
                    "model_layer": "analysis",
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
                "model_layer": "analysis",
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
                "model_layer": "analysis",
                "linked_use_case_ids": [],
                "fit_criterion": "",
                "trace": {},
            }
        )
    return objects


def _build_trace_links(
    requirement_objects: list[dict[str, Any]],
    use_cases: list[dict[str, Any]],
    domain_entities: list[dict[str, Any]],
    state_entities: list[dict[str, Any]],
    components: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Build conservative cross-view trace links from explicit textual references."""
    requirement_to_use_case = []
    use_case_to_analysis = []
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
        requirement["linked_use_case_ids"] = linked_use_case_ids

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

    return {
        "requirement_to_use_case": requirement_to_use_case,
        "use_case_to_analysis": use_case_to_analysis,
        "analysis_to_design": analysis_to_design,
    }


def _build_artifact_lineage(
    requirement_objects: list[dict[str, Any]],
    use_cases: list[dict[str, Any]],
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
        ("requirements-spec.md", "functional requirements", requirement_objects),
        ("use-case-model.md", "use cases", use_cases),
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

        realization_objects.append(
            {
                "id": f"interaction-realization-{index}",
                "use_case_id": use_case.get("id", ""),
                "use_case_name": use_case.get("name", ""),
                "participant_ids": participant_ids,
                "participant_names": participant_names,
                "steps": list(use_case.get("main_success_scenario", [])),
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
    all_requirement_objects = functional_requirement_objects + non_functional_requirement_objects
    analysis_view = {
        "actor_ids": [item["id"] for item in normalized_actors],
        "use_case_ids": [item["id"] for item in normalized_use_cases],
        "requirement_ids": [item["id"] for item in all_requirement_objects],
        "actors": normalized_actors,
        "use_cases": normalized_use_cases,
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
    traceability = _build_trace_links(
        all_requirement_objects,
        normalized_use_cases,
        domain_entity_objects,
        state_entity_objects,
        component_objects,
    )
    traceability["artifact_lineage"] = _build_artifact_lineage(
        all_requirement_objects,
        normalized_use_cases,
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
