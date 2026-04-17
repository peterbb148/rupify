---
name: rupify-discovery
description: Capture software requirements through a structured interview and normalize the answers into the canonical rupify-model without inventing missing information.
---

# Rupify Discovery

## Overview

Use this skill to normalize the interview output into the canonical model. It can also gather
missing details directly when the interview was partial, but the intended first step is
`rupify-interview`.

## Responsibilities

- capture the problem statement and system scope
- convert stakeholder language into normalized actors, goals, and requirements
- separate assumptions from confirmed facts
- identify open questions that block downstream estimation
- update `rupify-model.yaml` as the source of truth

## Rules

- keep software and system scope explicit
- prefer short, grouped interview rounds over one long questionnaire
- write down uncertainty rather than smoothing it over
- update the model, not just the chat transcript
