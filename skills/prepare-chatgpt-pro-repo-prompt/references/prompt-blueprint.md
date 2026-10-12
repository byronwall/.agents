# ChatGPT Pro Repository Prompt Blueprint

Use this reference to assemble a detailed prompt. Select only the sections that serve the task. Replace every placeholder before delivery.

The assembled handoff prompt is a Codex artifact. Save it as a new Markdown file in the target repository unless the user explicitly requests otherwise. Do not overwrite an existing file.

## 1. Repository and mission

Start with the canonical repository URL. Put it on its own line.

State:

- the exact repository and target ref;
- the one primary task;
- why the result is needed now;
- the decision or later work that the result must support.

Prefer a decision question over a broad request. For example: “Which API changes reduce consumer work without weakening type safety or increasing the public surface?”

## 2. Role and review posture

Assign a useful expert role. Name the relevant domain, language, framework, or product concern.

Ask for a candid review. Require strengths, weaknesses, tradeoffs, rejected ideas, and uncertainty. Do not ask the model to support a preferred answer.

## 3. Access preflight

Put this before the substantive work.

### GO

Continue only when:

- the exact repository or an explicitly permitted source packet is accessible;
- the owner and repository name match the full URL or packet manifest;
- the required branch, ref, or packet baseline can be identified;
- the required source and documents are available;
- the requested task is possible with the active tools;
- required write capability exists, or the prompt permits a complete read-only output fallback.

Record the inspected branch, ref, or commit when available. If Codex supplies a source packet, identify its baseline and included paths. Use it when the prompt explicitly permits that fallback. State its coverage limits and whether it can run tests.

### NO-GO

Stop and report the blocker when:

- the source belongs to the wrong repository;
- the repository is unavailable and no permitted source packet supplies the required evidence;
- a required private repository is not authorized;
- repository indexing prevents access and no permitted source packet supplies the required evidence;
- required source, data, or prior artifacts are absent from both the repository and any permitted source packet;
- the prompt requires mutation, write capability is absent, and no read-only output fallback is permitted;
- instructions conflict in a way that changes the result;
- a success metric cannot be evaluated;
- work would require guessing a material product decision.

State the smallest action that would unblock the work. Do not claim a complete review from partial access.

## 4. Repository reading route

Give a short, ranked route through the actual repository. Common groups include:

1. `AGENTS.md` and repository rules.
2. README, principles, architecture, and product documents.
3. Package manifests and public entry points.
4. Core implementation and framework adapters.
5. Representative consumers and advanced examples.
6. Tests, fixtures, evaluation tools, and current baselines.
7. Prior research or plans that define the decision context.

Name real files. Say “at minimum” when broader discovery is useful. Tell the model to verify that the prompt's repository facts still match the selected ref.

## 5. Objectives and priority questions

Use one section per major question. For each question, specify:

- what to inspect;
- which users or cases it affects;
- what evidence is required;
- which tradeoffs matter;
- what a useful answer must decide.

Rank the questions. State which question is most important.

For repository reviews, useful lenses can include:

- consumer experience and repeated work;
- correctness and failure behavior;
- public API size and stability;
- implementation complexity;
- type inference and diagnostics;
- runtime behavior and performance;
- inspectability and debugging;
- framework integration;
- example realism and corpus gaps;
- migration and compatibility costs.

Use only relevant lenses.

## 6. Evidence rules

Require the result to:

- cite exact repository paths and symbols;
- use short excerpts only when they improve clarity;
- separate observed facts, inferences, and proposals;
- say when evidence is missing or conflicting;
- distinguish common cases from advanced cases;
- separate product, API, documentation, example, test, and tooling problems;
- explain the cost and benefit of each recommendation;
- reject ideas that do not earn their added complexity.

Do not accept line count or token count as the only quality measure. A shorter design can hide behavior or move complexity into the library.

## 7. Scope and non-goals

List what the model must not do. Typical boundaries include:

