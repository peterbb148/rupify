# State Model

## Project

- Name: A system to manage inventory of IT Systems themselves.
- Domain: Unspecified

## Scope

All IT systems

## State Entities

- `state-entity-system` System {states: Proposed, Active, Retiring, Retired, Deprecated} [source: round 6 state_entities]


## State Transitions

- `state-transition-1` Proposed -> Active (entity: System) [source: round 6 states_and_transitions]
- `state-transition-2` Active -> Retiring (entity: System) [source: round 6 states_and_transitions]
- `state-transition-3` Retiring -> Retired (entity: System) [source: round 6 states_and_transitions]
- `state-transition-4` Active -> Deprecated (entity: System) [source: round 6 states_and_transitions]


## Triggers and Approvals

- `trigger-1` Deprecation approval requires enterprise architect review (event: Deprecation approval; type: approval; approval required) [source: round 6 triggers_and_approvals]
- `trigger-2` Contract expiry triggers lifecycle review (event: Contract expiry; type: event) [source: round 6 triggers_and_approvals]


## Use-Case To State Traceability

- `trace-uc-analysis-2` register-a-system -> state-entity-system (use-case text references analysis object name)
- `trace-uc-analysis-4` compare-overlapping-systems -> state-entity-system (use-case text references analysis object name)


## State To Design Traceability

- `trace-analysis-design-1` entity-system -> component-system-inventory-web-app (design component name references analysis object name)
- `trace-analysis-design-2` entity-system -> component-system-inventory-api (design component name references analysis object name)
- `trace-analysis-design-3` state-entity-system -> component-system-inventory-web-app (design component name references analysis object name)
- `trace-analysis-design-4` state-entity-system -> component-system-inventory-api (design component name references analysis object name)


## Artifact Lineage

- `trace-artifact-state-model-state-entities-state-entity-system` state-entity-system -> state-model.md#state entities (canonical state entities object renders into state-model.md)
- `trace-artifact-state-model-state-transitions-state-transition-1` state-transition-1 -> state-model.md#state transitions (canonical state transitions object renders into state-model.md)
- `trace-artifact-state-model-state-transitions-state-transition-2` state-transition-2 -> state-model.md#state transitions (canonical state transitions object renders into state-model.md)
- `trace-artifact-state-model-state-transitions-state-transition-3` state-transition-3 -> state-model.md#state transitions (canonical state transitions object renders into state-model.md)
- `trace-artifact-state-model-state-transitions-state-transition-4` state-transition-4 -> state-model.md#state transitions (canonical state transitions object renders into state-model.md)
- `trace-artifact-state-model-triggers-and-approvals-trigger-1` trigger-1 -> state-model.md#triggers and approvals (canonical triggers and approvals object renders into state-model.md)
- `trace-artifact-state-model-triggers-and-approvals-trigger-2` trigger-2 -> state-model.md#triggers and approvals (canonical triggers and approvals object renders into state-model.md)

