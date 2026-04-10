# Use-Case Model

## Actors

- `business-owner` IT Business Owner (human, complex): Owns business accountability for systems and uses the platform for inventory, planning, lifecycle oversight, and approvals.
- `technical-owner` Technical Owner (human, complex): Maintains technical metadata, lifecycle details, and system-level attributes.
- `enterprise-architect` Enterprise Architect (human, complex): Reviews overlap, portfolio fit, capability coverage, and strategic lifecycle direction.
- `governance-user` Procurement/Security/Finance/Application Owner (human, average): Contributes governance, cost, security, and ownership review activities.
- `downstream-system` Downstream API Consumer (system, simple): Reads inventory and lifecycle data through the API for reporting or automation.

## Use Cases

### Register a system

- ID: `register-system`
- Primary actor: IT Business Owner
- Complexity: simple
- Goal: Add a non-OT IT system to the inventory.

#### Main Success Scenario

1. IT Business Owner opens the registration flow.
2. User enters required metadata for the system.
3. System validates the submission.
4. System creates the inventory record.

#### Extensions

- Required metadata is missing.
- A potential duplicate system is detected.

### Edit system metadata

- ID: `edit-metadata`
- Primary actor: Technical Owner
- Complexity: average
- Goal: Maintain and update metadata for an existing system.

#### Main Success Scenario

1. Technical Owner locates the system record.
2. Technical Owner edits metadata fields.
3. System validates the changes.
4. System saves the updated record and audit trail.

#### Extensions

- User lacks permission to edit certain fields.
- A field value violates policy or data validation.

### Compare overlapping systems

- ID: `compare-overlap`
- Primary actor: Enterprise Architect
- Complexity: complex
- Goal: Identify and compare systems with overlapping purpose or capability.

#### Main Success Scenario

1. Enterprise Architect searches or selects systems for comparison.
2. System displays metadata, capabilities, cost, risk, and lifecycle information side by side.
3. Enterprise Architect reviews overlap indicators and redundancy signals.
4. System supports documenting comparison outcomes.

#### Extensions

- Overlap signals are incomplete because metadata is missing.
- Comparison scope spans too many systems and must be narrowed.

### Track lifecycle state

- ID: `track-lifecycle`
- Primary actor: IT Business Owner
- Complexity: average
- Goal: Maintain lifecycle state and progression for a system.

#### Main Success Scenario

1. IT Business Owner opens the lifecycle view for a system.
2. User reviews current lifecycle state and allowed transitions.
3. User updates or submits a lifecycle transition.
4. System records the transition and exposes the updated state.

#### Extensions

- Requested transition is not allowed by workflow rules.
- Transition requires approval before completion.

### Review risks and costs

- ID: `review-risk-cost`
- Primary actor: Procurement/Security/Finance/Application Owner
- Complexity: average
- Goal: Inspect risk and cost dimensions for a system or portfolio slice.

#### Main Success Scenario

1. Governance user opens a system or portfolio view.
2. System shows annual cost, contract end, owner gap, security rating, business criticality, technical debt, and redundancy.
3. Governance user filters or searches the results.
4. Governance user records or exports the review outcome.

#### Extensions

- Required source data is missing or stale.
- Some data is restricted by role.

### Approve deprecation and stage gates

- ID: `approve-deprecation`
- Primary actor: Procurement/Security/Finance/Application Owner
- Complexity: complex
- Goal: Execute workflow approvals for lifecycle stage gates and deprecation decisions.

#### Main Success Scenario

1. A lifecycle or deprecation request is submitted.
2. Governance user reviews the request and supporting metadata.
3. Governance user approves or rejects the stage-gate decision.
4. System records the decision and updates the workflow state.

#### Extensions

- Additional approvers are required.
- A rejection sends the item back for rework.
- Mandatory supporting information is missing.

### Report portfolio gaps

- ID: `report-portfolio-gaps`
- Primary actor: Enterprise Architect
- Complexity: complex
- Goal: Identify gaps, duplication, or planning issues across the IT system portfolio.

#### Main Success Scenario

1. Enterprise Architect selects a scope such as capability, geography, or ownership area.
2. System analyzes the selected inventory subset.
3. System presents detected gaps, duplication, or lifecycle concerns.
4. Enterprise Architect exports or shares the results.

#### Extensions

- The selected data set is incomplete.
- Gap analysis rules need refinement for the selected scope.

### Expose inventory data by API

- ID: `export-api`
- Primary actor: Downstream API Consumer
- Complexity: average
- Goal: Retrieve inventory and lifecycle data programmatically.

#### Main Success Scenario

1. Downstream system authenticates to the API.
2. Downstream system requests inventory or lifecycle data.
3. System validates access rights and query parameters.
4. System returns the requested data.

#### Extensions

- Caller is unauthorized.
- Query parameters are invalid.
- Requested data includes restricted fields.

