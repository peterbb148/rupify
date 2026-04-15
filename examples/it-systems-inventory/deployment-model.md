# Deployment Model

## Project

- Name: A system to manage inventory of IT Systems themselves.
- Domain: Unspecified

## Scope

All IT systems

## Components

- `component-system-inventory-web-app` System Inventory Web App [source: round 7 components_and_services]
- `component-system-inventory-api` System Inventory API [source: round 7 components_and_services]
- `component-reporting-consumers` Reporting Consumers [source: round 7 components_and_services]


## Interfaces and Integrations

- `interface-1` System Inventory Web App calls System Inventory API [source: round 7 interfaces_and_integrations]
- `interface-2` System Inventory API sends Reporting Consumers [source: round 7 interfaces_and_integrations]


## Runtime Boundaries

- `runtime-boundary-1` System Inventory API runs separately from the UI [source: round 7 runtime_boundaries]


## Artifact Lineage

- `trace-artifact-deployment-model-components-component-system-inventory-web-app` component-system-inventory-web-app -> deployment-model.md#components (canonical components object renders into deployment-model.md)
- `trace-artifact-deployment-model-components-component-system-inventory-api` component-system-inventory-api -> deployment-model.md#components (canonical components object renders into deployment-model.md)
- `trace-artifact-deployment-model-components-component-reporting-consumers` component-reporting-consumers -> deployment-model.md#components (canonical components object renders into deployment-model.md)
- `trace-artifact-deployment-model-interfaces-and-integrations-interface-1` interface-1 -> deployment-model.md#interfaces and integrations (canonical interfaces and integrations object renders into deployment-model.md)
- `trace-artifact-deployment-model-interfaces-and-integrations-interface-2` interface-2 -> deployment-model.md#interfaces and integrations (canonical interfaces and integrations object renders into deployment-model.md)
- `trace-artifact-deployment-model-runtime-boundaries-runtime-boundary-1` runtime-boundary-1 -> deployment-model.md#runtime boundaries (canonical runtime boundaries object renders into deployment-model.md)

