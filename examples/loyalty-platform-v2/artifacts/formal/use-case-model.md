# Use-Case Model

## Actors

- `customer` Customer (human, complex):  [source: round 3 actors]
- `operations-manager` Operations Manager (human, average):  [source: round 3 actors]
- `payment-gateway` Payment Gateway (system, simple):  [source: round 3 actors]

## Use Cases

### Enroll Member

- ID: `enroll-member`
- Primary actor: Unspecified
- Complexity: simple
- Goal: Enroll Member
- Source: round 3 use_cases

#### Main Success Scenario

1. Customer opens the loyalty enrollment flow.
2. Customer provides the required details and consents.
3. System validates the submission and creates the member account.

#### Extensions

- Enrollment is blocked when required consent is missing.

### Browse Rewards

- ID: `browse-rewards`
- Primary actor: Unspecified
- Complexity: average
- Goal: Browse Rewards
- Source: round 3 use_cases

#### Main Success Scenario

1. Customer opens the rewards catalog.
2. System displays available rewards and points balance.
3. Customer filters or sorts the catalog.

#### Extensions

- Catalog view degrades if an integration is temporarily unavailable.

### Redeem Reward

- ID: `redeem-reward`
- Primary actor: Unspecified
- Complexity: complex
- Goal: Redeem Reward
- Source: round 3 use_cases

#### Main Success Scenario

1. Customer selects a reward.
2. System validates reward eligibility and available points.
3. System reserves the reward and updates the member balance.
4. System confirms redemption to the customer.

#### Extensions

- Reward inventory is exhausted before completion.
- Customer does not have enough points.
- Payment confirmation is missing for a reward that depends on purchase completion.

### Manage Reward Catalog

- ID: `manage-reward-catalog`
- Primary actor: Unspecified
- Complexity: average
- Goal: Manage Reward Catalog
- Source: round 3 use_cases

#### Main Success Scenario

1. Operations Manager opens catalog administration.
2. Operations Manager updates reward configuration.
3. System validates and publishes the change.

#### Extensions

- A change is rejected because it would make an active reward invalid.

### Review Redemption Analytics

- ID: `review-redemption-analytics`
- Primary actor: Unspecified
- Complexity: simple
- Goal: Review Redemption Analytics
- Source: round 3 use_cases

#### Main Success Scenario

1. Operations Manager opens the analytics dashboard.
2. System shows redemption and campaign metrics.

#### Extensions

- A reporting data source is delayed.


## States and Transitions

- `state-transition-1` Redemption: Requested -> Validated -> Fulfilled [source: round 6 states_and_transitions]
- `state-transition-2` Redemption: Requested -> Validated -> Fulfilled [source: round 6 states_and_transitions]
- `state-transition-3` Redemption: Requested -> Rejected [source: round 6 states_and_transitions]
- `state-transition-4` Reward Catalog Entry: Draft -> Published -> Retired [source: round 6 states_and_transitions]
- `state-transition-5` Reward Catalog Entry: Draft -> Published -> Retired [source: round 6 states_and_transitions]


## Triggers and Approvals

- `trigger-1` Payment confirmation triggers redemption fulfillment [source: round 6 triggers_and_approvals]
- `trigger-2` Catalog validation approval is required before a reward becomes Published [source: round 6 triggers_and_approvals]


## Interfaces and Integrations

- `interface-1` Member App calls Loyalty API [source: round 7 interfaces_and_integrations]
- `interface-2` Operations Console calls Loyalty API [source: round 7 interfaces_and_integrations]
- `interface-3` Loyalty API calls Payment Gateway Adapter [source: round 7 interfaces_and_integrations]
- `interface-4` Loyalty API sends Analytics Service [source: round 7 interfaces_and_integrations]


## Requirement To Use-Case Traceability

- `trace-req-uc-1` non_functional-requirement-6 -> redeem-reward (requirement statement references use-case name)


## Use-Case To Analysis Traceability

- `trace-uc-analysis-1` enroll-member -> entity-member (use-case text references analysis object name)
- `trace-uc-analysis-2` browse-rewards -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-3` redeem-reward -> entity-member (use-case text references analysis object name)
- `trace-uc-analysis-4` redeem-reward -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-5` redeem-reward -> entity-redemption (use-case text references analysis object name)
- `trace-uc-analysis-6` redeem-reward -> state-entity-redemption (use-case text references analysis object name)
- `trace-uc-analysis-7` manage-reward-catalog -> entity-reward (use-case text references analysis object name)
- `trace-uc-analysis-8` review-redemption-analytics -> entity-campaign (use-case text references analysis object name)
- `trace-uc-analysis-9` review-redemption-analytics -> entity-redemption (use-case text references analysis object name)
- `trace-uc-analysis-10` review-redemption-analytics -> state-entity-redemption (use-case text references analysis object name)

