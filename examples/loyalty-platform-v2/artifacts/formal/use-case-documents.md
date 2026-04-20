# Use-Case Documents

## Enroll Member

- ID: `enroll-member`
- Primary Actor: Unspecified
- Supporting Actors: None
- Priority: high
- Status: confirmed
- Content Semantics: normative
- Readiness: ready
- Complexity: simple
- Goal: Enroll Member
- Trigger: Unspecified
- Source: round 3 use_cases

### Brief Description

Enroll Member

### Preconditions

- Customer is not already enrolled

### Postconditions

- Member account exists and is active

### Extension Points

- None

### Used Use Cases

- None

### Subordinate Use Cases

- None

### Flow of Events

1. Customer opens the loyalty enrollment flow.
2. Customer provides the required details and consents.
3. System validates the submission and creates the member account.

### Extensions

- Enrollment is blocked when required consent is missing.

### Secondary Scenarios

No named scenarios documented.

### User Interface

- Member-facing responsive enrollment form with consent capture and validation messaging.

### View of Participating Classes

- `entity-member` Member [source: round 5 domain_entities]

### Sequence and Interaction Notes

#### Enroll Member

- Participants: Unspecified

##### Realization Steps

1. Customer opens the loyalty enrollment flow.
2. Customer provides the required details and consents.
3. System validates the submission and creates the member account.


### Linked Requirements

- None

### Other Artifacts

- None


## Use-Case To Analysis Traceability

- `trace-uc-analysis-1` enroll-member -> entity-member (use-case text references analysis object name)
- `trace-uc-analysis-3` redeem-reward -> entity-member (use-case text references analysis object name)



## Browse Rewards

- ID: `browse-rewards`
- Primary Actor: Unspecified
- Supporting Actors: None
- Priority: high
- Status: confirmed
- Content Semantics: normative
- Readiness: ready
- Complexity: average
- Goal: Browse Rewards
- Trigger: Unspecified
- Source: round 3 use_cases

### Brief Description

Browse Rewards

### Preconditions

- Member is enrolled

### Postconditions

- Eligible rewards and point balance are visible

### Extension Points

- None

### Used Use Cases

- None

### Subordinate Use Cases

- None

### Flow of Events

1. Customer opens the rewards catalog.
2. System displays available rewards and points balance.
3. Customer filters or sorts the catalog.

### Extensions

- Catalog view degrades if an integration is temporarily unavailable.

### Secondary Scenarios

No named scenarios documented.

### User Interface

- Reward catalog view with filters, points balance summary, and eligibility indicators.

### View of Participating Classes

- `entity-reward` Reward [source: round 5 domain_entities]

### Sequence and Interaction Notes

#### Browse Rewards

- Participants: Unspecified

##### Realization Steps

1. Customer opens the rewards catalog.
2. System displays available rewards and points balance.
3. Customer filters or sorts the catalog.


### Linked Requirements

- None

### Other Artifacts

- None


## Use-Case To Analysis Traceability

- `trace-uc-analysis-2` browse-rewards -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-4` redeem-reward -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-7` manage-reward-catalog -> entity-reward (use-case text references analysis object name)



## Redeem Reward

- ID: `redeem-reward`
- Primary Actor: Unspecified
- Supporting Actors: None
- Priority: high
- Status: confirmed
- Content Semantics: normative
- Readiness: ready
- Complexity: complex
- Goal: Redeem Reward
- Trigger: Unspecified
- Source: round 3 use_cases

### Brief Description

Redeem Reward

### Preconditions

- Member is enrolled
- Reward is available

### Postconditions

- Redemption is recorded and balance is updated

### Extension Points

- None

### Used Use Cases

- None

### Subordinate Use Cases

- None

### Flow of Events

1. Customer selects a reward.
2. System validates reward eligibility and available points.
3. System reserves the reward and updates the member balance.
4. System confirms redemption to the customer.

### Extensions

- Reward inventory is exhausted before completion.
- Customer does not have enough points.
- Payment confirmation is missing for a reward that depends on purchase completion.

### Secondary Scenarios

#### Reward Inventory Exhausted

