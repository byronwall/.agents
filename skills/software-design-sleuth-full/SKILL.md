---
name: software-design-sleuth
description: Recover intent from messy software or product inputs, then optionally brainstorm contrasting approaches, shape a buildable solution, and create a proof-first implementation plan. Use for transcripts, notes, repositories, prior plans, or iterative dictation when the work must move from “what is actually wanted?” through “what should we build?” to “how can we implement it with fast feedback, isolated dependencies, vertical slices, and low delivery risk?”
compatibility: Designed for Claude Code and portable Agent Skills runtimes with filesystem or repository access. Search, web, issue-tracker, and subagent tools improve results but are optional.
metadata:
  version: "0.4.0"
  category: product-design-planning
  artifacts: intent-brief, brainstorm, shape-brief, implementation-plan, initiative-map
---

# Software Design Sleuth — Intent to Proof

Move an initiative through three connected jobs without turning the user's review artifact into the agent's scratchpad:

1. recover the user's actual intent;
2. shape a coherent and buildable approach;
3. produce a proof-first implementation plan.

An optional brainstorming mode generates a wider set of contrasting approaches before convergence.

The human artifacts must remain concise. Detailed provenance, supersession, dependency analysis, and phase state belong in one machine-readable sidecar.

## Invocation modes

Interpret `$ARGUMENTS` and the current request semantically. Supported modes:

- `intent` — recover and reconcile intent; this is the default when inputs are messy;
- `brainstorm` — generate 6–7 genuinely contrasting approaches from stable intent;
- `shape` — recommend a solution shape and make it easier to build successfully;
- `plan` — create a repository-grounded, proof-first implementation plan;
- `full` — run every safe phase in order until a genuine human, access, or real-world boundary;
- `update` — absorb new dictation, update state, invalidate stale downstream work, and continue;
- `audit` — review existing artifacts for readability, fidelity, buildability, and implementation success.

Do not repeat an earlier phase merely because the skill was reinvoked. Resume from the current state unless new evidence invalidates it.

## Canonical artifact set

Use project conventions when present. Otherwise use:

```text
docs/intent/<initiative-slug>/
├── intent-brief.md
├── initiative-map.json
├── brainstorm.md              # optional
├── shape-brief.md              # after intent is stable
└── implementation-plan.md      # after the shape is stable
```

`initiative-map.json` is the canonical machine state. It stores source anchors, intent claims, revisions, selected shape, implementation dependencies, proof strategy, artifact status, and history.

If `initiative-map.json` is absent but a v0.3 `intent-map.json` exists, migrate it non-destructively with `scripts/migrate-v0.3.mjs`. Preserve the legacy file and mark existing downstream shape/plan artifacts stale until they pass the new gates.

Human artifacts must be understandable without opening the JSON.

## Standing rules

1. **Intent is interpreted, not argued with.** Separate durable goals from examples, rough estimates, implementation ideas, and older superseded statements.
2. **Implementation strategy is challenged.** Once intent is clear, do not merely translate the proposed solution. Recommend a safer, faster, more testable route when one exists.
3. **One point appears once.** Do not repeat the same concern as intent, constraint, risk, scenario, rationale, and milestone.
4. **The method stays backstage.** Human artifacts should not expose evidence ledgers, design-space matrices, generated IDs, scoring dashboards, or source inventories.
5. **Repository reality is not product intent.** Code tells you what exists, what is reusable, and what is expensive. It does not decide what the user wants.
6. **Research cannot silently overwrite intent.** It may challenge a hypothesis or reveal a better implementation path. During shaping and planning, verify current provider, emulator, and platform behavior from primary documentation when it could change the proof strategy.
7. **Ask humans only for human judgments.** Research facts, test observable behavior, and default reversible details. Ask about purpose, priority, audience, policy, appetite, or irreversible direction.
8. **Prefer valid intermediate systems.** Every substantial milestone should leave the system runnable, testable, and understandable.
9. **Prefer a fast local loop.** Live infrastructure should not be the primary development or failure-testing loop when a faithful local seam is practical.
10. **Separate risks instead of bundling them.** Product behavior, application logic, provider protocol, credentials, deployment wiring, and operational resilience are different proofs.
11. **Use the smallest proof that can change the decision.** Do not build a platform to answer a question a reducer, fixture, fake, storyboard, container, or sandbox smoke test can answer.
12. **Keep reversible choices provisional.** Commit only as far as the evidence requires.
13. **Preserve a cut line.** Generalization, polish, speculative infrastructure, and distant failure handling remain below the line until they protect the current proof.
14. **Never mutate production, deploy, migrate data, or publish issues unless explicitly requested.**

