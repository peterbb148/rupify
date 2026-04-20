# Loyalty Platform V2 Bundle

This directory is the V2 checked-in publication bundle for the legacy loyalty-platform example at
[examples/loyalty-platform/specops-model.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/loyalty-platform/specops-model.json).

It was generated from the current publication pipeline:

```bash
uv run rupify-publish-bundle \
  --model examples/loyalty-platform/specops-model.json \
  --output-dir /tmp/rupify-loyalty-v2-bundle
```

## Purpose

This bundle gives the loyalty example the same current publication layout as the rest of Rupify:

- formal Markdown artifacts
- Mermaid publication artifacts
- UCP output
- bundle manifest
- a checked-in planning export path

## Current Result

This V2 bundle currently shows:

- a complete publication bundle with 17 generated files
- a valid bundle manifest at
  [bundle-manifest.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/loyalty-platform-v2/bundle-manifest.json)
- a canonical model snapshot at
  [model/rupify-model.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/loyalty-platform-v2/model/rupify-model.json)
- a Speckify export path at
  [exports/speckify-planning-export.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/loyalty-platform-v2/exports/speckify-planning-export.json)

## Important Limitation

Unlike the CMDB V2 bundle, this loyalty-platform example still starts from an older `specops-model`
shape rather than a newer replay-normalized Rupify model.

That means the checked-in planning export is currently structurally valid but empty:

- `element_count = 0`
- `trace_link_count = 0`

So this bundle is a publication-layout refresh, not yet a full Speckify handoff proof.
