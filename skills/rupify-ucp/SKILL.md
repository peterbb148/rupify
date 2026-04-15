---
name: rupify-ucp
description: Produce a deterministic Use Case Point estimate from the canonical Rupify model and fail clearly when required estimation inputs are missing.
---

# Rupify UCP

## Overview

Use this skill when the canonical model is complete enough to estimate. This skill is deterministic
where the method requires formulas.

## Workflow

1. Validate actor and use-case complexity values.
2. Validate technical and environmental factor scores.
3. Run the deterministic UCP calculation.
4. Present the result together with unresolved questions and assumptions.

## Command

```bash
uv run python -m rupify_tools.ucp_cli --model <path-to-model>
```

For YAML input:

```bash
uv sync --extra yaml
```

## Rules

- do not infer hidden fallback values
- fail clearly if required inputs are missing
- keep the estimate traceable to model fields and formulas

