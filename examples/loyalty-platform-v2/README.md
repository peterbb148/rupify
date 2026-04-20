# Loyalty Platform V2 Bundle

This directory is the V2 checked-in publication bundle for the loyalty-platform interview fixture at
[tests/fixtures/loyalty_platform_session.json](/Volumes/Data/GitHub/Peterbb148/rupify/tests/fixtures/loyalty_platform_session.json).

It was generated from the current interview and publication pipeline:

```bash
uv run rupify-interview-to-formal \
  --input tests/fixtures/loyalty_platform_session.json \
  --output-dir /tmp/rupify-loyalty-v2-formal \
  --write-model /tmp/rupify-loyalty-v2-formal/rupify-model.json

uv run rupify-publish-bundle \
  --model /tmp/rupify-loyalty-v2-formal/rupify-model.json \
  --output-dir /tmp/rupify-loyalty-v2-bundle
```

## Purpose

This bundle gives the loyalty example the same current replay-based V2 treatment as the CMDB case:

- interview replay into the canonical model
- formal Markdown artifacts
- Mermaid publication artifacts
- UCP output
- bundle manifest
- Speckify planning export

## Speckify Handoff Surface

The primary downstream contract for Speckify is:

- [exports/speckify-planning-export.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/loyalty-platform-v2/exports/speckify-planning-export.json)

The root publication index for the full handoff bundle is:

- [bundle-manifest.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/loyalty-platform-v2/bundle-manifest.json)

The canonical model snapshot used to generate the bundle is:

- [model/rupify-model.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/loyalty-platform-v2/model/rupify-model.json)

## Current Result

This V2 export currently shows:

- a complete publication bundle with 17 generated files
- 108 flattened planning elements
- 144 trace links
- 62 ready normative elements
- 0 blocking ambiguities
- 0 duplicate exported element IDs
- 0 unresolved trace references

## Notes

- this fixture was reconstructed from the legacy loyalty example so that the product can now be
  exercised through the current interview/replay pipeline
- the replay-generated UCP estimate is now [artifacts/ucp/ucp-estimate.md](/Volumes/Data/GitHub/Peterbb148/rupify/examples/loyalty-platform-v2/artifacts/ucp/ucp-estimate.md)
  rather than being inherited directly from the old checked-in model
