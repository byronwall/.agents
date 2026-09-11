# Shaping after intent

Use this file for `shape`, `full`, or `update` when intent is stable enough to judge a solution.

## Shape objective

A shape answers:

- What problem are we solving now?
- How much work is it worth?
- What is the recommended product and system shape?
- Where does it fit in the current system?
- What is most likely to make it fail or expand?
- What is the cheapest meaningful proof?
- What is deliberately out of scope?

It is not a detailed design document or implementation backlog.

## Shape sequence

1. Restate the problem without embedding the implementation.
2. Set an appetite or at least a relative size boundary.
3. Inspect the current system only enough to identify reusable paths and collisions.
4. Sketch the essential places, actions, data movement, and boundaries.
5. Construct and test the strongest dependency-light or smaller counterproposal.
6. Run the implementation-success challenge.
7. Amend the shape to remove or isolate rabbit holes.
8. Choose the first proof.
9. Write the concise shape brief.

## Recommended shape standard

The selected shape should include:

- one coherent user or operator flow;
- the minimum system elements required;
- a clear source of truth or ownership model when state matters;
- the seam to current behavior;
- a valid intermediate state;
- a disable, bypass, or rollback path;
- a first proof that can invalidate the recommendation.

## “How to make this go better”

This section is mandatory for capability and program work and for any feature with a material external dependency.

Use 3–6 plain-language recommendations. Examples:

- Put the provider behind a small interface so the core behavior is testable without the cloud.
- Prove read/write and failure semantics locally before adding IAM and deployment wiring.
- Keep the old path available until the new path has a live sandbox smoke test.
- Build one representative end-to-end flow before generalizing to all config types.
- Reuse the existing lifecycle rather than introducing a second source of truth.

Do not hide these recommendations in a risk register.

## Rabbit-hole categories

Look specifically for:

- uncertain third-party behavior;
- missing local development path;
- unclear state ownership;
- migration or compatibility;
- permissions and security;
- retries, idempotency, and partial failure;
- slow feedback caused by deployment-only testing;
- broad generalization before one representative path works;
- several new dependencies introduced together;
- UX that depends on an unproven backend model.

## Shape gate

Do not proceed to a detailed plan when:

- the intended outcome is still contested;
- the recommended shape has no credible first proof;
- a provider or migration risk has no isolation seam;
- the first usable intermediate state is unknown;
- the shape exceeds the appetite with no meaningful cut;
- a human policy or product decision materially changes the architecture.

Create a focused spike or ask one high-leverage question instead.
