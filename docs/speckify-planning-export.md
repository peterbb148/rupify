# Speckify Planning Export

Rupify now exposes a dedicated machine-oriented planning export for downstream Speckify consumption.

## Purpose

The canonical model remains the source of truth inside Rupify. The planning export is a stricter
downstream contract that:

- flattens planning-relevant canonical elements into one machine-friendly `elements` collection
- preserves stable ids through `id`, `semantic_id`, and `change_metadata`
- carries element-level `content_semantics` and `readiness_status`
- exposes `ready_normative_elements` so downstream tools can consume only defensible planning inputs
- preserves flattened `trace_links` and `blocking_ambiguities`

## CLI

```bash
uv run rupify-export-planning \
  --model examples/it-systems-inventory/rupify-model.json \
  --output /tmp/rupify-planning-export.json
```

## Export Shape

- `export_metadata`
  - `schema_version`
  - `export_kind`
  - `source_model_semantic_id`
  - `source_model_change_metadata`
- `summary`
  - `element_count`
  - `trace_link_count`
  - `ready_normative_count`
  - `blocking_ambiguity_count`
  - `ready_normative_ids`
  - `partial_or_blocked_normative_ids`
  - `blocking_ambiguity_ids`
- `elements`
  - flat machine-oriented element records with:
    - `id`
    - `semantic_id`
    - `family`
    - `name`
    - `text`
    - `content_semantics`
    - `readiness_status`
    - `normative_ready`
    - `missing_fields`
    - `blocking_ambiguity_ids`
    - `source_round`
    - `source_key`
    - `change_metadata`
    - `attributes`
- `ready_normative_elements`
  - the ready subset of `elements` where `content_semantics == normative`
- `blocking_ambiguities`
  - the ambiguity subset that explicitly blocks downstream planning
- `trace_links`
  - flattened traceability and artifact lineage records

## Contract Guidance

- Speckify should prefer `ready_normative_elements` when selecting decomposition inputs.
- `elements` should still be retained for context, partial markers, and auditability.
- `trace_links` should be treated as the canonical link surface for downstream graph traversal.
- `blocking_ambiguities` should be treated as explicit stop conditions, not hidden warnings.
