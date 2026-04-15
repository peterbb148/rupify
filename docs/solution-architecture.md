# Rupify Solution Architecture

## Overview

Rupify is structured as a skill pack with a small deterministic tooling layer underneath it. The
skills define the interview and reasoning workflow. The Python tools provide calculation and
rendering paths where freeform prompting would be brittle.

## Core Architecture

## 1. Interview Entry Layer

The interview is a first-class skill entrypoint: `specops-interview`. It owns the stakeholder
conversation and gathers the inputs needed for modeling and estimation readiness.

Responsibilities:

- run the interview in grouped rounds
- separate facts, assumptions, and open questions
- stop clearly when the input is insufficient for normalization or UCP

V1.5 extends this layer toward iterative interview management rather than one linear pass. The
workflow should support targeted re-interview of affected views when new information appears later,
instead of forcing a full restart.

## 2. Orchestrator Layer

The `specops` skill is the entrypoint. It performs scope checks, runs the structured interview,
builds or updates the canonical model, and coordinates the downstream artifact generation flow.

Responsibilities:

- verify the request is about software or system requirements
- collect business goals, actors, use cases, constraints, and estimation inputs
- stop clearly when the model is not sufficient for a defensible estimate
- invoke `specops-interview` when the interview should be run as its own skill
- route to subskills using the canonical model instead of reinterpreting raw chat history

## 3. Domain Skills

The orchestrator delegates to focused skills:

- `specops-interview` for the interview itself
- `specops-discovery` for elicitation and normalization
- `specops-use-cases` for actor and use-case structure
- `specops-ucp` for complexity classification and UCP scoring

This keeps each skill narrow and reusable without turning the repo into a plugin or application.

## 4. Canonical Model

The project model is the system boundary between interview logic and generated artifacts.

Required sections:

- project summary and problem statement
- business goals and success criteria
- actors
- use cases
- assumptions and open questions
- functional and non-functional requirements
- UCP inputs
- reserved placeholders for future UML and formal specification translations

The next model evolution must also represent ambiguity, provenance, readiness, and staleness so the
system can preserve incomplete or conflicting information honestly and determine which downstream
artifacts need regeneration.

The canonical path is `specops-model.yaml`. A JSON mirror is included in examples so the offline
tooling can run without the optional YAML extra.

## 5. Deterministic Python Utilities

The Python utilities live in `src/specops_tools/` and are executed with `uv run`.

Components:

- `ucp.py`: deterministic UCP calculation
- `render.py`: Markdown artifact rendering
- `structured_io.py`: JSON and optional YAML model loading
- CLI modules for command-line use and skill wrapper scripts

The tooling does not invent heuristic fallbacks. If YAML support is requested without the optional
dependency, the command fails clearly and tells the user to run `uv sync --extra yaml`.

The same rule should apply to richer specification outputs: if a view is not ready, Rupify should
fail clearly or mark that view as partial rather than silently inventing structure.

## 6. Dogfooding Loop

Rupify is expected to define and refine itself.

The loop is:

1. create or update a spec in `.specify/specs/`
2. convert that spec into GitHub issues
3. implement on a dedicated branch
4. feed the lessons back into the skills, model, or constitution
