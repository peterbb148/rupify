# Use-Case Documents

## Enroll Member

- ID: `uc-enroll`
- Primary Actor: Customer
- Supporting Actors: None
- Priority: Unspecified
- Status: Unspecified
- Content Semantics: Unspecified
- Readiness: unspecified
- Complexity: simple
- Goal: Join the loyalty program and activate an account.
- Trigger: Unspecified
- Source: round n/a 

### Brief Description

Join the loyalty program and activate an account.

### Preconditions

- None

### Postconditions

- None

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

- None

### View of Participating Classes

- None

### Sequence and Interaction Notes

No interaction realization documented.

### Linked Requirements

- None

### Other Artifacts

- None




## Browse Rewards

- ID: `uc-browse`
- Primary Actor: Customer
- Supporting Actors: None
- Priority: Unspecified
- Status: Unspecified
- Content Semantics: Unspecified
- Readiness: unspecified
- Complexity: average
- Goal: View eligible rewards and current point balance.
- Trigger: Unspecified
- Source: round n/a 

### Brief Description

View eligible rewards and current point balance.

### Preconditions

- None

### Postconditions

- None

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

- None

### View of Participating Classes

- None

### Sequence and Interaction Notes

No interaction realization documented.

### Linked Requirements

- None

### Other Artifacts

- None




## Redeem Reward

- ID: `uc-redeem`
- Primary Actor: Customer
- Supporting Actors: None
- Priority: Unspecified
- Status: Unspecified
- Content Semantics: Unspecified
- Readiness: unspecified
- Complexity: complex
- Goal: Redeem a selected reward against available loyalty points.
- Trigger: Unspecified
- Source: round n/a 

### Brief Description

Redeem a selected reward against available loyalty points.

### Preconditions

- None

### Postconditions

- None

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

No named scenarios documented.

### User Interface

- None

### View of Participating Classes

- None

### Sequence and Interaction Notes

No interaction realization documented.

### Linked Requirements

- None

### Other Artifacts

- None




## Manage Reward Catalog

- ID: `uc-catalog`
- Primary Actor: Operations Manager
- Supporting Actors: None
- Priority: Unspecified
- Status: Unspecified
- Content Semantics: Unspecified
- Readiness: unspecified
- Complexity: average
- Goal: Create or update reward catalog entries and campaign details.
- Trigger: Unspecified
- Source: round n/a 

### Brief Description

Create or update reward catalog entries and campaign details.

### Preconditions

- None

### Postconditions

- None

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

No named scenarios documented.

### User Interface

- None

### View of Participating Classes

- None

### Sequence and Interaction Notes

No interaction realization documented.

### Linked Requirements

- None

### Other Artifacts

- None




## Review Redemption Analytics

- ID: `uc-analytics`
- Primary Actor: Operations Manager
- Supporting Actors: None
- Priority: Unspecified
- Status: Unspecified
- Content Semantics: Unspecified
- Readiness: unspecified
- Complexity: simple
- Goal: Inspect reward redemption and campaign performance.
- Trigger: Unspecified
- Source: round n/a 

### Brief Description

Inspect reward redemption and campaign performance.

### Preconditions

- None

### Postconditions

- None

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

No named scenarios documented.

### User Interface

- None

### View of Participating Classes

- None

### Sequence and Interaction Notes

No interaction realization documented.

### Linked Requirements

- None

### Other Artifacts

- None