## Phase posture

| Phase | Agent posture |
|---|---|
| Intent | Faithful, compressive, careful with examples and corrections |
| Brainstorm | Divergent, contrasting, concise, resistant to first-idea fixation |
| Shape | Constructively skeptical; challenge overbuild and hidden rabbit holes |
| Plan | Opinionated about proof order, local feedback, dependency isolation, rollback, and verification |

## Phase 1 — Recover intent

Load `references/intent-recovery.md` and `templates/intent-brief.md`.

Work unattended through relevant first-party material before asking questions:

1. current request and attachments;
2. direct transcripts, notes, and dictation;
3. accepted decisions and explicit corrections;
4. repository material needed to understand references;
5. external research only when requested or necessary to interpret a term.

Produce or update:

- `intent-brief.md` — concise current interpretation;
- `initiative-map.json` — detailed state and anchors.

Intent brief limits:

- feature: 400–650 words;
- capability: 650–950 words;
- program: 850–1,250 words;
- hard maximum: 1,500 words;
- at most ten major sections, thirty-five bullets, three questions, and one compact comparison table—usually none.

Intent is shape-ready when purpose, audience, desired outcome, strongest boundaries, and current time horizon are clear enough to judge a solution.

## Optional phase — Brainstorm

Load `references/brainstorming.md` and `templates/brainstorm.md`.

Use when the user asks for breadth, alternatives, divergent thinking, or 6–7 options. Do not require it for routine shaping.

Default to seven options unless the user specifies another count. Each option must differ in governing premise, user model, system boundary, or proof strategy—not merely technology or styling.

Across the set, include when relevant:

- a minimal or null approach;
- a reuse-first approach;
- an assumption inversion;
- a different ownership or workflow model;
- a dependency-light or local-first approach;
- an ambitious end-state;
- a synthesis that combines the strongest mechanisms.

Keep each option to roughly 70–140 words. Include only:

- core move;
- what becomes easier;
- main catch;
- best fit.

Do not include source notes, evidence IDs, long scoring tables, or repeated justification. End with a short contrast summary and, only when useful, the agent's current lean.

## Phase 2 — Shape the work

Load `references/shaping.md`, `references/implementation-success.md`, and `templates/shape-brief.md`.

A shape is not merely a proposed interface or architecture. It is a bounded approach that is attractive, fits the appetite, and has a credible proof path.

Before writing the shape brief, construct the strongest materially simpler counterproposal, then run the **implementation success pass** internally:

1. Can the desired outcome be proven with less product or infrastructure?
2. Which assumption is most likely to make the work fail or expand?
3. Which external or difficult dependency can be placed behind one narrow seam?
4. Can core behavior run against a deterministic fake or local substitute?
5. Is an emulator, container, contract test, or sandbox smoke needed for provider fidelity?
6. Can failure states be injected without waiting for real outages?
7. What is the first visible or operator-visible proof?
8. What valid intermediate system exists after each major step?
9. What can be disabled, reverted, or bypassed cleanly?
10. Which generalization should be deferred?

If the user's proposed route is materially worse, say so plainly in the artifact under **How to make this go better**. Preserve the intent while changing the implementation strategy.

The shape brief should normally contain:

1. the problem and desired outcome;
2. appetite and boundaries;
3. one recommended shape;
4. the essential flow or system elements;
5. current system reuse and collisions;
6. **How to make this go better** — 3–6 concrete success moves;
7. rabbit holes and no-gos;
8. first proof;
9. one serious alternative only when it sharpens the decision;
10. at most two remaining human decisions.

Hard maximum: 1,800 words. Do not include a full implementation backlog.

A shape is plan-ready only when the proof path, major seams, cut line, and top implementation risks are clear enough to sequence work.

## Phase 3 — Produce the implementation plan

Load `references/implementation-planning.md`, `references/dependency-ladders.md`, and `templates/implementation-plan.md`.

Inspect enough real code, tests, configuration, deployment files, and recent history to identify actual subsystem names, reusable paths, and missing foundations.

Build the plan around outcomes, not layers. Preserve the strongest rules from the thin-slice approach:

- first prove the smallest high-impact end-to-end behavior;
- map tasks to concrete implementation, configuration, operational, or test work;
- use familiar subsystem names;
- turn unknowns into explicit spikes with decision outputs and fallbacks;
- keep one concise desired-end-state list per milestone;
- draw a clear cut line.

### Dependency proof strategy

For each material external or difficult dependency, first record whether it is absent, locally substituted, or real in the first proof. Then decide which later rungs are necessary:

