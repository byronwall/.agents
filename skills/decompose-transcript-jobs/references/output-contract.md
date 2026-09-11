# Transcript Decomposition Output Contract

Use this contract to keep transcript analyses comparable across projects and
iterations. The artifact count may vary; the underlying model and section names
should remain stable.

## Canonical finding record

Maintain these fields while analyzing. The final documents may present them as
prose rather than a table.

| Field | Meaning |
| --- | --- |
| `id` | Stable local identifier such as `J01`, `B02`, or `T03` |
| `type` | Job, outcome, pain, requirement, constraint, decision, solution, current-state claim, question, or speculation |
| `actor` | Person, team, business, operator, or system seeking progress |
| `statement` | Normalized finding |
| `theme` | Canonical work stream or product responsibility |
| `evidence` | One or more source locators |
| `confidence` | Explicit or inferred |
| `commitment` | Baseline, decided, near-term candidate, exploratory, or parked |
| `implications` | Possible product behavior, not part of the job itself |
| `tensions` | Contradictions, dependencies, or unresolved tradeoffs |

## Artifact selection

Follow the user's explicit request first.

### Single document

Use one document when the user asks for one, the transcript describes one
bounded product decision, or the total result remains easy to scan.

Recommended sections:

1. Purpose and source
2. Executive synthesis
3. Jobs and desired outcomes
4. Themes and work streams
5. Scope and commitment levels
6. Described solutions and changes
7. Current-state and gap audit, when requested
8. Tensions, assumptions, and non-goals
9. Opportunity backlog
10. Product questions
11. Recommended next slice or sequence

### Small document pack

Use a pack when jobs, current-state evidence, reusable primitives, and delivery
planning each need substantial detail.

Default pack:

- `README.md` — executive synthesis, document map, key decisions, and sequence.
- `01-jobs-and-outcomes.md` — deduplicated end-user, business, and system jobs.
- `02-themes-and-scope.md` — work streams, commitment levels, tensions, and
  cross-cutting decisions.
- `03-opportunity-backlog.md` — adjacent, exploratory, and parked ideas.

Add only when needed:

- `03-current-capability-audit.md` — code-grounded implemented/partial/planned/
  absent matrix; renumber later files.
- `04-core-primitives.md` — reusable domain or platform concepts that several
  jobs depend on.
- `05-delivery-sequence.md` — phased plan, dependencies, decision gates, and
  non-goals.
- `06-reference-scenarios.md` — realistic acceptance walkthroughs and tests.
- one focused file per major theme when the user explicitly requests detailed
  theme/work-stream documents.

Do not create a large document pack merely because the source is long.

## Job entry template

```markdown
### J01 — Outcome-oriented title

**Actor:** [actor]

**When** [situation],  
**I want to** [motivation or progress],  
**so I can** [desired outcome].

**Success looks like**

- [observable outcome or decision]

**Evidence**

- [timestamp, section, turn, or identifying phrase]

**Implications, not commitments**

- [possible behavior or solution]

**Confidence:** Explicit | Inferred
```

Omit fields that genuinely add no value, but keep evidence and the separation
between the job and its proposed solution.

## Theme entry template

```markdown
## Theme: [name]

**Why it matters:** [relationship to jobs and outcomes]

**Related jobs:** J01, J04, B02

**What the transcript describes**

- [behaviors, requirements, and solution ideas]

**Current baseline**

- [grounded evidence, or "Not audited"]

**Tensions and unknowns**

- [tradeoffs, contradictions, assumptions]

**Strongest next move**

- [smallest useful discovery or delivery step]
```

## Scope table

Prefer a compact table when many ideas need classification.

| Idea or capability | Related jobs | Commitment | Current state | Recommended treatment |
| --- | --- | --- | --- | --- |
| [item] | J01, J03 | Decided | Partial | Include in first slice |
| [item] | J08 | Exploratory | Absent | Preserve in backlog |

## Current-capability audit

Use this matrix only after inspecting the product or repository.

| Capability needed by a job | Status | Evidence | Gap or caution |
| --- | --- | --- | --- |
| [capability] | Implemented / Partial / Planned / Absent / Uncertain | [file, behavior, or authoritative doc] | [what remains] |

Do not infer runtime behavior solely from a plan or transcript.

## Product questions

Questions should be decision instruments, not a generic appendix.

For each question:

1. Name the decision and why it matters.
2. Offer two to four concrete options.
3. State the consequence of each option.
4. Give a recommended lean when the evidence supports one.
5. Avoid asking about details that can be decided safely during
   implementation.

Prefer 5–15 questions. Follow an explicit requested count exactly.

## Traceability rules

- Use timestamps when available and trustworthy.
- Otherwise cite a section, speaker turn, paragraph, or short identifying
  phrase.
- Combine multiple locators when several passages support one normalized job.
- Label inferences explicitly.
- Keep quotations short and use them only when exact wording carries product
  meaning.
- Do not pretend the transcript is internally consistent; record conflicts.

## Quality rubric

Score the draft before delivery:

| Dimension | Passing standard |
| --- | --- |
| Coverage | Every major transcript region is represented or intentionally omitted |
| Uniqueness | Overlapping jobs are merged without erasing distinct moments or outcomes |
| Job quality | Primary jobs describe progress, not screens, components, or technologies |
| Separation | Jobs, solutions, constraints, decisions, and speculation are visibly distinct |
| Traceability | Material claims have usable source locators |
| Grounding | Current-state claims have code or authoritative-document evidence |
| Scope clarity | Near-term, exploratory, parked, and non-goal items cannot be confused |
| Actionability | Next steps prove named outcomes and include decision gates |
| Compactness | The artifact set is no larger than the task requires |

Revise any dimension that does not pass.
