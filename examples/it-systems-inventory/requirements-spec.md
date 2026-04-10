# Requirements Specification

## Project

- Name: IT Systems Inventory and Lifecycle Management
- Domain: Enterprise IT portfolio management
- Scope: Web-based inventory and lifecycle management system for all non-OT IT systems.

## Problem Statement

The company has many overlapping IT systems with different costs, risks, and lifecycle states. IT Business Owners and related stakeholders lack a single system for inventory, planning, deprecation, cost management, and risk oversight.

## Business Goals

- Improve planning of IT system purchasing and lifecycle decisions.
- Create a single inventory source of truth for non-OT IT systems.
- Improve visibility of overlap, cost, risk, and deprecation status.

## Success Criteria

- Stakeholders can inventory all non-OT systems in one place.
- Lifecycle and approval states are visible and configurable.
- Downstream systems can consume data through an API.
- The system supports lifecycle planning, deprecation, and cost/risk management workflows.

## Functional Requirements

- The system must manage inventory for all non-OT IT systems.
- The system must allow users to register a system.
- The system must allow authorized users to edit system metadata.
- The system must support comparison of overlapping systems.
- The system must track configurable lifecycle states, including proposed, active, tolerated, sunset, and decommissioned.
- The system must track annual cost, contract end, owner gap, security rating, business criticality, technical debt, and redundancy.
- The system must support business workflows such as stage gates and approval states.
- The system must provide API access for downstream systems and AI agents.
- The system must support reporting of portfolio gaps.
- The system must support risk and cost review across inventoried systems.

## Non-Functional Requirements

- The UI must be web based.
- The system must support SSO.
- The system must support role-based access control.
- The system must provide an audit trail.
- The system must support search and filtering.
- The system must provide availability of at least 99%.
- The system must provide acceptable web performance for normal page rendering.

## Assumptions

- The system acts as the CMDB for IT applications and systems, excluding OT systems.
- API consumers include downstream reporting systems and AI agents.
- Lifecycle states are configurable even though an initial default set exists.
- V1 includes workflow support for approvals and stage gates, not just passive inventory.
- The UCP inputs were estimated using defaults for a similar internal enterprise system at a company of about 1000 people.

## Open Questions

- Did performance mean page rendering should be less than 1 second rather than greater than 1 second?
- Are integrations/interfaces first-class inventory objects or only metadata on systems?
- Should procurement, security, finance, and application owners have distinct roles and workflows in V1?
- What exact approval workflows and stage-gate states are required in V1?
- What data model is required for overlap analysis and portfolio gap reporting?
