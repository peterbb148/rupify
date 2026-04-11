---
name: specops-interview
description: Run the stakeholder interview for a software or system idea, collect the required discovery inputs in grouped rounds, and stop with explicit open questions when the information is not yet strong enough for downstream modeling or UCP estimation.
---

# SpecOps Interview

## Overview

Use this skill when the user wants the interview itself as a first-class step. This is the clean
entrypoint for discovery before the canonical model or generated artifacts exist.

## Interaction Contract

- Prefer short rounds with 2 to 4 prompts.
- Prefer compact answer shapes over large prose blocks.
- Give the user a copy-paste answer template when the round has multiple fields.
- Do not ask the user to edit long inline matrices or dense walls of text.
- If the platform offers native structured question UI, it may be used, but do not assume it exists.
  The prompt flow must still work cleanly in plain chat and terminal form.

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

## Prompting Style

- Start broad, then narrow.
- Use one round for discovery shape, one for actors/use cases, one for requirements, and then
  smaller UCP readiness rounds.
- When information is ambiguous, ask the smallest clarifying question that will remove the
  ambiguity.
- Read back what is already known before asking for the next missing inputs.

## UCP Prompt Rules

- Do not open with raw UCP scoring.
- Only ask for actor and use-case complexity after the discovery baseline is stable.
- Explain the UCP scale briefly before asking for scores.
- Correct the most common intuition mismatch explicitly:
  - system/API actors are often `simple`
  - human actors using a richer UI are often `complex`
- Explain that `0-5` factor inputs are influence scores, not quality grades.
- Ask for UCP values in small groups:
  - actor complexity
  - use-case complexity
  - technical factors
  - environmental factors
- For environmental factors, state clearly which higher values are positive and which indicate drag.
- When helpful, apply a reasonable provisional value and label it clearly as an assumption instead
  of forcing the user through an awkward scoring wall.

## Output Rules

- Ask short grouped questions, not one massive questionnaire.
- Keep confirmed facts, assumptions, and open questions separate.
- Do not invent missing inputs just to reach a complete estimate.
- Hand off to `specops-discovery` once the interview is complete enough to normalize.

## Routing

- Use `specops-discovery` after the interview to update `specops-model.yaml`.
- Use `specops` only when the user wants the full interview-to-artifact workflow in one pass.
