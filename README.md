# SpecOps

SpecOps is a Codex-native skill pack for software requirements discovery. It is designed to
interview a stakeholder, normalize the answers into a canonical project model, and generate three
first-class artifacts from the same source of truth:

- `requirements-spec.md`
- `use-case-model.md`
- `ucp-estimate.md`

The interview step can be invoked directly as the `$specops-interview` skill.

The repository is documentation-first and dogfood-oriented. The immediate goal is to use SpecOps to
specify and improve SpecOps itself.

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
- [Dogfooding Workflow](docs/dogfooding.md)
- [GitHub Issue Map](docs/github-issue-map.md)
- [SpecKit Constitution](.specify/memory/constitution.md)

## Dogfooding Example

The IT systems inventory example is both a sample workflow output and a feedback input for improving
SpecOps:

- [Example Model](/Volumes/Data/GitHub/Peterbb148/specops/examples/it-systems-inventory/specops-model.yaml)
- [Example Feedback](/Volumes/Data/GitHub/Peterbb148/specops/examples/it-systems-inventory/specops-feedback.md)
