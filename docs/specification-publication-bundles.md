# Specification Publication Bundles

This document defines the stable publication layout for sharing a complete Rupify specification.

## Purpose

Use a publication bundle when you want one intentional handoff surface instead of a loose
collection of model files, rendered Markdown, and ad hoc downstream exports.

The canonical model remains the source of truth. The publication bundle is a generated package
that snapshots that model together with the derived outputs that are safe to publish or hand off.

## Bundle Layout

The current stable layout is:

```text
bundle-manifest.json
model/
  rupify-model.json
artifacts/
  formal/
    system-document.md
    requirements-spec.md
    use-case-model.md
    use-case-documents.md
    scenario-documents.md
    domain-model.md
    interaction-model.md
    deployment-model.md
    state-model.md
  ucp/
    ucp-estimate.md
  mermaid/
    domain-model.mmd
    interaction-model.mmd
    deployment-model.mmd
    state-model.mmd
exports/
  speckify-planning-export.json
```

## Manifest Contract

`bundle-manifest.json` is the root index for the package.

It records:

- the publication bundle schema version
- the source model semantic id and change metadata
- the artifact families included in the bundle
- the stable relative paths for the model, formal artifacts, Mermaid artifacts, and planning export
- a compact file-count summary

This keeps publication traceable back to the canonical model instead of treating the published
Markdown bundle as the source of truth.

## Generation

Generate a bundle from any normalized model:

```bash
uv run rupify-publish-bundle \
  --model examples/it-systems-inventory/rupify-model.json \
  --output-dir /tmp/rupify-publication-bundle
```

If you also want a zip archive for handoff:

```bash
uv run rupify-publish-bundle \
  --model examples/it-systems-inventory/rupify-model.json \
  --output-dir /tmp/rupify-publication-bundle \
  --archive /tmp/rupify-publication-bundle.zip
```

## Operational Rules

- do not hand-edit published bundle files as the primary source
- regenerate the bundle from the canonical model when requirements or design semantics change
- use the root manifest to locate bundle contents instead of hard-coding ad hoc file paths
- treat the planning export as the downstream machine contract, not as a replacement for the model
