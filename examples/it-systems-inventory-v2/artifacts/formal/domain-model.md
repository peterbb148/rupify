# Domain Model

## Project

- Name: A system to manage inventory of IT Systems themselves.
- Domain: Unspecified

## Scope

All IT systems

## Domain Entities

- `entity-system` System [source: round 5 domain_entities]
- `entity-risk-assessment` Risk Assessment [source: round 5 domain_entities]
- `entity-cost-record` Cost Record [source: round 5 domain_entities]
- `entity-capability` Capability [source: round 5 domain_entities]
- `entity-contract` Contract [source: round 5 domain_entities]
- `entity-integration` Integration [source: round 5 domain_entities]


## Relationships

- `relationship-1` A System has one Business Owner [source: round 5 relationships]
- `relationship-2` A System has one Technical Owner [source: round 5 relationships]
- `relationship-3` A System has many Integrations (multiplicity: 1 -> *; roles: integrations / a_system) [source: round 5 relationships]
- `relationship-4` A System has many Capabilities (multiplicity: 1 -> *; roles: capabilities / a_system) [source: round 5 relationships]
- `relationship-5` A System has one Contract [source: round 5 relationships]
- `relationship-6` A System has many Risk Assessments (multiplicity: 1 -> *; roles: risk_assessments / a_system) [source: round 5 relationships]
- `relationship-7` A System has many Cost Records (multiplicity: 1 -> *; roles: cost_records / a_system) [source: round 5 relationships]


## Business Rules

- `business-rule-1` A System must have a business owner before it becomes Active. [source: round 5 business_rules]
- `business-rule-2` A System lifecycle state change requires approval for deprecation. [source: round 5 business_rules]
- `business-rule-3` A System must record vendor and contract dates. [source: round 5 business_rules]


## Domain Invariants

- `domain-invariant-1` A System must have a business owner before it becomes Active. (semantics: normative; business rule: business-rule-1; scope: entity-system; readiness: ready; source: round 5 business_rules)
- `domain-invariant-2` A System lifecycle state change requires approval for deprecation. (semantics: normative; business rule: business-rule-2; scope: entity-system; readiness: ready; source: round 5 business_rules)
- `domain-invariant-3` A System must record vendor and contract dates. (semantics: normative; business rule: business-rule-3; scope: entity-system, entity-contract; readiness: ready; source: round 5 business_rules)


## Use-Case To Domain Traceability

- `trace-uc-analysis-1` register-a-system -> entity-system (use-case text references analysis object name)
- `trace-uc-analysis-3` compare-overlapping-systems -> entity-system (use-case text references analysis object name)


## Domain Invariant To Entity Traceability

- `trace-domain-invariant-entity-1` domain-invariant-1 -> entity-system (domain invariant scope references domain entity)
- `trace-domain-invariant-entity-2` domain-invariant-2 -> entity-system (domain invariant scope references domain entity)
- `trace-domain-invariant-entity-3` domain-invariant-3 -> entity-system (domain invariant scope references domain entity)
- `trace-domain-invariant-entity-4` domain-invariant-3 -> entity-contract (domain invariant scope references domain entity)



## Artifact Lineage

- `trace-artifact-domain-model-domain-entities-entity-system` entity-system -> domain-model.md#domain entities (canonical domain entities object renders into domain-model.md)
- `trace-artifact-domain-model-domain-entities-entity-risk-assessment` entity-risk-assessment -> domain-model.md#domain entities (canonical domain entities object renders into domain-model.md)
- `trace-artifact-domain-model-domain-entities-entity-cost-record` entity-cost-record -> domain-model.md#domain entities (canonical domain entities object renders into domain-model.md)
- `trace-artifact-domain-model-domain-entities-entity-capability` entity-capability -> domain-model.md#domain entities (canonical domain entities object renders into domain-model.md)
- `trace-artifact-domain-model-domain-entities-entity-contract` entity-contract -> domain-model.md#domain entities (canonical domain entities object renders into domain-model.md)
- `trace-artifact-domain-model-domain-entities-entity-integration` entity-integration -> domain-model.md#domain entities (canonical domain entities object renders into domain-model.md)
- `trace-artifact-domain-model-relationships-relationship-1` relationship-1 -> domain-model.md#relationships (canonical relationships object renders into domain-model.md)
- `trace-artifact-domain-model-relationships-relationship-2` relationship-2 -> domain-model.md#relationships (canonical relationships object renders into domain-model.md)
- `trace-artifact-domain-model-relationships-relationship-3` relationship-3 -> domain-model.md#relationships (canonical relationships object renders into domain-model.md)
- `trace-artifact-domain-model-relationships-relationship-4` relationship-4 -> domain-model.md#relationships (canonical relationships object renders into domain-model.md)
- `trace-artifact-domain-model-relationships-relationship-5` relationship-5 -> domain-model.md#relationships (canonical relationships object renders into domain-model.md)
- `trace-artifact-domain-model-relationships-relationship-6` relationship-6 -> domain-model.md#relationships (canonical relationships object renders into domain-model.md)
- `trace-artifact-domain-model-relationships-relationship-7` relationship-7 -> domain-model.md#relationships (canonical relationships object renders into domain-model.md)
- `trace-artifact-domain-model-business-rules-business-rule-1` business-rule-1 -> domain-model.md#business rules (canonical business rules object renders into domain-model.md)
- `trace-artifact-domain-model-business-rules-business-rule-2` business-rule-2 -> domain-model.md#business rules (canonical business rules object renders into domain-model.md)
- `trace-artifact-domain-model-business-rules-business-rule-3` business-rule-3 -> domain-model.md#business rules (canonical business rules object renders into domain-model.md)
- `trace-artifact-domain-model-domain-invariants-domain-invariant-1` domain-invariant-1 -> domain-model.md#domain invariants (canonical domain invariants object renders into domain-model.md)
- `trace-artifact-domain-model-domain-invariants-domain-invariant-2` domain-invariant-2 -> domain-model.md#domain invariants (canonical domain invariants object renders into domain-model.md)
- `trace-artifact-domain-model-domain-invariants-domain-invariant-3` domain-invariant-3 -> domain-model.md#domain invariants (canonical domain invariants object renders into domain-model.md)

