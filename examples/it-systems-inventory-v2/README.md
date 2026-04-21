# IT Systems Inventory V2 Bundle

This directory is the V2 checked-in publication bundle for the existing CMDB-style interview
fixture at [tests/fixtures/it_systems_inventory_session.json](/Volumes/Data/GitHub/Peterbb148/rupify/tests/fixtures/it_systems_inventory_session.json).

It was generated from the current Rupify pipeline rather than assembled by hand:

```bash
uv run rupify-interview-to-formal \
  --input tests/fixtures/it_systems_inventory_session.json \
  --output-dir /tmp/rupify-cmdb-v2-formal \
  --write-model /tmp/rupify-cmdb-v2-formal/rupify-model.json

uv run rupify-publish-bundle \
  --model /tmp/rupify-cmdb-v2-formal/rupify-model.json \
  --output-dir /tmp/rupify-cmdb-v2-bundle
```

## Purpose

This bundle is the concrete proof for the downstream Speckify integration path under issue `#84`,
with the import-cleanliness blockers from issue `#151` corrected upstream in Rupify.

It demonstrates that the existing CMDB interview can now be carried all the way through:

- canonical model normalization
- formal Markdown artifact rendering
- Mermaid publication artifacts
- UCP output
- stable publication bundle packaging
- Speckify-facing planning export generation

## Speckify Handoff Surface

The primary downstream contract for Speckify is:

- [exports/speckify-planning-export.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/it-systems-inventory-v2/exports/speckify-planning-export.json)

The root publication index for the full handoff bundle is:

- [bundle-manifest.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/it-systems-inventory-v2/bundle-manifest.json)

The canonical model snapshot used to generate the bundle is:

- [model/rupify-model.json](/Volumes/Data/GitHub/Peterbb148/rupify/examples/it-systems-inventory-v2/model/rupify-model.json)

## Current Result

This V2 export currently shows:

- a complete publication bundle with 17 files
- 82 flattened planning elements
- 127 trace links
- 29 ready normative elements
- 0 blocking ambiguities
- 0 unresolved trace references
- 0 duplicate exported element IDs
- explicit requirement obligations where the upstream requirement normalization can derive them safely

## Known Limits In This Example

- [artifacts/formal/scenario-documents.md](/Volumes/Data/GitHub/Peterbb148/rupify/examples/it-systems-inventory-v2/artifacts/formal/scenario-documents.md)
  is still empty because this fixture does not yet carry explicit named scenario objects
- this proves the Rupify export boundary, not a full Speckify repository-side import workflow
