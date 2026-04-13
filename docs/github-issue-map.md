# GitHub Issue Map

This document records the issue hierarchy used in GitHub and the current delivery status.

## V1 Status

Closed V1 issues:

- `#1` `EPIC: SpecOps V1 repository foundation`
- `#10` `EPIC: SpecOps V1 interview-to-artifact workflow`
- `#9` `EPIC: SpecOps V1 dogfooding and validation`
- `#6` `Bootstrap SpecOps repository docs, constitution, and architecture`
- `#5` `Define the canonical specops-model and skill pack scaffold`
- `#4` `Implement deterministic UCP engine and artifact renderer`
- `#3` `Add example fixtures and generated outputs`
- `#2` `Dogfood SpecOps on the SpecOps product definition`
- `#16` `Improve interview UX and reduce wall-of-text responses`
- `#17` `Improve UCP scoring guidance in the interview flow`

V1 is complete. V1.5 is also complete. The next active bridge is now V1.6, which exists to harden
the model and workflow before broad V2 UML/formalization work is treated as implementation-ready.

## Closed V1.5 Work

- `#27` `EPIC: SpecOps V1.5 interview readiness`
- `#23` `Extend interview coverage for the relevant RUP-aligned views`
- `#24` `Make ambiguity and provenance first-class in the canonical model`
- `#25` `Support incremental re-interview and model patching`
- `#26` `Track per-view readiness and downstream staleness`
- `#38` `Normalize UCP rounds into canonical model structures`
- `#39` `Render structured canonical model objects in artifacts`
- `#40` `Add trace metadata from interview rounds into normalized objects`

## V1.5 Focus Delivered

- interview coverage for the relevant RUP-aligned specification views
- explicit ambiguity and conflict handling
- incremental re-interview and model patching
- readiness, provenance, and staleness tracking
- deterministic normalization from replay output into the richer canonical model
- structured rendering and trace-aware artifact output

These themes now shape the completed bridge into V1.6 hardening work.

## Open V1.6 Work

- `#45` `EPIC: SpecOps V1.6 specification hardening`

## V1.6 Focus

- formalize the canonical analysis and design model
- define per-view completeness and readiness gates
- strengthen cross-view traceability
- separate analysis-level and design-level structures where needed
- prove at least one real formal artifact pipeline end to end

## Open V1.6 Decomposition for Epic #45

- `#47` `Formalize canonical analysis and design model semantics`
- `#46` `Define per-view completeness and readiness gates`
- `#50` `Implement cross-view specification traceability`
- `#49` `Separate analysis structures from design structures in the canonical model`
- `#48` `Prove one end-to-end formal artifact pipeline from the canonical model`

## Open Epics

- `#8` `EPIC: SpecOps V2 UML and formal specification translation`
- `#7` `EPIC: SpecOps V2 integrations and productization`

## Open V2 Decomposition for Epic #8

- `#11` `Implement V2 domain and class modeling`
- `#14` `Implement V2 interaction diagram support`
- `#15` `Implement V2 state modeling support`
- `#12` `Implement V2 component and deployment modeling`
- `#13` `Implement V2 RUP traceability layer`

## Relationship Model

- V1 foundation epic owns repo documentation, constitution, and branch conventions
- V1 workflow epic owns the orchestrator, subskills, model, renderer, and UCP logic
- V1 dogfooding epic owns the self-hosting spec, validation loop, and workflow adjustments
- V1.6 is the active hardening bridge between the completed V1.5 work and the future-facing V2
  epics
- V2 epics remain future-facing and should build on the stricter V1.6 baseline rather than bypass
  it

## Labels To Use

- `epic`
- `v1`
- `v2`
- `documentation`
- `skills`
- `python`
- `dogfooding`
