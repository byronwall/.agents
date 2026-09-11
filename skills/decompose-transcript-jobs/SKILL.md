---
name: decompose-transcript-jobs
description: Decompose long transcripts, dictations, voice-memo exports, brainstorming notes, and exploratory conversations into traceable jobs to be done, themes, product scope, decisions, open questions, opportunity backlogs, capability gaps, and implementation-ready planning artifacts. Use when Codex is asked to process a large transcript or memo; capture unique jobs or desired outcomes; group ideas into themes or work streams; separate committed changes from speculative ideas; map transcript goals to an existing product or repository; preserve side ideas without bloating the immediate plan; or turn loosely ordered commentary into a consistent Markdown document set.
---

# Decompose Transcript Jobs

Turn exploratory speech into a stable product model without confusing proposed
solutions with the progress people want to make. Preserve traceability to the
source and clearly distinguish what is known, inferred, decided, and merely
imagined.

## Load the output contract

Read [references/output-contract.md](references/output-contract.md) before
writing deliverables. Use its canonical finding fields, artifact-selection
rules, templates, and quality rubric.

## 1. Establish the assignment

Identify:

- the transcript or memo sources;
- the product, repository, or domain in scope;
- whether the user wants synthesis, product discovery, a current-state audit,
  an implementation plan, or some combination;
- explicit output constraints such as one document, new files only, named
  sections, or a requested question count.

Honor an explicit artifact shape. Otherwise choose the smallest document pack
that keeps jobs, scope, evidence, and next steps understandable.

When the work concerns an existing repository:

1. Read its `AGENTS.md`.
2. Inspect git status before changing files.
3. Read the product intent, README, current plans, and relevant code before
   claiming that a capability exists or is absent.
4. Preserve unrelated user changes.

Treat transcript synthesis as documentation work. Do not implement product
changes unless the user asks for implementation.

## 2. Build an evidence ledger

Read the entire source before settling the taxonomy. Process it in logical
chunks if necessary, but maintain one cumulative ledger.

Record each material statement as one or more typed findings:

- end-user job;
- product or business job;
- supporting system job;
- desired outcome or success measure;
- pain or failure;
- requirement or constraint;
- explicit decision;
- proposed solution or interaction;
- current-state claim;
- question or ambiguity;
- speculation or parked idea.

Attach the best available locator: timestamp, speaker turn, heading, paragraph,
or a short identifying phrase. Do not fabricate precise timestamps. Mark each
finding as explicit or inferred and assign its commitment level.

Use short evidence excerpts only when wording matters. Prefer paraphrase plus a
locator.

## 3. Normalize jobs at the outcome level

Write user jobs in this form when it fits naturally:

> When [situation], I want to [motivation/progress], so I can [outcome].

Use descriptive outcome statements when the formula becomes awkward. Keep the
actor explicit.

Apply these tests:

- A job survives a change in interface or technology.
- A solution describes one way to serve a job.
- A requirement constrains the solution.
- A system job is work the product must perform to serve another actor's job.
- A business job describes progress sought by the operator or organization.

Merge statements that share actor, situation, motivation, and outcome. Keep
separate jobs when their success criteria or moments of use differ. Preserve
multiple evidence locators on merged jobs.

For every primary job, include:

- actor and job statement;
- desired outcome or success signal;
- evidence locators;
- implications or solution ideas, clearly labeled as such;
- confidence or uncertainty when the job is inferred.

Do not inflate a feature list into dozens of fake jobs.

## 4. Derive themes and work streams independently

Group the ledger into themes based on product responsibility, workflow, actor,
or decision boundary—not the transcript's chronology.

For each theme, state:

- why it matters;
- related jobs;
- described product behavior;
- current baseline, if grounded;
- unresolved tensions;
- strongest next move.

Allow one job to support several themes, but choose one canonical home for each
detailed discussion and cross-link rather than duplicating it.

## 5. Separate commitment from imagination

Classify scope using these stable levels:

1. **Current baseline** — verified existing behavior or an explicit current
   constraint.
2. **Decided direction** — the speaker clearly commits to an outcome or
   boundary.
3. **Near-term candidate** — directly described and plausibly next, but not
   committed.
4. **Exploratory branch** — a larger or alternative product bet.
5. **Parked or cautioned idea** — preserved intentionally without implying
   near-term scope.

Also surface:

- contradictions and product tensions;
- assumptions disguised as requirements;
- non-goals;
- ideas that belong to another product or repository;
- dependencies among work streams.

Never silently convert enthusiasm, repetition, or implementation detail into a
product decision.

## 6. Ground current-state and gap claims

Only claim “exists,” “works this way,” “missing,” or “partially supported” after
checking the relevant code or authoritative documentation.

Use these capability labels:

- implemented;
- partial or proxy;
- planned only;
- absent;
- uncertain because evidence is incomplete.

Tie each label to concrete evidence. Distinguish the transcript's mental model
from the repository's actual behavior. If the task does not authorize or
require a repository audit, omit the gap audit instead of guessing.

## 7. Convert discovery into action

Choose next steps that advance the jobs rather than merely implementing every
mentioned feature.

When planning is requested:

- identify the smallest coherent vertical slice;
- define the primary user outcome it proves;
- list required capabilities or primitives;
- preserve adjacent ideas in a backlog;
- state non-goals and decision gates;
- provide acceptance criteria grounded in a realistic scenario;
- separate discovery documents from executable implementation plans.

Ask product questions only when answers materially alter audience, workflow,
scope, data model, trust boundary, or delivery sequence. Do not ask questions
already answered by the transcript. Give concrete options, implications, and a
recommended lean when useful.

## 8. Verify completeness and consistency

Before delivery:

1. Re-scan the transcript by chunk or section and map every major passage to a
   finding, intentional omission, or duplicate.
2. Confirm each primary job is outcome-level and unique.
3. Confirm solutions, requirements, decisions, and speculation are separated.
4. Confirm current-state claims have repository evidence.
5. Confirm side ideas are preserved without contaminating immediate scope.
6. Confirm the artifact pack follows the output contract.
7. Validate links and run formatting checks appropriate to the repository.

Report the major synthesis decisions, artifact paths, and any meaningful
uncertainty. Do not imply that documentation-only work verified runtime
behavior.
