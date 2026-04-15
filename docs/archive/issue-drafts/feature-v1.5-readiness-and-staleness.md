## Summary

Track per-view readiness and downstream staleness so SpecOps can tell the truth about which parts
of a specification are complete, partial, blocked, or invalidated by later changes.

Parent epic: V1.5 interview readiness

## Scope

- readiness state per view
- dependency tracking between interview/model sections and outputs
- stale markers after impactful changes
- gating rules for specification outputs

## Acceptance Criteria

- the workflow can report readiness independently for the relevant specification views
- downstream artifacts are marked stale when dependent answers change
- requested outputs fail clearly or report blockers when prerequisite information is unresolved
- traceability gaps are made visible before UML rendering is attempted
