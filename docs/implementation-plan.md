# SpecOps Implementation Plan

## Objective

Deliver a reusable Codex-native skill pack for software requirements discovery. The first release
must capture requirements through an interview, persist them in one canonical model, and generate a
requirements spec, use-case model, and UCP estimate from that shared model.

## Workstreams

## 1. Repository Foundation

- Create a documentation-first repo structure
- Establish UV as the Python workflow
- Add a SpecKit constitution and initial dogfooding spec

## 2. Skill Pack

- `specops`: orchestrator skill
- `specops-discovery`: interview and model normalization
- `specops-use-cases`: actors, use cases, scenarios, complexity
- `specops-ucp`: deterministic UCP calculation and estimate reporting

## 3. Canonical Model and Artifacts

- Define `specops-model.yaml` as the canonical project model
- Keep artifact generation anchored to that model
- Reserve space for future UML and formal specification outputs

## 4. Deterministic Utilities

- Add a Python UCP engine
- Add a renderer that turns a model into Markdown artifacts
- Keep YAML support explicit through `uv sync --extra yaml`

## 5. Dogfooding

- Use SpecOps to spec and prioritize SpecOps itself
- Keep one active dogfooding loop inside `.specify/specs/`
- Drive ongoing work from GitHub issues rather than ad hoc notes

## Immediate Deliverables

- Architecture documentation
- SpecKit constitution
- Skill pack scaffold
- UCP engine and renderer
- Example project model and generated outputs
- GitHub issue hierarchy for V1 and V2

