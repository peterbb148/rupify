"""Structured round-trip feedback contract for downstream corrections."""

from __future__ import annotations

from typing import Any


VALID_FEEDBACK_CATEGORIES = {
    "clarify",
    "split",
    "merge",
    "revise_invariant",
    "revise_transition",
    "add_missing_requirement",
    "contradiction_detected",
}

VALID_PROPOSAL_STATUSES = {"proposed", "accepted", "rejected", "superseded"}


def _normalized_string_list(value: Any) -> list[str]:
    """Return a normalized list of non-empty strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _normalize_proposed_changes(items: Any) -> list[dict[str, str]]:
    """Return normalized proposed change operations."""
    if items is None:
        return []
    normalized_items = items if isinstance(items, list) else [items]
    results = []
    for item in normalized_items:
        if not isinstance(item, dict):
            raise TypeError("Proposed changes must be mappings.")
        operation = str(item.get("operation", "")).strip() or "revise"
        field_path = str(item.get("field_path", "")).strip()
        value = str(item.get("value", "")).strip()
        rationale = str(item.get("rationale", "")).strip()
        if not field_path:
            raise ValueError("Proposed changes must include a non-empty field_path.")
        results.append(
            {
                "operation": operation,
                "field_path": field_path,
                "value": value,
                "rationale": rationale,
            }
        )
    return results


def _normalize_feedback_item(item: dict[str, Any], index: int) -> dict[str, Any]:
    """Normalize one feedback proposal item."""
    category = str(item.get("category", "")).strip()
    if category not in VALID_FEEDBACK_CATEGORIES:
        raise ValueError(f"Unsupported feedback category: {category or '<empty>'}")

    title = str(item.get("title", "")).strip()
    description = str(item.get("description", "")).strip()
    if not title:
        raise ValueError("Feedback items must include a non-empty title.")
    if not description:
        raise ValueError("Feedback items must include a non-empty description.")

    target_semantic_ids = _normalized_string_list(item.get("target_semantic_ids"))
    if not target_semantic_ids:
        raise ValueError("Feedback items must include at least one target semantic id.")

    proposal_status = str(item.get("proposal_status", "")).strip() or "proposed"
    if proposal_status not in VALID_PROPOSAL_STATUSES:
        raise ValueError(f"Unsupported proposal status: {proposal_status}")

    return {
        "id": str(item.get("id", "")).strip() or f"feedback-{category}-{index}",
        "category": category,
        "title": title,
        "description": description,
        "target_semantic_ids": target_semantic_ids,
        "target_change_hashes": _normalized_string_list(item.get("target_change_hashes")),
        "target_families": _normalized_string_list(item.get("target_families")),
        "proposal_status": proposal_status,
        "blocking_for_downstream": bool(item.get("blocking_for_downstream", False)),
        "priority": str(item.get("priority", "")).strip(),
        "encountered_in": str(item.get("encountered_in", "")).strip(),
        "downstream_evidence": _normalized_string_list(item.get("downstream_evidence")),
        "related_element_ids": _normalized_string_list(item.get("related_element_ids")),
        "related_trace_link_ids": _normalized_string_list(item.get("related_trace_link_ids")),
        "proposed_changes": _normalize_proposed_changes(item.get("proposed_changes")),
        "requested_action": str(item.get("requested_action", "")).strip(),
        "notes": str(item.get("notes", "")).strip(),
    }


def normalize_feedback_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize a downstream feedback payload into the strict feedback contract."""
    if not isinstance(payload, dict):
        raise TypeError("Feedback payload must be a mapping.")

    metadata = payload.get("feedback_metadata", {})
    if metadata and not isinstance(metadata, dict):
        raise TypeError("feedback_metadata must be a mapping when provided.")

    source_planning_export = payload.get("source_planning_export", {})
    if source_planning_export and not isinstance(source_planning_export, dict):
        raise TypeError("source_planning_export must be a mapping when provided.")

    raw_items = payload.get("feedback_items", [])
    if not isinstance(raw_items, list):
        raise TypeError("feedback_items must be a list.")

    feedback_items = [
        _normalize_feedback_item(item, index)
        for index, item in enumerate(raw_items, 1)
    ]
    feedback_items.sort(key=lambda item: (item["category"], item["id"]))

    category_counts: dict[str, int] = {}
    for item in feedback_items:
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1

    return {
        "feedback_metadata": {
            "schema_version": 1,
            "feedback_kind": "speckify_feedback",
            "source_model_semantic_id": str(metadata.get("source_model_semantic_id", "")).strip(),
            "source_model_change_hash": str(metadata.get("source_model_change_hash", "")).strip(),
            "source_planning_export_semantic_id": str(
                source_planning_export.get("source_planning_export_semantic_id", "")
                or metadata.get("source_planning_export_semantic_id", "")
            ).strip(),
            "source_planning_export_change_hash": str(
                source_planning_export.get("source_planning_export_change_hash", "")
                or metadata.get("source_planning_export_change_hash", "")
            ).strip(),
            "emitted_by": str(metadata.get("emitted_by", "")).strip(),
            "emitted_at": str(metadata.get("emitted_at", "")).strip(),
            "proposal_only": True,
        },
        "summary": {
            "feedback_item_count": len(feedback_items),
            "blocking_item_count": sum(1 for item in feedback_items if item["blocking_for_downstream"]),
            "categories": category_counts,
            "target_semantic_ids": sorted(
                {
                    semantic_id
                    for item in feedback_items
                    for semantic_id in item["target_semantic_ids"]
                }
            ),
        },
        "feedback_items": feedback_items,
    }
