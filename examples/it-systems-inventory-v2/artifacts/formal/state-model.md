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


## State Invariants

- `state-invariant-1` A System must have a business owner before it becomes Active. (semantics: normative; business rule: business-rule-1; states: state-entity-system; readiness: ready; source: round 5 business_rules)
- `state-invariant-2` A System lifecycle state change requires approval for deprecation. (semantics: normative; business rule: business-rule-2; states: state-entity-system; readiness: ready; source: round 5 business_rules)
- `state-invariant-3` A System must record vendor and contract dates. (semantics: normative; business rule: business-rule-3; states: state-entity-system; readiness: ready; source: round 5 business_rules)


## Guard Conditions

- `guard-condition-1` Deprecation approval requires enterprise architect review (semantics: normative; trigger: trigger-1; readiness: blocked; source: round 6 triggers_and_approvals)
- `guard-condition-2` Contract expiry triggers lifecycle review (semantics: normative; trigger: trigger-2; readiness: blocked; source: round 6 triggers_and_approvals)



## Use-Case To State Traceability

- `trace-uc-analysis-2` register-a-system -> state-entity-system (use-case text references analysis object name)
- `trace-uc-analysis-4` compare-overlapping-systems -> state-entity-system (use-case text references analysis object name)


## State Invariant To State Traceability

- `trace-state-invariant-state-1` state-invariant-1 -> state-entity-system (state invariant scope references state entity)
- `trace-state-invariant-state-2` state-invariant-2 -> state-entity-system (state invariant scope references state entity)
- `trace-state-invariant-state-3` state-invariant-3 -> state-entity-system (state invariant scope references state entity)




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
- `trace-artifact-state-model-state-invariants-state-invariant-1` state-invariant-1 -> state-model.md#state invariants (canonical state invariants object renders into state-model.md)
- `trace-artifact-state-model-state-invariants-state-invariant-2` state-invariant-2 -> state-model.md#state invariants (canonical state invariants object renders into state-model.md)
- `trace-artifact-state-model-state-invariants-state-invariant-3` state-invariant-3 -> state-model.md#state invariants (canonical state invariants object renders into state-model.md)
- `trace-artifact-state-model-guard-conditions-guard-condition-1` guard-condition-1 -> state-model.md#guard conditions (canonical guard conditions object renders into state-model.md)
- `trace-artifact-state-model-guard-conditions-guard-condition-2` guard-condition-2 -> state-model.md#guard conditions (canonical guard conditions object renders into state-model.md)

