# SpecOps Implementation Plan

## Status

V1 is complete. This document now serves as the implementation record for what was delivered in V1,
the completed V1.5 bridge, the new V1.6 hardening phase, and the shape that should be preserved
while later work expands UML/formalization and integration support.

## Objective

Deliver a reusable Codex-native skill pack for software requirements discovery. The first release
must capture requirements through an interview, persist them in one canonical model, and generate a
requirements spec, use-case model, and UCP estimate from that shared model.

## Workstreams

## 1. Repository Foundation

- Delivered: documentation-first repo structure
- Delivered: UV as the Python workflow
- Delivered: SpecKit constitution and initial dogfooding spec

## 2. Skill Pack

- Delivered: `specops` orchestrator skill
- Delivered: `specops-interview` first-class interview skill
- Delivered: `specops-discovery` interview and model normalization skill
- Delivered: `specops-use-cases` actor, use-case, scenario, and complexity skill
- Delivered: `specops-ucp` deterministic UCP calculation and estimate reporting skill

## 3. Canonical Model and Artifacts

- Delivered: `specops-model.yaml` as the canonical project model
- Delivered: artifact generation anchored to that model
- Delivered: reserved space for future UML and formal specification outputs

## 4. Deterministic Utilities

- Delivered: Python UCP engine
- Delivered: renderer that turns a model into Markdown artifacts
- Delivered: explicit YAML support through `uv sync --extra yaml`
- Delivered: executable interview CLI and replay harness for automated regression testing

## 5. Dogfooding

- Delivered: SpecOps used to spec and prioritize SpecOps itself
- Delivered: active dogfooding loop inside `.specify/specs/`
- Delivered: work driven from GitHub issues rather than ad hoc notes
- Delivered: example-feedback pattern to feed workflow friction back into the product

## V1 Deliverables

- Architecture documentation
- SpecKit constitution
- Skill pack scaffold
- First-class interview entry skill
- UCP engine and renderer
- Example project models and generated outputs
- Executable interview replay fixtures and tests
- GitHub issue hierarchy for V1 and V2

## V1.5 Bridge Work

The next phase is not direct UML rendering. It is interview and model readiness for full
specification work.

V1.5 focuses on:

- stronger interview coverage across the relevant RUP-aligned views
- explicit ambiguity handling for unknowns, assumptions, conflicts, and stale answers
- incremental re-interview so new information can update the model without restarting from scratch
- readiness, provenance, and traceability needed before deterministic UML outputs are credible

Reference: [V1.5 Interview Readiness](v1.5-interview-readiness.md)

## V1.6 Hardening Work

V1.6 exists because the current system is interview-ready and model-aware, but not yet a full
RUP-grade specification system.

V1.6 focuses on:

- stronger canonical semantics for analysis and design structures
- per-view completeness and readiness gates
- cross-view traceability beyond simple provenance
- explicit separation between analysis-level and design-level structures where needed
- one proven end-to-end formal artifact pipeline

Reference: [V1.6 Specification Hardening](v1.6-specification-hardening.md)

## Remaining Roadmap After V1.6

- V2 UML and formal specification translation at broader artifact breadth
- V2 integrations and productization
