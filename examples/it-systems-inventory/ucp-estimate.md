# UCP Estimate

## Project

IT Systems Inventory and Lifecycle Management

## Summary

- `UAW`: 12.00
- `UUCW`: 90.00
- `UUCP`: 102.00
- `TCF`: 1.060
- `EF`: 0.965
- `UCP`: 104.336
- `Effort Hours`: 2086.72

## Inputs

- Technical factor weighted sum: 46.00
- Environmental factor weighted sum: 14.50
- Productivity hours per UCP: 20.00

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
