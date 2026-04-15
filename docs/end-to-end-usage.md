# End-to-End Usage

This document explains the supported end-to-end ways to use Rupify today.

## Recommended Mental Model

Rupify has one central rule:

- the canonical model is the source of truth

Everything else hangs off that:

- interviews produce structured replay output
- replay output normalizes into the canonical model
- formal Markdown artifacts render from the canonical model
- Mermaid diagrams render from the canonical model
- UCP estimation renders from the canonical model

Do not treat raw interview text, copied Markdown, or Mermaid files as the primary editing surface.

## Workflow 1: Model To Artifacts

Use this when you already have a canonical model.

### Formal Markdown Artifacts

```bash
uv run specops-render \
  --model examples/it-systems-inventory/specops-model.json \
  --output-dir /tmp/specops-formal \
  --artifact-family formal
```

This renders:

- `requirements-spec.md`
- `use-case-model.md`
- `domain-model.md`
- `interaction-model.md`
- `deployment-model.md`
- `state-model.md`

### UCP Estimate

```bash
uv run specops-ucp --model examples/it-systems-inventory/specops-model.json
```

Or through the renderer:

```bash
uv run specops-render \
  --model examples/it-systems-inventory/specops-model.json \
  --output-dir /tmp/specops-ucp \
  --artifact-family ucp
```

### Mermaid Outputs

```bash
uv run specops-render \
  --model examples/it-systems-inventory/specops-model.json \
  --output-dir /tmp/specops-mermaid-domain \
  --artifact-family domain-mermaid

uv run specops-render \
  --model examples/it-systems-inventory/specops-model.json \
  --output-dir /tmp/specops-mermaid-interaction \
  --artifact-family interaction-mermaid

uv run specops-render \
  --model examples/it-systems-inventory/specops-model.json \
  --output-dir /tmp/specops-mermaid-deployment \
  --artifact-family deployment-mermaid

uv run specops-render \
  --model examples/it-systems-inventory/specops-model.json \
  --output-dir /tmp/specops-mermaid-state \
  --artifact-family state-mermaid
```

## Workflow 2: Interview Fixture To Formal Artifacts

Use this when you have a replayable interview fixture and want the normalized model plus the formal
artifact bundle.

```bash
uv run python -m specops_tools.interview_to_formal_cli \
  --input tests/fixtures/it_systems_inventory_session.json \
  --output-dir /tmp/specops-from-interview \
  --write-model /tmp/specops-from-interview/specops-model.json
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
uv run specops-interview-replay \
  --input tests/fixtures/it_systems_inventory_session.json
```

### Replay With Targeted Updates

```bash
uv run specops-interview-replay \
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
uv run specops-interview --round 3 --input path/to/answers.txt
```

You can also pipe text through stdin:

```bash
cat path/to/answers.txt | uv run specops-interview --round 3
```

## Skill Usage

The repo also ships local skills intended for Codex-style environments.

Those skill names still use the older `specops` prefix for compatibility:

- `$specops`
- `$specops-interview`
- `$specops-discovery`
- `$specops-use-cases`
- `$specops-ucp`

Recommended skill-level flow:

1. start with `$specops-interview` or `$specops`
2. normalize with `$specops-discovery`
3. refine actors/use cases with `$specops-use-cases`
4. estimate with `$specops-ucp`

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
