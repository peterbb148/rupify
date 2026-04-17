# Dogfooding Workflow

## Principle

Rupify should be used to create Rupify as early as possible. The repository should not rely on
freeform design notes once the core workflow exists.

## First Dogfooding Loop

The first loop for this repo is:

1. capture the Rupify product goal and boundaries
2. represent them in a canonical model or feature spec
3. generate the first documentation and issue hierarchy
4. implement the minimum skill pack and deterministic tooling
5. refine the workflow based on friction discovered while using it on itself

## Repo Convention

- keep the dogfooding spec in `.specify/specs/001-dogfood-rupify/`
- keep long-lived governance rules in `.specify/memory/constitution.md`
- keep work tracked in GitHub issues
- prefer updating the model or spec over adding disconnected notes
- when an example reveals product gaps, keep the example and add an explicit feedback artifact next
  to it

## Working Agreement

- every meaningful change should be traceable to a spec or issue
- open questions should remain explicit until resolved
- estimation should not hide uncertainty
- if a workflow step is too awkward to use on Rupify itself, treat that as a product defect

## Example-Driven Improvement

Examples in `examples/` serve two purposes:

- show what Rupify can currently produce
- expose where the system still needs to improve

When an example is important enough to shape the product, keep a sibling feedback file that records:

- what the example validated
- what the example exposed as weaknesses or ambiguity
- which existing issues or epics should absorb the learning

Current dogfooding example:

- `examples/it-systems-inventory/`
- `examples/it-systems-inventory/rupify-feedback.md`

The checked-in IT systems inventory bundle should now demonstrate both layers of the formal output:

- overview artifacts such as `requirements-spec.md`, `use-case-model.md`, and `deployment-model.md`
- compiled template-driven documents such as `system-document.md`, `use-case-documents.md`, and
  `scenario-documents.md`
