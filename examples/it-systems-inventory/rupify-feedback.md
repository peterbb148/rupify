# Rupify Feedback from the IT Systems Inventory Example

## Purpose

This example is not only a sample output set. It is also a dogfooding artifact used to improve
Rupify itself.

## What This Example Validates

- The interview flow can capture a credible enterprise software problem statement.
- The current model is strong enough for overview artifacts plus the template-driven system and
  use-case document families.
- The existing renderer and deterministic UCP path can turn one model into consistent artifacts.

The current checked-in bundle now includes:

- overview artifacts like `requirements-spec.md`, `use-case-model.md`, `domain-model.md`, and
  `deployment-model.md`
- template-driven artifacts like `system-document.md`, `use-case-documents.md`, and
  `scenario-documents.md`

In this specific example, `scenario-documents.md` is currently empty because the model does not yet
carry explicit named scenario objects for the IT systems inventory case. That is an honest example
of current coverage, not a rendering failure.

## What This Example Exposes About Rupify

## 1. V1 is strong on discovery, weaker on modeling depth

The interview captured goals, actors, lifecycle states, risks, cost dimensions, and workflows
quickly. That validates the V1 discovery direction.

The same interview does not yet produce enough structure for full UML generation. It surfaces the
gap between use-case/UCP readiness and UML-ready analysis/design capture.

## 2. Ambiguity handling needs stronger guidance

This example surfaced several ambiguities that should become explicit Rupify guidance:

- ambiguous performance wording
- unclear role decomposition for governance users
- unclear status of integrations as first-class inventory objects or metadata fields
- unclear workflow depth for stage gates and approvals
- unclear analytical method for overlap and portfolio-gap detection

Rupify should make these ambiguity classes explicit during interview and normalization.

## 3. Actor and use-case complexity scoring needs clearer UX

The initial actor complexity answers reflected natural human intuition rather than standard UCP
interpretation. Rupify should do a better job of guiding users through UCP classification so the
system does not depend on later correction.

The same friction appeared in the interaction style itself: answering a large prompt with inline
complexity values is awkward in terminal/chat form and increases the chance of bad inputs.

## 4. Workflow-heavy enterprise systems need richer canonical structures

This example shows the need for stronger support for:

- configurable lifecycle models
- approval workflow/state models
- role-specific governance responsibilities
- portfolio analytics semantics
- downstream API contracts

These needs should directly inform the next model revisions.

## Improvement Directions Triggered by This Example

### V1-adjacent improvements

- add stronger interview prompts for ambiguity detection
- add explicit normalization guidance for enterprise governance roles
- improve interview UX so questions arrive in smaller, easier-to-answer groups
- add guidance for interpreting UCP complexity ratings
- add support for structured metadata taxonomies in the canonical model

### Concrete UX direction

- break interview rounds into smaller prompts with copy-paste templates
- avoid large inline classification walls
- split UCP capture into actor, use-case, technical, and environmental micro-rounds
- keep app-level structured UI optional rather than pretending it is always available

### V2 improvements

- domain and class modeling for inventory concepts
- workflow/state modeling for lifecycle and approvals
- interaction and architectural modeling for integrations and APIs
- RUP-aligned traceability from discovery to richer UML artifacts

## Related Issues

- `#2` Dogfood Rupify on the Rupify product definition
- `#5` Define the canonical rupify-model and skill pack scaffold
- `#16` Improve interview UX and reduce wall-of-text responses
- `#17` Improve UCP scoring guidance in the interview flow
- `#8` EPIC: Rupify V2 UML and formal specification translation
- `#11` Implement V2 domain and class modeling
- `#12` Implement V2 component and deployment modeling
- `#13` Implement V2 RUP traceability layer
- `#14` Implement V2 interaction diagram support
- `#15` Implement V2 state modeling support

## Working Rule for This Example

Keep this example as both:

- a reusable demonstration of the current interview-to-artifact workflow
- a standing source of product feedback for how Rupify should improve
