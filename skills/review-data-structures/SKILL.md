---
name: review-data-structures
description: Review application data structures, fixtures, schemas, TypeScript types, persistence models, API contracts, and UI projections. Use when deciding whether current shapes are clear, durable, database-ready, easy to extend, or burdened by duplicate types and transformations. Produces direct but motivating improvements. Do not use for query-performance tuning or database operations unless data-model design is also in scope.
---

# Review Data Structures

Review the data model as a system. Find changes that reduce concepts, prevent invalid states, clarify ownership, and make future work easier.

The goal is not theoretical purity. Prefer the design with fewer representations, fewer unjustified transformations, clear boundaries, safe durable state, and low extension cost.

Default to a read-only review. Do not edit schemas, fixtures, migrations, or application code unless the user asks for implementation.

## Review stance

Be candid and constructive. The review should make improvement feel attainable.

- Identify the strongest foundations first. State what should remain.
- Describe weaknesses as specific model risks or maturity gaps, not as developer failures.
- Connect each recommendation to a practical gain: less code, safer state, easier queries, simpler UI, or cheaper extension.
- Prefer a small sequence of high-leverage changes over a long fault list.
- Give credit for prototype shapes that serve the UI well, while distinguishing them from safe persistence models.
- Do not soften a high-risk finding. Explain it plainly, then give a realistic route forward.

## Core model

Prefer one canonical representation of a concept through most of the system:

```text
external or persisted input
-> validate and normalize at the trust boundary
-> canonical domain representation
-> API transport
-> client
-> UI
```

Each different shape must justify itself. Valid reasons include security filtering, aggregation, a stable read projection, third-party adaptation, normalization, or a real trust boundary.

Question shapes created only because data crossed a folder, framework layer, or component boundary.

## First classify each shape

Do not compare types only by field similarity. Determine their role:

- Durable entity: identity, lifecycle, ownership, and persistence.
- Immutable value or snapshot: compared by content and often stored as one unit.
- Domain variant: one legitimate state in a discriminated union.
- Command or untrusted input: validated at entry.
- Event or audit record: records something that happened.
- Read projection: a deliberate query result for a use case.
- UI state: loading, selection, drafts, formatting, or local interaction.
- Fixture or scenario container: test and demonstration data, not automatically a domain concept.
- External representation: owned by another system.

Merge shapes only when their semantics match. Keep a distinct type when it protects a real boundary or concept.

## Investigate from evidence

Inspect definitions and actual consumers. Search for runtime schemas, interfaces, aliases, fixtures, mappers, serializers, API handlers, persistence code, tests, and UI adapters.

For the important concepts, record:

```text
concept
canonical candidate and owner
where it is created and persisted
who consumes it
equivalent or competing shapes
transformations and renames
runtime validation
identity and relationships
lifecycle states
```

Trace representative flows end to end. Count named types, schemas, mapping steps, property renames, and serialization changes only when the count helps explain real complexity.

Read tests and fixtures as design evidence. A passing fixture test proves only the invariant it checks. It does not prove database readiness.

## Apply two review lenses

### 1. Structural simplicity

Check for:

- Parallel `Domain`, `DTO`, `Client`, `ViewModel`, and props hierarchies.
- Nearly identical interfaces and aliases without added safety.
- Mappers that copy or rename fields without semantic work.
- Repeated date, enum, null, or optionality conversions.
- Generated types immediately converted to handwritten copies.
- `Pick`, `Omit`, and conditional-type chains that hide a simple contract.
- Component props that recreate a domain object without a good decoupling reason.
- Runtime validation repeated after data has entered trusted code.

Prefer schema-inferred TypeScript types at real trust boundaries. Prefer transport-friendly canonical values when they remove repeated conversion. Do not force a component to accept a large domain object when it is genuinely a generic primitive.

### 2. Durable domain safety

For data that may reach a real database, test:

- Identity: Does each durable concept have a stable identity where needed?
- Ownership and authorization: Is there one clear path from a record to its owner?
- Lifecycle: Can status fields express only valid states? Use discriminated unions when they remove invalid combinations.
- Required output: Do running or failed records need fake success data to satisfy a type?
- Relationships: Can references be enforced, or can parallel IDs and arrays disagree?
- Cardinality and ordering: Are one-to-one, one-to-many, rank, and order explicit?
- Source of truth: Is mutable or failure state copied across records?
- Versioning: Are snapshots immutable? Is the current head explicit? Can stale writes be detected?
- Granularity: Are decisions, evidence, or permissions attached to the exact item they govern?
- Concurrency: Can claims, counters, allocations, retries, and approvals be atomic and idempotent?
- Deletion and history: Is retention, cascading, audit, or soft deletion needed?
- Persistence validation: Is loaded data validated and migrated instead of cast?
- Privacy: Are secrets, tokens, payment display strings, or presentation text mistaken for durable fields?

Do not derive tables by copying fixture interfaces. First establish a valid domain model. Then choose relational columns, validated JSON, or read projections based on access, integrity, and update patterns.

## Challenge the model

Use concrete extension and failure tests that fit the product:

- Add a field to a core entity.
- Add a lifecycle state such as canceled or partially complete.
- Attach different evidence or decisions to two child items.
- Retry a failed job.
- Approve a change against a stale version.
- Rename, transfer, or delete an owned entity.
- Process two concurrent claims or updates.

Compare the current and proposed designs. Show which types, schemas, mappers, and consumers must change. A good model keeps ordinary extensions local and makes unsafe operations explicit.

## Form findings

Report only findings supported by direct evidence. Include exact file links and line numbers when available.

For each material finding, explain:

```text
severity and confidence
current shape
invalid state, maintenance cost, or product constraint it creates
recommended canonical shape
what the recommendation lets the team delete or simplify
smallest safe migration step
```

Use High for integrity, ownership, lifecycle, or application-wide complexity risks. Use Medium for contained maintenance or extension costs. Use Low for local naming and simplification work.

Avoid false precision. If you score the model, define the dimensions and support each score. Separate prototype quality from persistence readiness when both matter.

## Prefer removal with purpose

Prefer deleting a redundant type or mapper over adding a mapping framework. Prefer one status-safe union over many nullable properties. Prefer one authoritative relationship over copied IDs or parallel arrays.

Do not remove a projection merely because it differs from the canonical entity. A stable summary, search result, permission-filtered response, or aggregated workspace can be a legitimate contract. Name it for its product meaning rather than its layer.

## Deliver the review

Lead with the answer. Adapt the report to the evidence, but normally include:

1. Executive assessment, with separate prototype and persistence judgments when relevant.
2. Strengths to preserve.
3. Highest-leverage findings in priority order.
4. Current and proposed data-flow examples.
5. Types and transformations to delete, merge, rename, or keep.
6. A recommended target domain model, without treating it as final DDL.
7. Extension and failure tests that demonstrate the improvement.
8. An incremental migration order.
9. Verification limits, including failed or inconclusive checks.

Make the migration order motivating. Show the first change that unlocks later simplifications. Make clear which good parts survive the migration. End with a practical next step, not a generic call for cleanup.

Do not claim verification from a command that timed out, failed, or produced inconclusive output.
