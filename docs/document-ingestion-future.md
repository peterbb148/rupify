# Document Ingestion Future Direction

## Purpose

Rupify should eventually support one or more unstructured documents as first-class input for
building a system specification.

This should not replace the canonical model or bypass the interview workflow. It should add a new
input path into the same model and artifact pipeline.

Related issue: `#65`

## Product Shape

The intended future flow is:

1. ingest one or more source documents
2. extract candidate facts and evidence from those documents
3. normalize the extracted information into the canonical model
4. identify gaps, conflicts, and unresolved areas
5. generate targeted follow-up interview questions only where needed
6. render the existing artifacts from the merged canonical model

This means Rupify would support:

- interview-first specification
- document-first specification
- hybrid document + interview specification

## Design Principles

- documents produce evidence-backed candidate model data, not silent final truth
- the canonical model remains the source of truth
- conflicts and uncertainty stay explicit
- document provenance must be preserved down to the normalized model objects
- document ingestion should converge with the existing readiness, staleness, and traceability
  pipeline

## Expected Model Impact

Document ingestion will need explicit source metadata on normalized objects, such as:

- document id
- section, heading, or page reference
- extraction note or evidence summary
- confidence
- conflict status

This should align with the existing provenance and traceability direction rather than create a
second parallel metadata scheme.

## Why This Matters

Real system knowledge is often distributed across:

- architecture notes
- business process documents
- operational manuals
- interface descriptions
- old requirement sets

If Rupify can only interview stakeholders, it leaves value on the table and forces manual
re-entry of information that already exists in written form.

## Recommended Implementation Order

1. define the document source and provenance contract
2. add deterministic extraction targets for canonical structures
3. support gap analysis against readiness gates
4. add hybrid merge behavior between documents and interview answers
5. expose the workflow through a CLI or skill entry point

## Non-Goal

The goal is not to generate a specification directly from opaque document text without an explicit
canonical model step.

The correct architecture is:

- documents -> candidate model data
- candidate model data -> canonical model
- canonical model -> rendered specification artifacts
