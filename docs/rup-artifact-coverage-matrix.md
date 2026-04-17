# RUP Artifact Coverage Matrix

## Purpose

This note maps a pragmatic RUP-style artifact set against what Rupify actually implements today.

The point is not to claim that RUP has one single universally binding template pack. The point is
to make the current gap visible between:

- a RUP-aligned specification system
- the narrower artifact set that Rupify can currently generate

## Status Scale

- `full`: implemented as a first-class artifact or model path
- `partial`: represented in the canonical model or supporting docs, but not yet a complete formal
  artifact path
- `missing`: not yet present as a credible first-class artifact path

## Coverage Matrix

| RUP-style artifact / view | What it usually covers | Rupify status | Current Rupify equivalent | Gap / next issue |
| --- | --- | --- | --- | --- |
| Vision / scope | problem, stakeholders, business goals, scope | `partial` | `project`, `business_goals`, `success_criteria`, rendered in `requirements-spec.md` | no standalone vision artifact yet |
| Supplementary requirements | non-functional requirements, constraints, quality attributes | `partial` | `requirements.non_functional`, `requirements-spec.md` | stronger fit criteria and broader formal structure still needed |
| Use-case model | actors, goals, scenarios, extensions | `full` | `use-case-model.md`, canonical actors/use cases | could deepen, but already credible |
| Template-driven system/subsystem document | overview, risks, system-level use cases, architecture, subsystem descriptions | `full` | `system-document.md` plus canonical risks/use cases/design views | deepen polish under `#123` follow-ons |
| Template-driven use-case document | per-use-case status, priorities, flows, secondary scenarios, UI, related artifacts | `partial` | canonical use cases, interaction/process/design views | `#123` template-driven document suite |
| Template-driven scenario document | scenario-level flow, sequence/activity views, artifact references | `missing` | scenario content is implicit inside use cases rather than first-class | `#123` template-driven document suite |
| Analysis model: domain / logical view | domain concepts, relationships, rules | `full` | `domain-model.md`, `analysis_view`, `logical_view`, Mermaid `classDiagram` output | deeper domain semantics and product polish, not a missing artifact family |
| Analysis model: state / process view | states, transitions, triggers, approvals | `full` | `state-model.md`, `analysis_view`, `process_view` | broader V2 state breadth in `#15` |
| Analysis model: interaction view | realization of use cases as messages/interactions | `full` | `interaction-model.md`, `interaction_view`, Mermaid `sequenceDiagram` output | deeper semantics and publication polish, not a missing artifact family |
| Design model: component view | components, interfaces, responsibilities | `full` | `deployment-model.md`, `design_view`, Mermaid deployment/architecture output | stronger deployment semantics and productization remain |
| Design model: deployment / physical view | nodes, runtime boundaries, deployment placement | `full` | `deployment-model.md`, `runtime_boundary_objects`, Mermaid deployment/architecture output | stronger physical/deployment semantics remain |
| Cross-artifact traceability | requirement -> use case -> analysis -> design | `partial` | canonical `traceability` plus validation and rendered trace sections | `#13` broader RUP traceability layer |
| Estimate / planning support | size and effort estimation | `full` | `ucp-estimate.md` | not a classic RUP core artifact, but implemented |

## What Rupify Follows Today

Rupify does follow a RUP-aligned internal structure in a meaningful sense:

- separate analysis and design layers
- explicit logical, process, and architecture views
- readiness by view
- traceability between model layers
- deterministic artifact generation from a canonical model

That is enough to say the system is RUP-aligned in architecture.

## What Rupify Does Not Yet Follow

Rupify does not yet implement a complete first-class artifact set for a broad RUP/UML solution
architecture workflow.

The main gaps are:

- no standalone vision artifact
- no standalone supplementary specification artifact
- traceability is real, but still narrower than a complete RUP trace suite
- deployment output is practical and publishable, but not yet a UML-pure deployment interchange path
- productization and publishing workflows still lag behind the underlying specification engine

## Bottom Line

If the question is:

- “Do we have a canonical internal template?” -> `yes`
- “Is it a full canonical RUP artifact set?” -> `no`
- “Are we moving toward one?” -> `yes`

The repo is now best described as:

> a RUP-aligned canonical model and materially broader artifact system, but not yet a full RUP
> artifact suite

## Recommended Next Move

The strongest next work is no longer another missing core artifact family. It is:

- productization of the existing formal and Mermaid outputs under `#7`
- template-driven system, use-case, and scenario documents under `#123`
- document ingestion and hybrid workflows under `#65`
- cleanup of remaining standalone vision/supplementary specification gaps
