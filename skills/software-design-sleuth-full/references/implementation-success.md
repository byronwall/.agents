# Implementation success challenge

This is the skill's constructive-pushback engine. Use it during shaping and again before finalizing the implementation plan.

## Core stance

The user's intent is authoritative. The proposed implementation is not.

When a different route materially improves testability, feedback speed, reversibility, or delivery probability, recommend it explicitly.

Do not add complexity merely because it is architecturally elegant. Every success move must reduce a named risk, shorten a feedback loop, or create a useful intermediate state.

## Internal counterproposal pass

Before accepting the obvious implementation route, construct the strongest materially simpler counterproposal. Attempt, in order:

1. omit the new dependency from the first proof;
2. isolate it behind one application-owned seam;
3. substitute a deterministic local implementation for routine work;
4. add the real dependency only for the property that requires it;
5. stage authority and rollout rather than cutting over immediately.

Reject the counterproposal only with a concrete reason. Do not expose this internal comparison unless it materially changes the recommendation.

## The nine leverage questions

1. **Smaller proof:** What is the least we can build that would change our confidence?
2. **Fast loop:** Can the core behavior be run and debugged locally without deployment or shared infrastructure?
3. **Narrow seam:** Can one interface isolate the external, legacy, or unstable dependency?
4. **Failure control:** Can we intentionally trigger missing data, timeouts, retries, conflicts, permission failures, and malformed responses?
5. **Fidelity ladder:** Which behavior requires a fake, emulator/container, contract test, sandbox, or deployed smoke?
6. **Independent risk:** Are product behavior, data model, provider integration, credentials, and rollout bundled together unnecessarily?
7. **Valid intermediate:** What useful state exists after the first and second milestones?
8. **Reversibility:** How can we disable, bypass, fall back, or migrate incrementally?
9. **Operational proof:** What logging, metrics, or diagnostics make the first real integration understandable?

## Success moves

Prefer moves such as:

- dependency inversion at the actual domain boundary;
- deterministic fakes with controllable failure modes;
- local emulators or real containers for protocol fidelity;
- shared adapter contract tests;
- one live sandbox smoke test instead of a live-only suite;
- feature flags or adapter selection for rollout;
- shadow reads, compare-only modes, or dual execution without dual authority;
- a single representative entity, workflow, or configuration type;
- migration by slice rather than big-bang replacement;
- fixtures and seed commands that make the path reproducible;
- one command that starts dependencies and runs the focused test;
- observability added with the first real integration, not as final polish.

## Anti-patterns to challenge

- “Build all infrastructure, then add behavior.”
- “Deploy to find out whether the code works.”
- “Mock every SDK call and assume the provider will match.”
- “Use the live cloud for routine failure testing.”
- “Introduce two providers, a migration, and a new domain model in one slice.”
- “Create a general framework before one concrete use case works.”
- “Hide a product or architecture decision inside an implementation task.”
- “Add a fallback that has never been exercised.”
- “Make the new path authoritative before it is observable.”

## Pushback format

Keep pushback concise and actionable:

```markdown
## How to make this go better

- **Separate core behavior from AWS.** Define a small configuration-store boundary and prove application behavior against a deterministic local implementation first.
- **Use two integration proofs, not one giant cloud test.** Run provider semantics against LocalStack or another faithful emulator, then keep a small sandbox smoke test for IAM and AWS-specific behavior.
- **Add one provider at a time.** Prove Parameter Store reads and writes before adding Secrets Manager rotation or fallback behavior.
```

Explain the benefit, not the methodology name.
