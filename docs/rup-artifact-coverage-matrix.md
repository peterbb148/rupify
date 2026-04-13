# RUP Artifact Coverage Matrix

## Purpose

This note maps a pragmatic RUP-style artifact set against what SpecOps actually implements today.

The point is not to claim that RUP has one single universally binding template pack. The point is
to make the current gap visible between:

- a RUP-aligned specification system
- the narrower artifact set that SpecOps can currently generate

## Status Scale

- `full`: implemented as a first-class artifact or model path
- `partial`: represented in the canonical model or supporting docs, but not yet a complete formal
  artifact path
- `missing`: not yet present as a credible first-class artifact path

## Coverage Matrix

| RUP-style artifact / view | What it usually covers | SpecOps status | Current SpecOps equivalent | Gap / next issue |
| --- | --- | --- | --- | --- |
| Vision / scope | problem, stakeholders, business goals, scope | `partial` | `project`, `business_goals`, `success_criteria`, rendered in `requirements-spec.md` | no standalone vision artifact yet |
| Supplementary requirements | non-functional requirements, constraints, quality attributes | `partial` | `requirements.non_functional`, `requirements-spec.md` | stronger fit criteria and broader formal structure still needed |
| Use-case model | actors, goals, scenarios, extensions | `full` | `use-case-model.md`, canonical actors/use cases | could deepen, but already credible |
| Analysis model: domain / logical view | domain concepts, relationships, rules | `partial` | `analysis_view`, `logical_view`, rendered in `requirements-spec.md` | `#11` domain and class modeling |
| Analysis model: state / process view | states, transitions, triggers, approvals | `full` | `state-model.md`, `analysis_view`, `process_view` | broader V2 state breadth in `#15` |
| Analysis model: interaction view | realization of use cases as messages/interactions | `missing` | trace links and use cases only | `#14` interaction diagram support |
| Design model: component view | components, interfaces, responsibilities | `partial` | `design_view`, `architecture_view`, rendered sections in existing artifacts | `#12` component and deployment modeling |
| Design model: deployment / physical view | nodes, runtime boundaries, deployment placement | `partial` | `runtime_boundary_objects`, architecture sections | `#12` component and deployment modeling |
| Cross-artifact traceability | requirement -> use case -> analysis -> design | `partial` | canonical `traceability` plus validation and rendered trace sections | `#13` broader RUP traceability layer |
| Estimate / planning support | size and effort estimation | `full` | `ucp-estimate.md` | not a classic RUP core artifact, but implemented |

## What SpecOps Follows Today

SpecOps does follow a RUP-aligned internal structure in a meaningful sense:

- separate analysis and design layers
- explicit logical, process, and architecture views
- readiness by view
- traceability between model layers
- deterministic artifact generation from a canonical model

That is enough to say the system is RUP-aligned in architecture.

## What SpecOps Does Not Yet Follow

SpecOps does not yet implement a complete first-class artifact set for a broad RUP/UML solution
architecture workflow.

The main gaps are:

- no standalone domain/class model artifact
- no interaction artifact family
- no formal component/deployment artifact family
- traceability is real, but not yet broad enough to count as a full RUP trace layer
- no standalone vision or supplementary specification artifact set

## Bottom Line

If the question is:

- “Do we have a canonical internal template?” -> `yes`
- “Is it a full canonical RUP artifact set?” -> `no`
- “Are we moving toward one?” -> `yes`

The repo is now best described as:

> a RUP-aligned canonical model and partial artifact system, not yet a full RUP artifact suite

## Recommended Next Move

If V2 proceeds, the strongest next artifact family is still `#11` domain and class modeling.

That closes the largest visible gap after the V1.6 `state-model.md` proof and moves SpecOps closer
to a genuinely broader RUP-style specification set.