- do not implement during a review;
- do not change production files;
- do not redesign unrelated areas;
- do not assume all repeated code is harmful;
- do not weaken types, tests, inspection, or runtime behavior;
- do not add a public helper for one isolated example;
- do not overwrite prior research or evidence;
- do not claim tool actions that were not verified.

Keep these boundaries proportional to the task.

## 8. Recommendation format

For each recommendation, request:

- the problem and affected users;
- repository evidence;
- the proposed change;
- a small before-and-after example when useful;
- impact on correctness, types, runtime, and diagnostics;
- implementation and maintenance cost;
- public API and compatibility impact;
- alternatives considered;
- a confidence level;
- a proof or validation method.

A useful final classification is:

- **Keep** — strong current behavior.
- **Fix now** — high-value, low-regret work.
- **Explore** — a hypothesis that needs a prototype.
- **Avoid** — an attractive idea with excess cost or hidden behavior.
- **Remove or deprecate** — surface that does not justify its cost.

## 9. Evaluation-loop additions

Use this section only for iterative research or optimization.

Define:

- an immutable baseline and exact comparison source;
- objective metrics and non-negotiable invariants;
- a result state such as `better`, `not-better`, or `invalid`;
- cheap rejection checks and full acceptance checks;
- required self-tests for the evaluator;
- rules that prevent deleting behavior or hiding work;
- isolated candidate work and protected user files;
- a bounded experiment count or time budget;
- stop conditions for repeated failures or missing decisions;
- a compact ledger for accepted, rejected, and invalid trials.

Static checks can reject a candidate. They cannot accept one when full evaluation is required.

Commit only accepted work when the user authorized commits. Never commit rejected experiments.

## 10. Deliverable contract

Distinguish the two deliverables:

1. Codex saves this ChatGPT Pro handoff prompt as a new Markdown file.
2. The handoff prompt tells ChatGPT Pro what result to produce.

Name the exact ChatGPT Pro output. Include:

- file type and path when an artifact is required;
- required sections and level of detail;
- whether the document must stand alone;
- required tables, examples, evidence, or appendices;
- what must remain out of the document;
- the final response summary and status evidence.

Require a compact final status. It should list access status, files read, checks run, deliverables, unresolved blockers, and assumptions.

### When Codex will collect the result autonomously

Specify the artifacts needed for local integration. For substantial research, request a report, source list, and recommendations with stable IDs. Add comparison tables, proposed document changes, or a proof plan only when useful.

Ask for downloadable files with clear names. For several files, request a ZIP plus standalone companions and a manifest. Require source citations, explicit unanswered questions, and separation of completed checks from proposed checks.

Ask Pro to link every output in its final response. If file creation is unavailable, require complete content in the response. Codex can then save it locally and record that fallback.

Tell Pro that Codex will review and integrate the results. Keep local Git and PR duties out of Pro's research assignment. Define which missing evidence should cause a targeted follow-up and which open choices can remain for human review.

## 11. Mutation and commit gate

Use only when the user explicitly requests mutation.

Before edits, require:

- a writable checkout, not only the read-only GitHub app;
- the correct branch or explicitly approved branch creation;
- current status and protection of existing changes;
- exact allowed files and forbidden files;
- the repository's package manager and validation commands.

Before a commit, require:

- all task-specific gates to pass;
- inspection of the staged diff;
- only authorized files in the commit;
- the required author and committer identity;
- the exact commit subject or its naming rule;
- verification of the resulting commit and final status.

Treat commit and push as separate permissions. Include them only when covered by the user's request. A full-process request includes Codex's scoped push for the review PR; it does not require Pro to push.

### Read-only fallback

If write capability is absent, return the complete artifact in the response. For code changes, return a patch only when it is useful and complete. State that no repository file, commit, push, or pull request was created.

## 12. Final quality gate

Tell the model not to declare success until:

- every priority question has an evidence-backed answer;
- the GO checks passed;
- no NO-GO condition remains hidden;
- required validation passed;
- the deliverable exists or the fallback is complete;
- mutation evidence matches the requested action;
- final claims do not exceed the available evidence.

When a gate fails, require the result to say `NO-GO`, name the failed gate, show the relevant evidence, and give the next safe action.
