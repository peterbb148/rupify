# SpecOps

SpecOps is a Codex-native skill pack for software requirements discovery. It is designed to
interview a stakeholder, normalize the answers into a canonical project model, and generate
first-class artifacts from the same source of truth:

- `requirements-spec.md`
- `use-case-model.md`
- `state-model.md`
- `ucp-estimate.md`

The interview step can be invoked directly as the `$specops-interview` skill.

The repository is documentation-first and dogfood-oriented. The immediate goal is to use SpecOps to
specify and improve SpecOps itself.

## V1 Status

SpecOps V1 is delivered.

Delivered in V1:

- first-class interview flow via `$specops-interview`
- canonical `specops-model` workflow
- generated `requirements-spec.md`, `use-case-model.md`, and `ucp-estimate.md`
- deterministic UCP calculation and Markdown rendering utilities
- dogfooding examples and replayable interview fixtures
- interview UX and UCP guidance refinements from real usage

V1.5 is complete and established the interview/model readiness bridge.

V1.6 is also complete. It hardened the canonical model, readiness rules, cross-view traceability,
analysis/design separation, and proved one end-to-end formal artifact pipeline via `state-model.md`.

The remaining roadmap is now V2 breadth work: broader UML/formal specification coverage and
integrations/productization on top of the hardened baseline.

## Repository Layout

- `docs/`: implementation plan, architecture, dogfooding workflow, and GitHub issue map
- `.specify/`: SpecKit constitution and the first dogfooding spec
- `skills/`: orchestrator and subskills
- `src/specops_tools/`: UV-based Python utilities for deterministic rendering and UCP scoring
- `examples/`: canonical example models, generated artifacts, and dogfooding feedback files

## Skill Entry Points

- `$specops-interview`: run the stakeholder interview as a first-class skill
- `$specops-discovery`: normalize interview output into the canonical model
- `$specops-use-cases`: refine actors, scenarios, and complexity
- `$specops-ucp`: calculate the deterministic estimate
- `$specops`: run the broader interview-to-artifact workflow

## Python Workflow

Python in this repo is managed with `uv`.

Common commands:

```bash
uv run python -m unittest
uv run python -m specops_tools.ucp_cli --model examples/loyalty-platform/specops-model.json
uv run python -m specops_tools.render_cli --model examples/loyalty-platform/specops-model.json --output-dir /tmp/specops-out
```

YAML parsing is optional and intentionally not installed by default. If you want the CLI tools to
read `*.yaml` models directly, install the optional dependency with:

```bash
uv sync --extra yaml
```

## Primary Documents

- [Implementation Plan](docs/implementation-plan.md)
- [Solution Architecture](docs/solution-architecture.md)
- [V1.5 Interview Readiness](docs/v1.5-interview-readiness.md)
- [V1.6 Specification Hardening](docs/v1.6-specification-hardening.md)
- [V2 Go/No-Go Decision](docs/v2-go-no-go-decision.md)
- [Document Ingestion Future Direction](docs/document-ingestion-future.md)
- [Dogfooding Workflow](docs/dogfooding.md)
- [GitHub Issue Map](docs/github-issue-map.md)
- [SpecKit Constitution](.specify/memory/constitution.md)

## Dogfooding Example

The IT systems inventory example is both a sample workflow output and a feedback input for improving
SpecOps:

- [Example Model](/Volumes/Data/GitHub/Peterbb148/specops/examples/it-systems-inventory/specops-model.yaml)
- [Example Feedback](/Volumes/Data/GitHub/Peterbb148/specops/examples/it-systems-inventory/specops-feedback.md)
