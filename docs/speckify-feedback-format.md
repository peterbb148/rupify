# Speckify Feedback Format

Rupify now defines a structured round-trip feedback artifact for downstream corrections discovered
during decomposition or implementation.

## Purpose

The feedback artifact is proposal-only. It does not rewrite the Rupify model directly.

It exists so Speckify can:

- point back to upstream `semantic_id` values and known change hashes
- describe what downstream work discovered
- propose an upstream correction in a machine-readable form
- keep reversibility auditable instead of relying on prose comments

## CLI

```bash
uv run rupify-normalize-feedback \
  --input tests/fixtures/speckify_feedback_example.json \
  --output /tmp/rupify-feedback.json
```

## Feedback Shape

- `feedback_metadata`
  - `schema_version`
  - `feedback_kind`
  - `source_model_semantic_id`
  - `source_model_change_hash`
  - `source_planning_export_semantic_id`
  - `source_planning_export_change_hash`
  - `emitted_by`
  - `emitted_at`
  - `proposal_only`
- `summary`
  - `feedback_item_count`
  - `blocking_item_count`
  - `categories`
  - `target_semantic_ids`
- `feedback_items`
  - flat proposal items with:
    - `id`
    - `category`
    - `title`
    - `description`
    - `target_semantic_ids`
    - `target_change_hashes`
    - `target_families`
    - `proposal_status`
    - `blocking_for_downstream`
    - `priority`
    - `encountered_in`
    - `downstream_evidence`
    - `related_element_ids`
    - `related_trace_link_ids`
    - `proposed_changes`
      - `operation`
      - `field_path`
      - `value`
      - `rationale`
    - `requested_action`
    - `notes`

## Supported Categories

- `clarify`
- `split`
- `merge`
- `revise_invariant`
- `revise_transition`
- `add_missing_requirement`
- `contradiction_detected`

## Contract Guidance

- Speckify should emit feedback items as proposals, never direct model rewrites.
- `target_semantic_ids` should reference upstream semantic ids from the planning export or model.
- `target_change_hashes` should be included when downstream work depends on a specific upstream version.
- `blocking_for_downstream` should be set only when the issue materially prevents safe decomposition.
- `proposed_changes` should describe the suggested correction, not an automatic patch to apply.
