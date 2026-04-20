# End-to-End Usage

This document explains the supported end-to-end ways to use Rupify today.

## Choose The Right Command

- `rupify-render`: start from a canonical model and generate Markdown or Mermaid artifacts
- `rupify-publish-bundle`: start from a canonical model and package a stable publication bundle
- `rupify-ucp`: start from a canonical model and calculate only the UCP estimate
- `rupify-interview-to-formal`: start from an interview fixture and generate the normalized model plus the formal Markdown bundle
- `rupify-interview-replay`: start from an interview fixture and inspect replay, readiness, staleness, and trace validation
- `rupify-interview`: process one interview round directly

## Recommended Mental Model

Rupify has one central rule:

- the canonical model is the source of truth

Everything else hangs off that:

- interviews produce structured replay output
- replay output normalizes into the canonical model
- formal Markdown artifacts render from the canonical model
- Mermaid diagrams render from the canonical model
- UCP estimation renders from the canonical model
- publication bundles package model-backed outputs from the canonical model

Do not treat raw interview text, copied Markdown, or Mermaid files as the primary editing surface.

## Workflow 1: Model To Artifacts

Use this when you already have a canonical model.

### Formal Markdown Artifacts

```bash
uv run rupify-render \
  --model examples/it-systems-inventory/rupify-model.json \
  --output-dir /tmp/rupify-formal \
  --artifact-family formal
```

This renders:

- `system-document.md`
- `requirements-spec.md`
- `use-case-model.md`
- `use-case-documents.md`
- `scenario-documents.md`
- `domain-model.md`
- `interaction-model.md`
- `deployment-model.md`
- `state-model.md`

### UCP Estimate

```bash
uv run rupify-ucp --model examples/it-systems-inventory/rupify-model.json
```

Or through the renderer:

```bash
uv run rupify-render \
  --model examples/it-systems-inventory/rupify-model.json \
  --output-dir /tmp/rupify-ucp \
  --artifact-family ucp
```

### Downstream Planning Export

```bash
uv run rupify-export-planning \
  --model examples/it-systems-inventory/rupify-model.json \
  --output /tmp/rupify-planning-export.json
```

### Publication Bundle

```bash
uv run rupify-publish-bundle \
  --model examples/it-systems-inventory/rupify-model.json \
  --output-dir /tmp/rupify-publication-bundle \
  --archive /tmp/rupify-publication-bundle.zip
```

This writes one stable handoff layout containing:

- the canonical model snapshot
- the formal Markdown bundle
- the UCP estimate
- Mermaid publication artifacts
- the Speckify planning export
- a root bundle manifest with source-model metadata and stable relative paths

### Normalize Downstream Feedback

```bash
uv run rupify-normalize-feedback \
  --input tests/fixtures/speckify_feedback_example.json \
  --output /tmp/rupify-feedback.json
```

### Mermaid Outputs

```bash
uv run rupify-render \
  --model examples/it-systems-inventory/rupify-model.json \
  --output-dir /tmp/rupify-mermaid-domain \
  --artifact-family domain-mermaid

uv run rupify-render \
  --model examples/it-systems-inventory/rupify-model.json \
  --output-dir /tmp/rupify-mermaid-interaction \
  --artifact-family interaction-mermaid

uv run rupify-render \
  --model examples/it-systems-inventory/rupify-model.json \
  --output-dir /tmp/rupify-mermaid-deployment \
  --artifact-family deployment-mermaid

uv run rupify-render \
  --model examples/it-systems-inventory/rupify-model.json \
  --output-dir /tmp/rupify-mermaid-state \
  --artifact-family state-mermaid
```

## Workflow 2: Interview Fixture To Formal Artifacts

Use this when you have a replayable interview fixture and want the normalized model plus the formal
artifact bundle.

```bash
uv run rupify-interview-to-formal \
  --input tests/fixtures/it_systems_inventory_session.json \
  --output-dir /tmp/rupify-from-interview \
  --write-model /tmp/rupify-from-interview/rupify-model.json
```

This does three things:

1. replay the interview fixture
2. normalize the replay into the canonical model
3. render the formal Markdown artifact family

## Workflow 3: Replay Or Update An Existing Interview Fixture

Use this when new information arrives later and you want to update an existing interview session
without starting over.

### Replay Existing Fixture

```bash
uv run rupify-interview-replay \
  --input tests/fixtures/it_systems_inventory_session.json
```

### Replay With Targeted Updates

```bash
uv run rupify-interview-replay \
  --input tests/fixtures/it_systems_inventory_session.json \
  --updates path/to/updates.json
```

The replay result includes:

- merged interview answers
- readiness by view
- stale downstream artifacts
- traceability validation

## Workflow 4: Process One Interview Round

Use this for low-level testing or skill development.

```bash
uv run rupify-interview --round 3 --input path/to/answers.txt
```

You can also pipe text through stdin:

```bash
cat path/to/answers.txt | uv run rupify-interview --round 3
```

## Skill Usage

The repo also ships local skills intended for Codex-style environments.

- `$rupify`
- `$rupify-interview`
- `$rupify-discovery`
- `$rupify-use-cases`
- `$rupify-ucp`

Recommended skill-level flow:

1. start with `$rupify-interview` or `$rupify`
2. normalize with `$rupify-discovery`
3. refine actors/use cases with `$rupify-use-cases`
4. estimate with `$rupify-ucp`

These skills are repo-local assets, not a standalone published package format by themselves.

## Recommended Public Demo Flow

For a concrete example, use the IT systems inventory fixture and model under
`examples/it-systems-inventory/`.

Suggested public demo order:

1. replay the fixture
2. generate the normalized model
3. render the formal Markdown bundle
4. render the Mermaid bundle
5. inspect the checked-in example outputs

## Failure Expectations

Rupify does not silently invent fallback values for missing model fields.

In practice this means:

- UCP rendering can fail if required estimate inputs are missing
- YAML input support fails clearly unless the optional dependency is installed
- incomplete views should remain partial or blocked instead of being silently fabricated

See also: [Specification Publication Bundles](specification-publication-bundles.md)
