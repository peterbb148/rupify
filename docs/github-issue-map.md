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

V1 is complete. Remaining open work is V2.

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
- V2 epics are explicitly future-facing and begin after the completed V1 baseline

## Labels To Use

- `epic`
- `v1`
- `v2`
- `documentation`
- `skills`
- `python`
- `dogfooding`