- Summary: Redemption fails because no reward inventory remains.
- Priority: high
- Status: open

##### Flow of Events

1. Customer selects a reward.
2. System checks reward availability.
3. System reports that inventory is exhausted.

##### Activity Notes

- None

##### Sequence Notes

- None


#### Missing Payment Confirmation

- Summary: Redemption pauses until dependent payment confirmation arrives.
- Priority: medium
- Status: open

##### Flow of Events

1. Customer selects a reward.
2. System requests payment confirmation.
3. System blocks fulfillment until confirmation arrives.

##### Activity Notes

- None

##### Sequence Notes

- None


### User Interface

- Reward detail and redemption confirmation flow with explicit failure states.

### View of Participating Classes

- `entity-member` Member [source: round 5 domain_entities]
- `entity-reward` Reward [source: round 5 domain_entities]
- `entity-redemption` Redemption [source: round 5 domain_entities]
- `state-entity-redemption` Redemption [source: round 6 state_entities]

### Sequence and Interaction Notes

#### Redeem Reward

- Participants: Unspecified

##### Realization Steps

1. Customer selects a reward.
2. System validates reward eligibility and available points.
3. System reserves the reward and updates the member balance.
4. System confirms redemption to the customer.


### Linked Requirements

- `non_functional-requirement-6` The system must allow members to redeem rewards when eligibility conditions are satisfied. [source: round 4 non_functional_requirements]

### Other Artifacts

- None


## Use-Case To Analysis Traceability

