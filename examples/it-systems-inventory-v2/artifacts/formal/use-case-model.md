# Use-Case Model

## Actors

- `business-owners` Business owners (human, complex):  [source: round 3 actors]
- `technical-owners` technical owners (human, complex):  [source: round 3 actors]
- `enterprise-architects` enterprise architects (human, complex):  [source: round 3 actors]
- `procurement` procurement (human, average):  [source: round 3 actors]
- `security` security (human, average):  [source: round 3 actors]
- `finance` finance (human, average):  [source: round 3 actors]
- `application-owners` application owners (human, complex):  [source: round 3 actors]
- `integration-system-owners` integration system owners (system, average):  [source: round 3 actors]

## Use Cases

### Register a system

- ID: `register-a-system`
- Primary actor: Unspecified
- Complexity: average
- Goal: Register a system
- Source: round 3 use_cases

#### Main Success Scenario

1. No main success scenario documented.

#### Extensions

- None

### edit metadata

- ID: `edit-metadata`
- Primary actor: Unspecified
- Complexity: simple
- Goal: edit metadata
- Source: round 3 use_cases

#### Main Success Scenario

1. No main success scenario documented.

#### Extensions

- None

### compare overlapping systems

- ID: `compare-overlapping-systems`
- Primary actor: Unspecified
- Complexity: average
- Goal: compare overlapping systems
- Source: round 3 use_cases

#### Main Success Scenario

1. No main success scenario documented.

#### Extensions

- None

### track lifecycle state

- ID: `track-lifecycle-state`
- Primary actor: Unspecified
- Complexity: average
- Goal: track lifecycle state
- Source: round 3 use_cases

#### Main Success Scenario

1. No main success scenario documented.

#### Extensions

- None

### review risks

- ID: `review-risks`
- Primary actor: Unspecified
- Complexity: simple
- Goal: review risks
- Source: round 3 use_cases

#### Main Success Scenario

1. No main success scenario documented.

#### Extensions

- None

### see costs

- ID: `see-costs`
- Primary actor: Unspecified
- Complexity: simple
- Goal: see costs
- Source: round 3 use_cases

#### Main Success Scenario

1. No main success scenario documented.

#### Extensions

- None

### approve deprecation

- ID: `approve-deprecation`
- Primary actor: Unspecified
- Complexity: average
- Goal: approve deprecation
- Source: round 3 use_cases

#### Main Success Scenario

1. No main success scenario documented.

#### Extensions

- None

### report portfolio gaps

- ID: `report-portfolio-gaps`
- Primary actor: Unspecified
- Complexity: average
- Goal: report portfolio gaps
- Source: round 3 use_cases

#### Main Success Scenario

1. No main success scenario documented.

#### Extensions

- None


## States and Transitions

- `state-transition-1` System: Proposed -> Active -> Retiring -> Retired [source: round 6 states_and_transitions]
- `state-transition-2` System: Proposed -> Active -> Retiring -> Retired [source: round 6 states_and_transitions]
- `state-transition-3` System: Proposed -> Active -> Retiring -> Retired [source: round 6 states_and_transitions]
- `state-transition-4` System: Active -> Deprecated [source: round 6 states_and_transitions]


## Triggers and Approvals

- `trigger-1` Deprecation approval requires enterprise architect review [source: round 6 triggers_and_approvals]
- `trigger-2` Contract expiry triggers lifecycle review [source: round 6 triggers_and_approvals]


## Interfaces and Integrations

- `interface-1` System Inventory Web App calls System Inventory API [source: round 7 interfaces_and_integrations]
- `interface-2` System Inventory API sends Reporting Consumers [source: round 7 interfaces_and_integrations]



## Use-Case To Analysis Traceability

- `trace-uc-analysis-1` register-a-system -> entity-system (use-case text references analysis object name)
- `trace-uc-analysis-2` register-a-system -> state-entity-system (use-case text references analysis object name)
- `trace-uc-analysis-3` compare-overlapping-systems -> entity-system (use-case text references analysis object name)
- `trace-uc-analysis-4` compare-overlapping-systems -> state-entity-system (use-case text references analysis object name)

