# Contributing

## Scope

Rupify is a model-driven specification system. Contributions should preserve that design:

- interview and discovery feed the canonical model
- the canonical model is the source of truth
- Markdown and Mermaid artifacts are generated from the model
- deterministic utilities own the brittle or formula-driven parts

## Local Setup

```bash
uv sync
```

For YAML support:

```bash
uv sync --extra yaml
```

The current Python package and CLI names still use the `specops` prefix for compatibility.

## Useful Commands

Run the test suite:

```bash
uv run python -m unittest
```

Render formal artifacts from a model:

```bash
uv run specops-render \
  --model examples/it-systems-inventory/specops-model.json \
  --output-dir /tmp/specops-formal \
  --artifact-family formal
```

Replay the checked-in interview fixture:

```bash
uv run specops-interview-replay \
  --input tests/fixtures/it_systems_inventory_session.json
```

Generate the formal bundle directly from the fixture:

```bash
uv run python -m specops_tools.interview_to_formal_cli \
  --input tests/fixtures/it_systems_inventory_session.json \
  --output-dir /tmp/specops-from-interview \
  --write-model /tmp/specops-from-interview/specops-model.json
```

## Contribution Rules

- do not bypass the canonical model by treating generated artifacts as the primary source
- do not add invented fallback paths unless the task explicitly requires them
- prefer clear failure over silent degradation
- keep examples and generated bundles synchronized with the current model contract
- when model semantics change, update the checked-in example bundle as part of the same work

## Pull Request Expectations

- keep work tied to a GitHub issue
- keep one issue per branch
- include verification notes in the PR description
- update docs when capability or workflow shape changes

## Good First Areas

- documentation and workflow polish
- test coverage around example fixtures and artifact generation
- productization work under the current open epics
- document-ingestion groundwork that preserves the canonical model workflow
