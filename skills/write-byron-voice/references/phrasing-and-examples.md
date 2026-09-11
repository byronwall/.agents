# Phrasing and examples

Use these as patterns, not catchphrases to paste repeatedly.

## Observed turns

These are evidence of how Byron moves through a thought, not recommended transitions to insert for flavor.

- `The question is...`
- `So what does that mean?`
- `What would that look like?`
- `One way to do this is...`
- `But then...`
- `The difference is...`
- `At the end of the day...`
- `That works pretty well.`
- `That is probably good enough.`
- `It is a legitimate question whether...`
- `The ideal display depends on...`
- `What this gives you is...`
- `The problem you are about to face...`

Do not stack these mechanically or insert one merely to signal voice. Question-and-answer transitions are useful only when they mark a real turn in the reasoning. Repeated use of these phrases can make an otherwise faithful draft sound generated.

## Transcript-to-prose examples

### Establish the dimensions

Transcript pattern:

> The ideal display really depends on how many rows and columns you have. And once you start looking at rows and columns, it starts to depend on what is the data, data types, data distributions...

Edited pattern:

> The ideal display depends first on the table's shape: how many rows, how many columns, and what kinds of values those columns contain. Those dimensions change which controls are useful and which ones are noise.

Keep the layered dependency. Remove the spoken restart.

### Work backward from usefulness

Transcript pattern:

> Think about what are the true desired end states rather than just being a cool tool that can do all sorts of stuff.

Edited pattern:

> The useful question is not how many things the tool can do. It is which end states people actually want from it.

Keep the practical reframe and plain language.

### Follow the transformation

Transcript pattern:

> We've gone from an object, we've narrowed to a single primitive... but then we take that ID and we fan back out...

Edited pattern:

> The object narrows to a single primitive—an ID—and then fans back out through another lookup. That contraction and expansion is exactly the transformation the visualization should expose.

Keep the spatial metaphor and technical consequence.

### Qualify a recommendation

Transcript pattern:

> It certainly could be done... But now you basically have to use an HTML validation step before you actually save it to the database.

Edited pattern:

> You can make the HTML approach work, but the cost moves into validation. Before saving, you have to parse the document and rebuild enough structure to know that the relationships are still valid.

Do not erase the viable alternative. Name its cost.

### Stop polishing

Transcript pattern:

> Or it could just be that's a boundary not worth crossing. Throw a bunch of tech at it and try to become a different product, and then it's much harder to actually satisfy the needs of that user. Maybe that's good enough.

Edited pattern:

> That may be a boundary not worth crossing. Adding a pile of editing technology turns this into a different product and makes the original user harder to satisfy. Maybe the generated image is good enough as an exploration artifact.

Keep the blunt boundary and the provisional ending. Do not replace them with a balanced survey of future opportunities.

### Retain a direct judgment

Transcript pattern:

> The button about the colors. It's just not working.

Edited pattern:

> The color control is just not working.

Fix the transcription error without diluting the judgment into `could be improved`.

### Keep supported confidence

Transcript pattern:

> Don't lie, don't oversell it, but you are free to only describe the good.

Edited pattern:

> State the contribution plainly when the evidence supports it. Accuracy does not require you to undersell the work.

Keep the boundary between honest confidence and invention. Do not add modest qualifiers merely to make the claim sound safer.

### Change to the reader's viewpoint

Transcript pattern:

> Think about it from their point of view. They just got 300 candidates.

Edited pattern:

> The hiring manager has 300 candidates and several plausible matches. Your resume cannot require them to infer why your experience transfers.

Make the other person's constraint concrete. Do not write the empty instruction `consider the reader`.

### Separate output from value

Transcript pattern:

> From the agent's point of view, it certainly created some stuff.

Edited pattern:

> The agent produced files. That does not show that the result is understandable, useful, or ready to ship.

Preserve the gap between activity and outcome. Do not let a visible artifact serve as its own success criterion.

### State the operational truth

Transcript pattern:

> We need an honest accounting of what works, what does not work.

Edited pattern:

> List what works, what fails, and which limits a customer will hit. A capability matrix is not a roadmap or a promise.

Keep readiness claims testable. Avoid diplomatic wording that makes known failures hard to find.

### Preserve a useful self-correction

Transcript pattern:

> Maybe it's hard only because I'm not actually familiar with the data structures.

Edited pattern:

> The interface may not be inherently complicated. I may be treating it as a black box because I do not know its data structures yet.

Keep the correction when it changes the diagnosis. Remove the spoken circling around it.

## Common over-polishing failures

Avoid drafts where:

- Every section opens with a rhetorical question and closes with a neat answer.
- Each argument becomes a balanced three-item list.
- Every viable alternative receives equal praise despite the source preferring one.
- Blunt language such as `not working`, `a mess`, or `good enough` becomes formal product language.
- The ending restates the opening instead of stopping at the useful boundary.
- Characteristic phrases carry the voice while the underlying reasoning could belong to anyone.
- The draft reports activity but never defines the user's result or the evidence of success.
- A prototype, feature, product, and deployable system are treated as the same level of completion.
- Conflict is polished away until the contract, ownership, or required decision becomes unclear.

## Openings

Prefer:

- A concrete scenario: `You have a table with twenty columns, but only four matter for the current question.`
- A practical tension: `Diagrams are valuable precisely where diagramming tools become painful: mixed structure, nested detail, and constant revision.`
- A target: `The goal is to make intermediate data transformations visible enough that you can count and remove them.`

Avoid carrying `Alright, here we go` into published prose. It is a recording cue, not a defining article voice trait.

## Endings

Prefer:

- A decision rule.
- A smallest useful next step.
- A clearly bounded open question.
- A statement of what the approach buys and what it costs.

Avoid `In conclusion`, a section-by-section recap, or an abrupt transcript sign-off.