- `trace-uc-analysis-1` enroll-member -> entity-member (use-case text references analysis object name)
- `trace-uc-analysis-2` browse-rewards -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-3` redeem-reward -> entity-member (use-case text references analysis object name)
- `trace-uc-analysis-4` redeem-reward -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-5` redeem-reward -> entity-redemption (use-case text references analysis object name)
- `trace-uc-analysis-6` redeem-reward -> state-entity-redemption (use-case text references analysis object name)
- `trace-uc-analysis-7` manage-reward-catalog -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-9` review-redemption-analytics -> entity-redemption (use-case text references analysis object name)
- `trace-uc-analysis-10` review-redemption-analytics -> state-entity-redemption (use-case text references analysis object name)



## Manage Reward Catalog

- ID: `manage-reward-catalog`
- Primary Actor: Unspecified
- Supporting Actors: None
- Priority: medium
- Status: confirmed
- Content Semantics: normative
- Readiness: ready
- Complexity: average
- Goal: Manage Reward Catalog
- Trigger: Unspecified
- Source: round 3 use_cases

### Brief Description

Manage Reward Catalog

### Preconditions

- Operations Manager is authenticated

### Postconditions

- Reward catalog change is published

### Extension Points

- None

### Used Use Cases

- None

### Subordinate Use Cases

- None

### Flow of Events

1. Operations Manager opens catalog administration.
2. Operations Manager updates reward configuration.
3. System validates and publishes the change.

### Extensions

- A change is rejected because it would make an active reward invalid.

### Secondary Scenarios

#### Invalid Catalog Change

- Summary: Publication is rejected because the new reward configuration would break an active offer.
- Priority: medium
- Status: open

##### Flow of Events

1. Operations Manager updates reward configuration.
2. System validates the change.
3. System rejects the invalid change.

##### Activity Notes

- None

##### Sequence Notes

- None


### User Interface

- Back-office catalog editor with validation messages before publish.

### View of Participating Classes

- `entity-reward` Reward [source: round 5 domain_entities]

### Sequence and Interaction Notes

#### Manage Reward Catalog

- Participants: Unspecified

##### Realization Steps

1. Operations Manager opens catalog administration.
2. Operations Manager updates reward configuration.
3. System validates and publishes the change.


### Linked Requirements

- None

### Other Artifacts

- None


## Use-Case To Analysis Traceability

- `trace-uc-analysis-2` browse-rewards -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-4` redeem-reward -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-7` manage-reward-catalog -> entity-reward (use-case text references analysis object name)



## Review Redemption Analytics

- ID: `review-redemption-analytics`
- Primary Actor: Unspecified
- Supporting Actors: None
- Priority: medium
- Status: confirmed
- Content Semantics: normative
- Readiness: ready
- Complexity: simple
- Goal: Review Redemption Analytics
- Trigger: Unspecified
- Source: round 3 use_cases

### Brief Description

Review Redemption Analytics

### Preconditions

- Reporting data is available

### Postconditions

- Operations Manager can inspect campaign and redemption metrics

### Extension Points

- None

### Used Use Cases

- None

### Subordinate Use Cases

- None

### Flow of Events

1. Operations Manager opens the analytics dashboard.
2. System shows redemption and campaign metrics.

### Extensions

- A reporting data source is delayed.

### Secondary Scenarios

#### Reporting Delay

- Summary: Analytics view is partial because a reporting source is delayed.
- Priority: low
- Status: open

##### Flow of Events

1. Operations Manager opens the analytics dashboard.
2. System detects delayed reporting data.
3. System shows a partial-data warning.

##### Activity Notes

- None

##### Sequence Notes

- None


### User Interface

- Operational dashboard summarizing redemptions, campaigns, and freshness warnings.

### View of Participating Classes

- `entity-campaign` Campaign [source: round 5 domain_entities]
- `entity-redemption` Redemption [source: round 5 domain_entities]
- `state-entity-redemption` Redemption [source: round 6 state_entities]

### Sequence and Interaction Notes

#### Review Redemption Analytics

- Participants: Unspecified

##### Realization Steps

1. Operations Manager opens the analytics dashboard.
2. System shows redemption and campaign metrics.


### Linked Requirements

- None

### Other Artifacts

- None


## Use-Case To Analysis Traceability

- `trace-uc-analysis-5` redeem-reward -> entity-redemption (use-case text references analysis object name)
- `trace-uc-analysis-6` redeem-reward -> state-entity-redemption (use-case text references analysis object name)
- `trace-uc-analysis-8` review-redemption-analytics -> entity-campaign (use-case text references analysis object name)
- `trace-uc-analysis-9` review-redemption-analytics -> entity-redemption (use-case text references analysis object name)
- `trace-uc-analysis-10` review-redemption-analytics -> state-entity-redemption (use-case text references analysis object name)



## Artifact Lineage

- `trace-artifact-use-case-documents-use-case-documents-enroll-member` enroll-member -> use-case-documents.md#use-case documents (canonical use-case documents object renders into use-case-documents.md)
- `trace-artifact-use-case-documents-use-case-documents-browse-rewards` browse-rewards -> use-case-documents.md#use-case documents (canonical use-case documents object renders into use-case-documents.md)
- `trace-artifact-use-case-documents-use-case-documents-redeem-reward` redeem-reward -> use-case-documents.md#use-case documents (canonical use-case documents object renders into use-case-documents.md)
- `trace-artifact-use-case-documents-use-case-documents-manage-reward-catalog` manage-reward-catalog -> use-case-documents.md#use-case documents (canonical use-case documents object renders into use-case-documents.md)
- `trace-artifact-use-case-documents-use-case-documents-review-redemption-analytics` review-redemption-analytics -> use-case-documents.md#use-case documents (canonical use-case documents object renders into use-case-documents.md)
- `trace-artifact-use-case-documents-scenario-summaries-scenario-reward-inventory-exhausted` scenario-reward-inventory-exhausted -> use-case-documents.md#scenario summaries (canonical scenario summaries object renders into use-case-documents.md)
- `trace-artifact-use-case-documents-scenario-summaries-scenario-missing-payment-confirmation` scenario-missing-payment-confirmation -> use-case-documents.md#scenario summaries (canonical scenario summaries object renders into use-case-documents.md)
- `trace-artifact-use-case-documents-scenario-summaries-scenario-invalid-catalog-change` scenario-invalid-catalog-change -> use-case-documents.md#scenario summaries (canonical scenario summaries object renders into use-case-documents.md)
- `trace-artifact-use-case-documents-scenario-summaries-scenario-reporting-delay` scenario-reporting-delay -> use-case-documents.md#scenario summaries (canonical scenario summaries object renders into use-case-documents.md)

