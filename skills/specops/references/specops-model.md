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
- `actors`
  - `id`
  - `name`
  - `type`
  - `description`
  - `complexity`: `simple`, `average`, or `complex`
- `use_cases`
  - `id`
  - `name`
  - `primary_actor`
  - `goal`
  - `complexity`: `simple`, `average`, or `complex`
  - `main_success_scenario`
  - `extensions`
- `requirements`
  - `functional`
  - `non_functional`
- `logical_view` (optional in V1, expected for V1.5+ full-spec work)
  - `domain_entities`
  - `relationships`
  - `business_rules`
- `process_view` (optional in V1, expected for V1.5+ full-spec work)
  - `state_entities`
  - `states_and_transitions`
  - `triggers_and_approvals`
- `architecture_view` (optional in V1, expected for V1.5+ full-spec work)
  - `components_and_services`
  - `interfaces_and_integrations`
  - `runtime_boundaries`
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
- `ucp-estimate.md`

For V1.5+ work, the same model should also have stable places to hold:

- logical-view discovery
- process/state-view discovery
- architecture/deployment-view discovery

If any artifact would require invented inputs, stop and surface the missing fields.
