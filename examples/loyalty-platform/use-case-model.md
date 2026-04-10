# Use-Case Model

## Actors

- `customer` Customer (human, complex): A loyalty member using the digital experience to enroll, browse, and redeem rewards.
- `ops-manager` Operations Manager (human, average): An internal operator responsible for campaigns, catalog changes, and reporting.
- `payment-gateway` Payment Gateway (system, simple): An external system that confirms payment completion for eligible transactions.

## Use Cases

### Enroll Member

- ID: `uc-enroll`
- Primary actor: Customer
- Complexity: simple
- Goal: Join the loyalty program and activate an account.

#### Main Success Scenario

1. Customer opens the loyalty enrollment flow.
2. Customer provides the required details and consents.
3. System validates the submission and creates the member account.

#### Extensions

- Enrollment is blocked when required consent is missing.

### Browse Rewards

- ID: `uc-browse`
- Primary actor: Customer
- Complexity: average
- Goal: View eligible rewards and current point balance.

#### Main Success Scenario

1. Customer opens the rewards catalog.
2. System displays available rewards and points balance.
3. Customer filters or sorts the catalog.

#### Extensions

- Catalog view degrades if an integration is temporarily unavailable.

### Redeem Reward

- ID: `uc-redeem`
- Primary actor: Customer
- Complexity: complex
- Goal: Redeem a selected reward against available loyalty points.

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

- ID: `uc-catalog`
- Primary actor: Operations Manager
- Complexity: average
- Goal: Create or update reward catalog entries and campaign details.

#### Main Success Scenario

1. Operations Manager opens catalog administration.
2. Operations Manager updates reward configuration.
3. System validates and publishes the change.

#### Extensions

- A change is rejected because it would make an active reward invalid.

### Review Redemption Analytics

- ID: `uc-analytics`
- Primary actor: Operations Manager
- Complexity: simple
- Goal: Inspect reward redemption and campaign performance.

#### Main Success Scenario

1. Operations Manager opens the analytics dashboard.
2. System shows redemption and campaign metrics.

#### Extensions

- A reporting data source is delayed.

