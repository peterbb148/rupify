# Requirements Specification

## Project

- Name: A system to manage inventory of IT Systems themselves.
- Domain: Unspecified
- Scope: All IT systems

## Problem Statement

We have many IT Systems and some overlap, some are free, some are expensive, all are slightly different.

## Business Goals

- Better planning of IT systems purchasing and life cycle

## Success Criteria

- Better planning of IT systems purchasing and life cycle

## Functional Requirements

- Yes business processes like stage gates and approval states must be supported
- I think this will be the CMDB for IT Applications/systems - we need to be able to export data to various system for reporting.

## Non-Functional Requirements

- UI must be web based
- SSO
- role-based access
- audit trail
- search
- filtering
- performance (regular >1s for web page rendering)
- availability >=99%

## Acceptance Constraints

- `acceptance-constraint-requirement-1` UI must be web based (semantics: normative; kind: non_functional_requirement; requirement: non_functional-requirement-1; readiness: ready; source: round 2 constraints)
- `acceptance-constraint-requirement-2` SSO (semantics: normative; kind: non_functional_requirement; requirement: non_functional-requirement-2; readiness: blocked; source: round 4 non_functional_requirements)
- `acceptance-constraint-requirement-3` role-based access (semantics: normative; kind: non_functional_requirement; requirement: non_functional-requirement-3; readiness: blocked; source: round 4 non_functional_requirements)
- `acceptance-constraint-requirement-4` audit trail (semantics: normative; kind: non_functional_requirement; requirement: non_functional-requirement-4; readiness: blocked; source: round 4 non_functional_requirements)
- `acceptance-constraint-requirement-5` search (semantics: normative; kind: non_functional_requirement; requirement: non_functional-requirement-5; readiness: blocked; source: round 4 non_functional_requirements)
- `acceptance-constraint-requirement-6` filtering (semantics: normative; kind: non_functional_requirement; requirement: non_functional-requirement-6; readiness: blocked; source: round 4 non_functional_requirements)
- `acceptance-constraint-requirement-7` performance (regular >1s for web page rendering) (semantics: normative; kind: non_functional_requirement; requirement: non_functional-requirement-7; readiness: ready; source: round 4 non_functional_requirements)
- `acceptance-constraint-requirement-8` availability >=99% (semantics: normative; kind: non_functional_requirement; requirement: non_functional-requirement-8; readiness: ready; source: round 4 non_functional_requirements)
- `acceptance-constraint-success-1` Better planning of IT systems purchasing and life cycle (semantics: normative; kind: success_criterion; readiness: blocked; source: round 2 success_criteria)


## Logical View

- `entity-system` System [source: round 5 domain_entities]
- `entity-risk-assessment` Risk Assessment [source: round 5 domain_entities]
- `entity-cost-record` Cost Record [source: round 5 domain_entities]
- `entity-capability` Capability [source: round 5 domain_entities]
- `entity-contract` Contract [source: round 5 domain_entities]
- `entity-integration` Integration [source: round 5 domain_entities]


## Relationships

- `relationship-1` A System has one Business Owner [source: round 5 relationships]
- `relationship-2` A System has one Technical Owner [source: round 5 relationships]
- `relationship-3` A System has many Integrations [source: round 5 relationships]
- `relationship-4` A System has many Capabilities [source: round 5 relationships]
- `relationship-5` A System has one Contract [source: round 5 relationships]
- `relationship-6` A System has many Risk Assessments [source: round 5 relationships]
- `relationship-7` A System has many Cost Records [source: round 5 relationships]


## Business Rules

- `business-rule-1` A System must have a business owner before it becomes Active. [source: round 5 business_rules]
- `business-rule-2` A System lifecycle state change requires approval for deprecation. [source: round 5 business_rules]
- `business-rule-3` A System must record vendor and contract dates. [source: round 5 business_rules]


## Process View

- `state-entity-system` System {states: Proposed, Active, Retiring, Retired, Deprecated} [source: round 6 state_entities]


## States and Transitions

- `state-transition-1` System: Proposed -> Active -> Retiring -> Retired [source: round 6 states_and_transitions]
- `state-transition-2` System: Proposed -> Active -> Retiring -> Retired [source: round 6 states_and_transitions]
- `state-transition-3` System: Proposed -> Active -> Retiring -> Retired [source: round 6 states_and_transitions]
- `state-transition-4` System: Active -> Deprecated [source: round 6 states_and_transitions]


## Triggers and Approvals

- `trigger-1` Deprecation approval requires enterprise architect review [source: round 6 triggers_and_approvals]
- `trigger-2` Contract expiry triggers lifecycle review [source: round 6 triggers_and_approvals]


## Architecture View

- `component-system-inventory-web-app` System Inventory Web App [source: round 7 components_and_services]
- `component-system-inventory-api` System Inventory API [source: round 7 components_and_services]
- `component-reporting-consumers` Reporting Consumers [source: round 7 components_and_services]


## Interfaces and Integrations

- `interface-1` System Inventory Web App calls System Inventory API [source: round 7 interfaces_and_integrations]
- `interface-2` System Inventory API sends Reporting Consumers [source: round 7 interfaces_and_integrations]


## Runtime Boundaries

- `runtime-boundary-1` System Inventory API runs separately from the UI [source: round 7 runtime_boundaries]



## Use-Case To Analysis Traceability

- `trace-uc-analysis-1` register-a-system -> entity-system (use-case text references analysis object name)
- `trace-uc-analysis-2` register-a-system -> state-entity-system (use-case text references analysis object name)
- `trace-uc-analysis-3` compare-overlapping-systems -> entity-system (use-case text references analysis object name)
- `trace-uc-analysis-4` compare-overlapping-systems -> state-entity-system (use-case text references analysis object name)


## Analysis To Design Traceability

- `trace-analysis-design-1` entity-system -> component-system-inventory-web-app (design component name references analysis object name)
- `trace-analysis-design-2` entity-system -> component-system-inventory-api (design component name references analysis object name)
- `trace-analysis-design-3` state-entity-system -> component-system-inventory-web-app (design component name references analysis object name)
- `trace-analysis-design-4` state-entity-system -> component-system-inventory-api (design component name references analysis object name)



## Assumptions

- None

## Open Questions

- None
