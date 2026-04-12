# SpecOps Constitution

## Purpose

This constitution defines the non-negotiable operating principles for SpecOps. It is the governing
document for specifications, skills, tooling, and delivery decisions in this repository.

## Principles

### 1. Spec First

Work starts from a spec, issue, or explicit change request. Freeform implementation without a
tracked problem statement is not the default path.

### 2. Canonical Model First

Generated outputs must derive from a canonical project model rather than ad hoc prompt state. If
multiple artifacts disagree, the model is the source that must be fixed.

### 3. Deterministic Estimation

Use Case Point estimation must be deterministic, inspectable, and reproducible. Where the workflow
depends on a formula, the formula must live in code rather than being improvised in chat.

### 4. Explicit Gaps Over Invented Confidence

Unknowns, assumptions, and unresolved questions must remain visible. SpecOps must fail clearly or
stop for clarification instead of fabricating precision.

### 5. Dogfood Early

SpecOps must be applied to SpecOps itself whenever that is practical. Workflow friction discovered
while dogfooding is product feedback, not incidental inconvenience.

### 6. UV for Python

Python in this repository is run with `uv`. Scripts, validation, and documentation should use
`uv run` and `uv sync` conventions.

### 7. Documentation Is Product Surface

Architecture, workflow, model definitions, and governance docs are part of the product. They are
not disposable notes and must remain aligned with the implementation.

### 8. Documentation Must Be Updated With The Change

Every meaningful implementation change must include the documentation updates needed to keep the
repository truthful. If code, workflow, issue status, or delivery state changes, the relevant docs
must be updated in the same change rather than deferred indefinitely.

## Delivery Rules

- V1 scope is software and system requirements discovery
- one canonical model must drive requirements, use-case, and UCP outputs
- UML and formal specification translation are future-facing and must not distort V1
- GitHub issues are the work tracking source of truth for this repo
- documentation and issue-status documents must be kept current as part of normal delivery work

## Amendment Process

Changes to this constitution require:

1. an explicit rationale
2. an update to this file
3. alignment with active specs and issue tracking

If a proposed change conflicts with an existing principle, the constitution must be updated before
the implementation is treated as valid.
