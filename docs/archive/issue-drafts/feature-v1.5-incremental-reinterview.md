## Summary

Add incremental re-interview behavior so new information can update an existing interview/model
state without forcing a complete restart.

Parent epic: V1.5 interview readiness

## Scope

- stable identifiers for rounds, questions, and model entities
- patch-oriented interview updates
- rerun by view, round, or unresolved-question set
- merge behavior for replayed or updated answers

## Acceptance Criteria

- an existing interview session can be replayed and selectively extended
- the workflow can revisit one affected area without rerunning unrelated rounds
- updated answers merge into the existing model instead of replacing it wholesale
- the system can target unresolved or stale questions directly
