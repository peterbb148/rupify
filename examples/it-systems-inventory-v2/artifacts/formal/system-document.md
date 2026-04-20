# System / Subsystem Document

## System Name

A system to manage inventory of IT Systems themselves.

## Brief Description

We have many IT Systems and some overlap, some are free, some are expensive, all are slightly different.

All IT systems

## Risk Factors

- None

## System-Level Use Cases

- `register-a-system` Register a system (actor: Unspecified): Register a system
- `edit-metadata` edit metadata (actor: Unspecified): edit metadata
- `compare-overlapping-systems` compare overlapping systems (actor: Unspecified): compare overlapping systems
- `track-lifecycle-state` track lifecycle state (actor: Unspecified): track lifecycle state
- `review-risks` review risks (actor: Unspecified): review risks
- `see-costs` see costs (actor: Unspecified): see costs
- `approve-deprecation` approve deprecation (actor: Unspecified): approve deprecation
- `report-portfolio-gaps` report portfolio gaps (actor: Unspecified): report portfolio gaps

## System-Level Diagram References

- `use-case-model.md` for the detailed system-level use-case view
- `deployment-model.md` for the detailed architecture and runtime view


## Architecture Overview

- `component-system-inventory-web-app` System Inventory Web App [source: round 7 components_and_services]
- `component-system-inventory-api` System Inventory API [source: round 7 components_and_services]
- `component-reporting-consumers` Reporting Consumers [source: round 7 components_and_services]


## Interfaces and Integrations

- `interface-1` System Inventory Web App calls System Inventory API [source: round 7 interfaces_and_integrations]
- `interface-2` System Inventory API sends Reporting Consumers [source: round 7 interfaces_and_integrations]


## Runtime Boundaries

- `runtime-boundary-1` System Inventory API runs separately from the UI [source: round 7 runtime_boundaries]

## Subsystem Descriptions

- `component-system-inventory-web-app` System Inventory Web App [source: round 7 components_and_services]
- `component-system-inventory-api` System Inventory API [source: round 7 components_and_services]
- `component-reporting-consumers` Reporting Consumers [source: round 7 components_and_services]

## Artifact Lineage

- `trace-artifact-system-document-system-level-use-cases-register-a-system` register-a-system -> system-document.md#system-level use cases (canonical system-level use cases object renders into system-document.md)
- `trace-artifact-system-document-system-level-use-cases-edit-metadata` edit-metadata -> system-document.md#system-level use cases (canonical system-level use cases object renders into system-document.md)
- `trace-artifact-system-document-system-level-use-cases-compare-overlapping-systems` compare-overlapping-systems -> system-document.md#system-level use cases (canonical system-level use cases object renders into system-document.md)
- `trace-artifact-system-document-system-level-use-cases-track-lifecycle-state` track-lifecycle-state -> system-document.md#system-level use cases (canonical system-level use cases object renders into system-document.md)
- `trace-artifact-system-document-system-level-use-cases-review-risks` review-risks -> system-document.md#system-level use cases (canonical system-level use cases object renders into system-document.md)
- `trace-artifact-system-document-system-level-use-cases-see-costs` see-costs -> system-document.md#system-level use cases (canonical system-level use cases object renders into system-document.md)
- `trace-artifact-system-document-system-level-use-cases-approve-deprecation` approve-deprecation -> system-document.md#system-level use cases (canonical system-level use cases object renders into system-document.md)
- `trace-artifact-system-document-system-level-use-cases-report-portfolio-gaps` report-portfolio-gaps -> system-document.md#system-level use cases (canonical system-level use cases object renders into system-document.md)
- `trace-artifact-system-document-architecture-overview-component-system-inventory-web-app` component-system-inventory-web-app -> system-document.md#architecture overview (canonical architecture overview object renders into system-document.md)
- `trace-artifact-system-document-architecture-overview-component-system-inventory-api` component-system-inventory-api -> system-document.md#architecture overview (canonical architecture overview object renders into system-document.md)
- `trace-artifact-system-document-architecture-overview-component-reporting-consumers` component-reporting-consumers -> system-document.md#architecture overview (canonical architecture overview object renders into system-document.md)
- `trace-artifact-system-document-interfaces-and-integrations-interface-1` interface-1 -> system-document.md#interfaces and integrations (canonical interfaces and integrations object renders into system-document.md)
- `trace-artifact-system-document-interfaces-and-integrations-interface-2` interface-2 -> system-document.md#interfaces and integrations (canonical interfaces and integrations object renders into system-document.md)
- `trace-artifact-system-document-runtime-boundaries-runtime-boundary-1` runtime-boundary-1 -> system-document.md#runtime boundaries (canonical runtime boundaries object renders into system-document.md)

