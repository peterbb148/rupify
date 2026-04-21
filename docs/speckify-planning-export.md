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
    - optional `obligations` for requirement elements where Rupify has explicit normalized
      requirement sub-obligations
      - `id`
      - `title`
      - `summary`
      - `acceptance`
      - `parent_requirement_id`
      - `parent_requirement_semantic_id`
    - optional `sub_actions` for use-case step elements where Rupify has explicit normalized
      step sub-actions
      - `id`
      - `semantic_id`
      - `title`
      - `text`
      - `subject`
      - `verb`
      - `target`
      - `order_index`
      - `parent_step_id`
      - `parent_step_semantic_id`
      - `parent_use_case_id`
      - `derivation_basis`
    - optional `guard_parts` for guard-condition elements where Rupify has explicit normalized
      guard structure
      - `id`
      - `semantic_id`
      - `part_kind`
      - `text`
      - `order_index`
      - `parent_guard_id`
      - `parent_guard_semantic_id`
      - `derivation_basis`
    - optional `invariant_clauses` for invariant elements where Rupify has explicit normalized
      invariant clause structure
      - `id`
      - `semantic_id`
      - `clause_kind`
      - `title`
      - `text`
      - `order_index`
      - `parent_invariant_id`
      - `parent_invariant_semantic_id`
      - `derivation_basis`
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
- `obligations` should be consumed only when present; Speckify should fail closed rather than
  inferring additional sub-obligations by splitting requirement prose downstream.
- `sub_actions` should be consumed only when present; Speckify should fail closed rather than
  inferring internal step decomposition from step prose downstream.
- `guard_parts` should be consumed only when present; Speckify should fail closed rather than
  inferring guard structure from free-text guard descriptions downstream.
- `invariant_clauses` should be consumed only when present; Speckify should fail closed rather than
  inferring invariant structure from broad rule prose downstream.
