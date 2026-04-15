# Rupify

Rupify is a Codex-native, model-driven specification system for software and system requirements.
It interviews a stakeholder, normalizes the answers into a canonical project model, and generates
first-class specification artifacts and diagrams from that shared source of truth.

Current first-class outputs include:

- `requirements-spec.md`
- `use-case-model.md`
- `domain-model.md`
- `interaction-model.md`
- `deployment-model.md`
- `state-model.md`
- `ucp-estimate.md`
- Mermaid diagram bundles for domain, interaction, deployment, and state views

The repository is documentation-first and dogfood-oriented. The current open-source goal is to make
Rupify usable as a model-driven specification system with a clear end-to-end skill and CLI
workflow.

## Current Status

Rupify currently provides:

- interview-driven discovery via local skills and replayable fixtures
- a canonical project model as the source of truth
- formal Markdown outputs for requirements, use cases, domain, interaction, deployment, state, and
  UCP estimation
- Mermaid outputs for domain, interaction, deployment, and state publication
- readiness, staleness, provenance, and cross-view traceability in the model workflow

The remaining roadmap is now productization and workflow expansion:

- CLI and publishing polish
- automation and downstream integrations
- document ingestion and hybrid document-to-spec workflows
- remaining standalone specification gaps such as vision and supplementary specification outputs

## Open Source Readiness

This repository is usable as an open-source, model-driven specification toolkit today, with some
important scope boundaries:

- the Python tooling and example workflows are executable locally
- the skill pack is designed for Codex-style environments where local skills are available
- the canonical model and generated artifacts are the supported interoperability surface
- productization and document-ingestion work are still active roadmap items

## Repository Layout

- `docs/`: implementation plan, architecture, dogfooding workflow, and GitHub issue map
- `.specify/`: SpecKit constitution and the first dogfooding spec
- `skills/`: orchestrator and subskills
- `src/rupify_tools/`: UV-based Python utilities for deterministic rendering and UCP scoring
- `examples/`: canonical example models, generated artifacts, and dogfooding feedback files

## Skill Entry Points

- `$rupify-interview`: run the stakeholder interview as a first-class skill
- `$rupify-discovery`: normalize interview output into the canonical model
- `$rupify-use-cases`: refine actors, scenarios, and complexity
- `$rupify-ucp`: calculate the deterministic estimate
- `$rupify`: run the broader interview-to-artifact workflow

## Python Workflow

Python in this repo is managed with `uv`.

## Installation

### Prerequisites

- Python `3.12+`
- [`uv`](https://docs.astral.sh/uv/)

### Install Local Tooling

```bash
uv sync
```

If you want YAML model support:

```bash
uv sync --extra yaml
```

### Available CLI Entry Points

After `uv sync`, the current supported commands are:

```bash
uv run rupify-interview --help
uv run rupify-interview-replay --help
uv run rupify-ucp --help
uv run rupify-render --help
```

There is also one module-only CLI for the interview-fixture-to-formal flow:

```bash
uv run python -m rupify_tools.interview_to_formal_cli --help
```

Common commands:

```bash
uv run python -m unittest
uv run python -m rupify_tools.ucp_cli --model examples/loyalty-platform/rupify-model.json
uv run python -m rupify_tools.render_cli --model examples/loyalty-platform/rupify-model.json --output-dir /tmp/rupify-out
uv run python -m rupify_tools.render_cli --model examples/loyalty-platform/rupify-model.json --output-dir /tmp/rupify-formal --artifact-family formal
uv run python -m rupify_tools.render_cli --model examples/it-systems-inventory/rupify-model.json --output-dir /tmp/rupify-mermaid --artifact-family domain-mermaid
uv run python -m rupify_tools.render_cli --model examples/it-systems-inventory/rupify-model.json --output-dir /tmp/rupify-mermaid-state --artifact-family state-mermaid
uv run python -m rupify_tools.render_cli --model examples/it-systems-inventory/rupify-model.json --output-dir /tmp/rupify-mermaid-interaction --artifact-family interaction-mermaid
uv run python -m rupify_tools.render_cli --model examples/it-systems-inventory/rupify-model.json --output-dir /tmp/rupify-mermaid-deployment --artifact-family deployment-mermaid
uv run python -m rupify_tools.interview_to_formal_cli --input tests/fixtures/it_systems_inventory_session.json --output-dir /tmp/rupify-from-interview --write-model /tmp/rupify-from-interview/rupify-model.json
```

YAML parsing is optional and intentionally not installed by default. If you want the CLI tools to
read `*.yaml` models directly, install the optional dependency with:

```bash
uv sync --extra yaml
```

## Primary Documents

- [End-to-End Usage](docs/end-to-end-usage.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Solution Architecture](docs/solution-architecture.md)
- [V1.5 Interview Readiness](docs/v1.5-interview-readiness.md)
- [V1.6 Specification Hardening](docs/v1.6-specification-hardening.md)
- [V2 Go/No-Go Decision](docs/v2-go-no-go-decision.md)
- [RUP Artifact Coverage Matrix](docs/rup-artifact-coverage-matrix.md)
- [Repo Review](docs/repo-review-2026-04.md)
- [Mermaid Publication Workflows](docs/mermaid-publication-workflows.md)
- [Document Ingestion Future Direction](docs/document-ingestion-future.md)
- [Dogfooding Workflow](docs/dogfooding.md)
- [GitHub Issue Map](docs/github-issue-map.md)
- [SpecKit Constitution](.specify/memory/constitution.md)
- [Contributing](CONTRIBUTING.md)

## Dogfooding Example

The IT systems inventory example is both a sample workflow output and a feedback input for
improving Rupify:

- [Example Model](examples/it-systems-inventory/rupify-model.yaml)
- [Example Feedback](examples/it-systems-inventory/rupify-feedback.md)

## Current Limitations

- the main end-to-end skill workflow assumes a Codex-style environment with local skill support
- there is not yet a standalone vision artifact or supplementary specification artifact
- Mermaid outputs are practical publication artifacts, not strict UML interchange files
- document ingestion is planned but not yet implemented as a product workflow
