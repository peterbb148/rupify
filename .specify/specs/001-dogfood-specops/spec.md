# Feature Spec: Dogfood SpecOps on SpecOps

## Context

SpecOps is intended to help discover and structure software requirements. The fastest path to
finding defects in that workflow is to use it on its own repository, architecture, and backlog.

## Problem

SpecOps currently has a design plan but no stable repo structure, constitution, issue hierarchy, or
repeatable dogfooding loop. Without those, the product risks drifting into disconnected notes and
untracked implementation.

## Goal

Use SpecOps to establish the first self-hosted product loop:

- define the repository architecture
- define the governing constitution
- define the V1 and V2 issue hierarchy
- define the first example model and generated outputs
- use real example outputs as feedback inputs for improving SpecOps itself

## Success Criteria

- the repo contains the architecture and governance documents
- the repo contains a dogfooding workflow
- the repo contains a first example model with generated artifacts
- the repo treats example outputs as product feedback, not only as demonstrations
- the repo work is represented in GitHub issues and epics

## Constraints

- V1 stays focused on software and system requirements
- Python uses `uv`
- UCP logic must be deterministic
- unknowns remain explicit rather than hidden behind heuristics

## Open Questions

- when should YAML support become a default dependency instead of an optional extra
- which GitHub project board, if any, should own the epics
- how formal the future UML output should be in V2
- how examples should consistently feed back into model and interview improvements
