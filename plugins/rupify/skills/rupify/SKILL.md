---
name: rupify
description: Orchestrate a structured software requirements discovery workflow that interviews stakeholders, builds or updates a canonical rupify-model, and generates a requirements spec, use-case model, and UCP estimate from the same source of truth.
---

# Rupify

## Overview

Use this as the entrypoint for Rupify work. It is optimized for software and system requirements,
not generic consulting discovery.

## Workflow

1. Confirm the request is about software or system requirements.
2. Invoke `rupify-interview` when the user wants the interview as a first-class step.
3. Run a structured interview using the guide in `references/interview-guide.md` if the work stays
   inside the orchestrator.
4. Build or update `rupify-model.yaml` using the contract in `references/rupify-model.md`.
5. If critical UCP inputs are missing, stop and present the unresolved questions explicitly.
6. Generate or refresh:
   - `requirements-spec.md`
   - `use-case-model.md`
   - `ucp-estimate.md`

## Routing

- Use `rupify-interview` to run the interview directly as a skill.
- Use `rupify-discovery` to normalize requirements into the canonical model.
- Use `rupify-use-cases` to refine actors, scenarios, and complexity.
- Use `rupify-ucp` to validate scoring inputs and produce the estimate.

## Commands

Python in this repo runs with `uv`.

When you need the deterministic renderer from the installed plugin, prefer the bundled helper
script at `scripts/render_artifacts.py`. It resolves the bundled `src/rupify_tools` package from
the plugin root.

For direct repo development, these commands are still valid:

```bash
uv run python -m rupify_tools.render_cli --model <path-to-model> --output-dir <artifact-dir>
uv run python -m rupify_tools.ucp_cli --model <path-to-model>
```

For YAML files, install the optional extra first:

```bash
uv sync --extra yaml
```

## Output Rules

- Treat the canonical model as the source of truth.
- Do not regenerate artifacts from raw chat state if the model exists.
- Do not invent missing estimation values. Keep open questions explicit.
