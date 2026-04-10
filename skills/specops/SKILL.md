---
name: specops
description: Orchestrate a structured software requirements discovery workflow that interviews stakeholders, builds or updates a canonical specops-model, and generates a requirements spec, use-case model, and UCP estimate from the same source of truth.
---

# SpecOps

## Overview

Use this as the entrypoint for SpecOps work. It is optimized for software and system requirements,
not generic consulting discovery.

## Workflow

1. Confirm the request is about software or system requirements.
2. Invoke `specops-interview` when the user wants the interview as a first-class step.
3. Run a structured interview using the guide in `references/interview-guide.md` if the work stays
   inside the orchestrator.
4. Build or update `specops-model.yaml` using the contract in `references/specops-model.md`.
5. If critical UCP inputs are missing, stop and present the unresolved questions explicitly.
6. Generate or refresh:
   - `requirements-spec.md`
   - `use-case-model.md`
   - `ucp-estimate.md`

## Routing

- Use `specops-interview` to run the interview directly as a skill.
- Use `specops-discovery` to normalize requirements into the canonical model.
- Use `specops-use-cases` to refine actors, scenarios, and complexity.
- Use `specops-ucp` to validate scoring inputs and produce the estimate.

## Commands

Python in this repo runs with `uv`.

```bash
uv run python -m specops_tools.render_cli --model <path-to-model> --output-dir <artifact-dir>
uv run python -m specops_tools.ucp_cli --model <path-to-model>
```

For YAML files, install the optional extra first:

```bash
uv sync --extra yaml
```

## Output Rules

- Treat the canonical model as the source of truth.
- Do not regenerate artifacts from raw chat state if the model exists.
- Do not invent missing estimation values. Keep open questions explicit.
