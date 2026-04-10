## Summary

Extend SpecOps beyond V1 into richer UML support and formal specification translation built on top
of the canonical project model. V2 is where SpecOps should close the current gap between
use-case/UCP discovery and UML-ready, RUP-aligned analysis and design capture.

## Scope

- UML generation
- richer domain modeling
- formal language outputs
- interview/model extensions for UML readiness
- RUP-aligned analysis and design information capture
- traceability from discovery to generated UML and formal artifacts

## Required Capability Additions

- capture domain concepts and relationships needed for class and domain diagrams
- capture boundary/control/entity candidates and use-case realizations
- capture sequence and interaction detail needed for interaction diagrams
- capture lifecycle and stateful behavior needed for state machines
- capture subsystem, component, integration, and deployment structure
- capture supplementary constraints that materially affect architecture and design

## Acceptance Criteria

- V2 adds outputs without breaking the V1 model contract
- translation rules remain anchored to the canonical model
- the interview/model path is strong enough to support full UML artifact generation without
  pretending V1 coverage was sufficient
- the repo explicitly closes the current RUP/UML-readiness gap instead of leaving it implicit
