---
name: specops-interview
description: Run the stakeholder interview for a software or system idea, collect the required discovery inputs in grouped rounds, and stop with explicit open questions when the information is not yet strong enough for downstream modeling or UCP estimation.
---

# SpecOps Interview

## Overview

Use this skill when the user wants the interview itself as a first-class step. This is the clean
entrypoint for discovery before the canonical model or generated artifacts exist.

## Workflow

1. Confirm the request is about software or system requirements.
2. Run the interview in grouped rounds using `references/interview-rounds.md`.
3. Capture:
   - problem statement
   - scope boundary
   - business goals and success criteria
   - actors
   - candidate use cases
   - functional and non-functional requirements
   - UCP-relevant complexity and factor inputs
4. End with either:
   - a ready-to-normalize interview result for `specops-discovery`, or
   - explicit unresolved questions that block a defensible model or estimate

## Output Rules

- Ask short grouped questions, not one massive questionnaire.
- Keep confirmed facts, assumptions, and open questions separate.
- Do not invent missing inputs just to reach a complete estimate.
- Hand off to `specops-discovery` once the interview is complete enough to normalize.

## Routing

- Use `specops-discovery` after the interview to update `specops-model.yaml`.
- Use `specops` only when the user wants the full interview-to-artifact workflow in one pass.