```text
application core + deterministic fake
    → local emulator or real container
    → shared adapter/contract tests
    → live sandbox smoke
    → deployed operational proof
```

Do not force every rung. Use the lightest set that proves the relevant risks.

The plan should normally separate:

- application behavior from provider integration;
- provider protocol from credentials and permissions;
- credentials and permissions from deployment wiring;
- happy-path integration from retry, outage, idempotency, and recovery;
- local development proof from live cloud confirmation.

When practical:

- define the narrow port or adapter before the provider implementation;
- implement the first behavior against a deterministic local fake;
- make the fake support intentional failures;
- run the same behavioral contract against fake, emulator/container, and real adapter where useful;
- keep live tests few, purposeful, and sandboxed;
- isolate one new external dependency per milestone;
- preserve a switch, feature flag, adapter choice, or fallback during rollout.

### Plan format

The implementation plan should contain:

1. **Plan at a glance** — recommended order and why it improves success likelihood;
2. **Implementation strategy** — seams, local loop, proof ladder, and transition approach;
3. **Outcome milestones** — each with concrete changes, verification, and desired end state;
4. **Cross-cutting verification** only when it cannot live inside milestones;
5. **Below the cut line**;
6. at most three unresolved decisions or spikes.

A first milestone may use a local substitute when that is the fastest way to prove real behavior. It must still produce a visible or operator-visible outcome and leave a clear path to the real dependency.

Do not create horizontal “frontend,” “backend,” “infrastructure,” or “tests” milestones without an independently useful outcome.

## Updates and downstream invalidation

Load `references/feedback-and-invalidation.md`.

The user may dictate corrections naturally. Update the initiative map and rewrite affected human artifacts in place.

- Intent change may invalidate brainstorm, shape, and plan.
- Shape change may invalidate the plan.
- Repository evidence may change implementation strategy without changing intent.
- A resolved reversible detail should not reopen the whole initiative.

Never silently preserve a stale downstream artifact. Mark it stale in JSON, explain the delta briefly, and regenerate it when the current mode permits.

## Autonomous stopping rules

Stop only at one of these boundaries:

- the current human artifact is review-ready and a consequential human judgment remains;
- access, permission, or an unavailable source blocks further progress;
- a real-world observation or external execution is required;
- the requested phase is complete and its gate is satisfied;
- further work is unlikely to change the recommendation or next step;
- the user explicitly limits the run.

Do not stop with a vague request to “review everything.” Name the exact judgment, access, or observation needed.

## End-of-run response

Keep chat shorter than the artifacts:

```markdown
## Produced
- [artifact links]

## My recommendation
[2–5 sentences, including any material pushback]

## What needs you
[0–3 concise judgments or actions]
```

After feedback, return a short delta rather than reposting every artifact.

## Quality gate

Before returning, verify:

- intent is faithful and examples are not promoted into requirements;
- human artifacts meet their budgets and do not expose internal bookkeeping;
- brainstorm options are genuinely independent when brainstorming was requested;
- the shape includes a concrete “make this go better” pass;
- the first proof can change a decision;
- material external dependencies have an explicit seam, first-proof role, and proof strategy;
- the primary development loop is local and fast where practical;
- provider-specific behavior is not trusted solely to mocks;
- every milestone has observable proof and a valid intermediate state;
- unknowns have decision outputs and fallbacks;
- rollback, disablement, or bypass is clear for risky changes;
- below-the-line work is explicit;
- downstream artifacts are not stale.

Run:

```bash
node "${CLAUDE_SKILL_DIR}/scripts/validate-sleuth.mjs" \
  docs/intent/<initiative-slug>
```

Use `scripts/audit-sleuth.mjs` when the user asks for an evaluation or before treating a large plan as execution-ready.

## Supporting resources

- `references/intent-recovery.md` — interpreting unstructured input;
- `references/brainstorming.md` — concise 6–7 option generation;
- `references/shaping.md` — shape brief and phase gate;
- `references/implementation-success.md` — constructive pushback and risk reduction;
- `references/dependency-ladders.md` — mocks, fakes, emulators, containers, contracts, sandboxes, and live proof;
- `references/implementation-planning.md` — thin slices and milestone construction;
- `references/feedback-and-invalidation.md` — dictation updates and stale-artifact handling;
- `references/foundations.md` — research and methodological basis;
- `templates/` — canonical human and machine artifacts;
- `examples/` — expected quality;
- `evals/` — regression prompts and rubric;
- `scripts/` — v0.3 migration, structural validation, and heuristic audit.
