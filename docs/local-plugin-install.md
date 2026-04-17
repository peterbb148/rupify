# Local Plugin Install

This repo now includes a repo-local Codex plugin bundle at `plugins/rupify/` and a repo marketplace
at `.agents/plugins/marketplace.json`.

## What Is Bundled

- the Rupify skill set under `plugins/rupify/skills/`
- a plugin manifest at `plugins/rupify/.codex-plugin/plugin.json`
- a bundled `src/rupify_tools/` tree so plugin helper scripts can import the Python utilities

## Install In Codex

1. Open this repository in Codex.
2. Restart Codex if it was already open before the marketplace file was added.
3. Open the Plugin Directory.
4. Select the marketplace named `Rupify Local Plugins`.
5. Install `Rupify`.

## Current Scope Boundary

This first pass is designed for local installation and use with the checked-out `rupify` repository.

- The plugin packages the repo's existing skills.
- The plugin also bundles `src/rupify_tools/` so helper scripts shipped inside the plugin can import
  the deterministic renderer and UCP code.
- The plugin does not yet provide a standalone published app, connector mapping, or MCP server
  configuration.
- Public distribution is still subject to OpenAI's app submission flow.

## Verification Notes

- The marketplace path is repo-relative: `./plugins/rupify`
- The manifest skill path is plugin-relative: `./skills/`
- The bundled helper scripts expect `src/` to live at the plugin root, which is now true for this
  package layout
