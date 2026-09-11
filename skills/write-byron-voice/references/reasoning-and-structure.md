# Reasoning and structure

## Default reasoning arc

Use this as a flexible pattern, not a mandatory template:

1. Name the practical object and desired result.
2. Identify the dimensions that change the answer.
3. Walk through one or more realistic cases.
4. Follow the data, state, or user action through the system.
5. Ask what breaks, becomes hidden, or grows expensive.
6. Compare an alternative and state what it buys.
7. Locate exceptions, scale boundaries, and unknowns.
8. Finish with the useful default or the next experiment.

Use only the moves the material needs. Do not make every article perform the complete arc, give equal space to every alternative, or end with a recommendation when the honest result is an open question. Preserve structural asymmetry when it reflects the evidence.

## Characteristic moves

### Start from the end state

Ask what output would make the tool or feature genuinely valuable. This often reveals that a technically interesting capability is not the product goal.

### Decompose by dimensions

Split broad questions by the variables that matter: row count, column count, data type, schema knowledge, viewport, persistence, user intent, or whether the system handles one item or many.

### Follow a concrete path

Trace what happens from database to application state to component to mutation, or from a user gesture to its stored result. Use this to expose extra transformations and hidden boundaries.

### Turn features into consequences

Do not stop at `add filtering` or `support saved views`. Ask how the control appears, how the user knows it is active, what state is persisted, how it is shared, and where the approach fails.

### Reframe the question

Move from a surface binary to the more useful distinction. Examples from the corpus include:

- Not merely dates versus timestamps, but which time aggregation matches the task.
- Not merely rendering a diagram, but combining topology, sequence, hierarchy, and editable layout.
- Not merely whether an agent completed a run, but what independent artifacts show about the run.
- Not merely whether data can be stored as HTML, but what type and relationship visibility is lost at that boundary.

### Test the alternative

Use counterfactuals: `What would it look like if...` or `Could the server have sent...` Follow the alternative far enough to show its cost, not just its appeal.

### Test the smallest complete path

Reduce the idea to the simplest end-to-end user flow or working example. Inspect the result before adding scope. Ask why that version is not good enough, then use the observed gap to decide what comes next.

### Keep evidence and status distinct

Separate what the source proves from what Byron infers. In exploratory material, also separate possible options, the current choice, the experiment being run, and work that is already complete.

### Change viewpoints

Test the claim from the position of the affected person. Ask what the user sees, what the reviewer can verify, what the maintainer inherits, or what another team reasonably owns. Use a specific situation instead of a generic appeal to empathy.

### Expose the choices

Name decisions hidden inside a broad request. Show which choices constrain later choices, which can wait, and which the source has already made. This is especially important when writing about agent work because an agent will fill an unspecified gap.

### Audit the boundary

Trace the handoff between components, representations, teams, or products. State the expected contract, the observed deviation, who owns the next action, and what breaks downstream. Do not blur responsibility merely to make the account sound diplomatic.

### Separate capability from readiness

Distinguish something that can be built from something that works. Then ask whether it is useful, reliable, deployable, and worth maintaining. A demo can prove a mechanism without proving the product.

### Let evidence shape the structure

Give detail in proportion to evidence and consequence. Do not divide space evenly across options. A weak or high-risk part may need most of the article, while familiar parts need one sentence.

### Revise the model in public

Keep a meaningful self-correction when it changes the conclusion. State the first model, the observation that broke it, and the better model. Remove false starts that do not change the reasoning.

### Keep recommendations conditional

Use defaults tied to context: `for most known-schema applications`, `once the table has twenty columns`, `if the user needs to share the view`. Avoid `always` and `never` unless the source states and supports them.

## Article structures

Select the lightest structure that fits the genre. These are defaults, not required section outlines.

### Design or product exploration

- Desired user outcome.
- Relevant scale or data-shape dimensions.
- Control and display options.
- Visibility and persistence requirements.
- Progressive disclosure.
- Recommended default and advanced escape hatch.

### Architecture or static-analysis article

- Concrete data-flow example.
- Intermediate representations or transformations.
- Where information becomes hidden or duplicated.
- Alternative representation.
- What the alternative buys in validation, inspection, or change safety.
- Visual or measurable signal that could expose the problem.

### Tool retrospective or proposal

- What the tool currently does.
- Actual desired outputs.
- Gaps between capability and usefulness.
- Quality, deployment, workflow, and business constraints.
- Smallest next step that can prove value.

### Project update

- What changed or now works.
- The concrete problem that made the change necessary.
- What the implementation or result revealed.
- What remains rough, uncertain, or worth doing next.

Do not turn a project update into a grand lesson unless the evidence supports one.

### Retrospective

- Original expectation or working model.
- What actually happened.
- The observation that changed the model.
- The revised default and its remaining boundary.

### Evidence-backed advice

- The real situation and desired result.
- The constraint that shaped Byron's choice.
- What happened when he used that approach.
- The reader's version of the same decision.
- The default, its exception, and any missing evidence.

Do not turn one experience into a universal rule. Do not weaken a supported lesson into generic encouragement.

### System or team critique

- The expected contract or division of responsibility.
- The observed behavior and direct evidence.
- The downstream effect on users, customers, or other teams.
- What remains uncertain or contested.
- The concrete action or decision now required.

Keep technical facts separate from frustration. Preserve the frustration only when it explains the stakes or the needed action.

### Short explanation

- Answer the practical question directly.
- Give the smallest concrete example needed to make the distinction clear.
- Stop when the reader has a useful decision rule.

Do not manufacture an exploratory journey for material that only needs a direct answer.

### Short message, email, bio, or caption

- State the purpose or useful point immediately.
- Include only supported personal context.
- Match the relationship and level of formality in the source material.
- Keep the natural directness; do not inflate a short note into an essay.
- End with the requested action, relevant boundary, or clean stopping point.

## Editing heuristic

For each paragraph, identify its job: scenario, distinction, consequence, alternative, qualification, or recommendation. Merge or remove paragraphs with no distinct job. If a passage lists features, add the decision criterion connecting them. If it states an opinion, add the concrete observation that earned it. Do not make paragraph jobs mechanically alternate or force similar lengths; the reasoning should determine the shape.
