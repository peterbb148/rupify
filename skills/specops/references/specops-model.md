# SpecOps Model Contract

The canonical project model is `specops-model.yaml`.

## Required Sections

- `project`
  - `name`
  - `domain`
  - `problem_statement`
  - `system_scope`
- `business_goals`
- `success_criteria`
- `actors` (compatibility mirror derived from `analysis_view.actors`)
  - `id`
  - `name`
  - `type`
  - `description`
  - `model_layer`: `analysis`
  - `interaction_style`
  - `responsibilities`
  - `complexity`: `simple`, `average`, or `complex`
- `use_cases` (compatibility mirror derived from `analysis_view.use_cases`)
  - `id`
  - `name`
  - `primary_actor`
  - `primary_actor_id`
  - `supporting_actor_ids`
  - `model_layer`: `analysis`
  - `goal`
  - `trigger`
  - `preconditions`
  - `postconditions`
  - `complexity`: `simple`, `average`, or `complex`
  - `main_success_scenario`
  - `extensions`
- `requirements`
  - `functional`
  - `functional_objects`
    - `id`
    - `statement`
    - `requirement_kind`
    - `quality_attribute`
    - `model_layer`: `analysis`
    - `linked_use_case_ids`
    - `fit_criterion`
    - `trace`
  - `non_functional`
  - `non_functional_objects`
    - `id`
    - `statement`
    - `requirement_kind`
    - `quality_attribute`
    - `model_layer`: `analysis`
    - `linked_use_case_ids`
    - `fit_criterion`
    - `trace`
- `analysis_view` (authoritative source for analysis-layer objects)
  - `actors`
  - `use_cases`
  - `requirement_objects`
  - `domain_entity_objects`
  - `relationship_objects`
  - `business_rule_objects`
  - `state_entity_objects`
  - `state_transition_objects`
  - `trigger_objects`
  - `actor_ids`
  - `use_case_ids`
  - `requirement_ids`
  - `domain_entity_ids`
  - `relationship_ids`
  - `business_rule_ids`
  - `state_entity_ids`
  - `state_transition_ids`
  - `trigger_ids`
- `traceability`
  - `requirement_to_use_case`
    - `id`
    - `from_id`
    - `to_id`
    - `link_type`
    - `basis`
  - `use_case_to_analysis`
    - `id`
    - `from_id`
    - `to_id`
    - `link_type`
    - `basis`
  - `analysis_to_design`
    - `id`
    - `from_id`
    - `to_id`
    - `link_type`
    - `basis`
- `logical_view` (derived compatibility view from `analysis_view` for V1/V1.5 renderers)
  - `domain_entities`
  - `domain_entity_objects`
    - `id`
    - `name`
    - `entity_type`
    - `model_layer`: `analysis`
    - `description`
    - `attributes`
    - `responsibilities`
    - `trace`
  - `relationships`
  - `relationship_objects`
    - `id`
    - `description`
    - `relationship_type`
    - `model_layer`: `analysis`
    - `source_name`
    - `source_entity_id`
    - `target_name`
    - `target_entity_id`
    - `source_multiplicity`
    - `target_multiplicity`
    - `source_role_name`
    - `target_role_name`
    - `trace`
  - `business_rules`
  - `business_rule_objects`
    - `id`
    - `name`
    - `rule_text`
    - `model_layer`: `analysis`
    - `scope`
    - `trace`
- `process_view` (derived compatibility view from `analysis_view` for V1/V1.5 renderers)
  - `state_entities`
  - `state_entity_objects`
    - `id`
    - `name`
    - `entity_type`
    - `model_layer`: `analysis`
    - `description`
    - `states`
    - `trace`
  - `states_and_transitions`
  - `state_transition_objects`
    - `id`
    - `description`
    - `model_layer`: `analysis`
    - `state_entity_id`
    - `state_entity_name`
    - `from_state`
    - `to_state`
    - `trigger`
    - `trace`
  - `triggers_and_approvals`
  - `trigger_objects`
    - `id`
    - `event_name`
    - `outcome`
    - `description`
    - `model_layer`: `analysis`
    - `approval_required`
    - `trace`
- `design_view` (authoritative source for design-layer objects)
  - `component_objects`
  - `interface_objects`
  - `runtime_boundary_objects`
  - `component_ids`
  - `interface_ids`
  - `runtime_boundary_ids`
- `architecture_view` (derived compatibility view from `design_view` for V1/V1.5 renderers)
  - `components_and_services`
  - `component_objects`
    - `id`
    - `name`
    - `component_kind`
    - `model_layer`: `design`
    - `responsibility`
    - `runtime_environment`
    - `trace`
  - `interfaces_and_integrations`
  - `interface_objects`
    - `id`
    - `description`
    - `model_layer`: `design`
    - `source_component_name`
    - `source_component_id`
    - `target_component_name`
    - `target_component_id`
    - `interaction_verb`
    - `protocol`
    - `trace`
  - `runtime_boundaries`
  - `runtime_boundary_objects`
    - `id`
    - `name`
    - `boundary_type`
    - `description`
    - `model_layer`: `design`
    - `deployment_nodes`
    - `trace`
- `assumptions`
  - supports plain strings
  - may also use structured items with:
    - `text`
    - `status`
    - `source`
    - `last_updated`
    - `notes`
- `open_questions`
  - supports plain strings
  - may also use structured items with:
    - `text`
    - `status`
    - `source`
    - `last_updated`
    - `notes`
- `ucp`
  - `technical_factors`
  - `environmental_factors`
  - `productivity_hours_per_ucp`
- `future_placeholders`
  - `uml`
  - `formal_specification`

## Artifact Contract

The model should be rich enough to generate:

- `requirements-spec.md`
- `use-case-model.md`
- `domain-model.md`
- `state-model.md`
- `ucp-estimate.md`

For V1.5+ work, the same model should also have stable places to hold:

- logical-view discovery
- process/state-view discovery
- architecture/deployment-view discovery

For the V1.6 proof artifact, `state-model.md` is generated from the canonical process semantics:

- `analysis_view.state_entity_objects`
- `analysis_view.state_transition_objects`
- `analysis_view.trigger_objects`
- relevant `traceability.use_case_to_analysis` links for state entities
- relevant `traceability.analysis_to_design` links where a stateful analysis object is realized by a
  design component

For the first V2 domain/class artifact, `domain-model.md` is generated from the canonical logical
semantics:

- `analysis_view.domain_entity_objects`
- `analysis_view.relationship_objects`
- `analysis_view.business_rule_objects`
- relevant `traceability.use_case_to_analysis` links for domain entities

If any artifact would require invented inputs, stop and surface the missing fields.

For V1.6 hardening, `analysis_view` and `design_view` are the source of truth. The older top-level
and per-view object collections remain in the contract as compatibility mirrors for existing
renderers and fixtures, but they should be derived from the layer-owned collections rather than
maintained independently.
