---
name: diagram-led-technical-brief
description: Create, review, and revise concise standalone Graphviz technical diagrams and diagram-led briefs from loose notes, transcripts, architecture discussions, implementation findings, or existing visuals. Use for system boundaries, dependencies, lifecycles, architecture, before-and-after comparisons, implementer handoffs, and technical graphics that need embedded titles, subtitles, legends, clear reading paths, or polished DOT/PNG output.
---

# Diagram-Led Technical Brief

Build the smallest diagram that gives the viewer the correct mental model, then let prose explain consequences, evidence, asks, and unresolved details.

Default to a finished Graphviz artifact, not an inline diagram language. Every rendered image should remain understandable when copied, clipped, or pasted without its surrounding document.

Treat visual design as information design. Optimize in this order:

1. message;
2. structure and reading path;
3. relationships and hierarchy;
4. legibility and consistency;
5. polish.

A polished diagram that communicates poorly is unsuccessful.

## Operating modes

Choose the mode that matches the request:

- **Create:** derive a diagram and brief from source material.
- **Review:** diagnose an existing visual without changing it.
- **Revise:** review first, then restructure and render an improved version.
- **Compare:** assess an original and revision against the intended understanding, not visual novelty.

For review or revision, use the same workflow as creation. Decode the existing visual before criticizing or restyling it. Do not merely recreate it more neatly.

## Default artifact contract

Unless the user explicitly asks for another format:

- author final diagrams in Graphviz DOT; do not use Mermaid;
- preserve each editable `.dot` source beside its rendered `.png` or `.svg`;
- render document-ready PNGs at 180 DPI and inspect the actual images;
- make every image standalone with an embedded practical title, one-line subtitle, and compact legend when color or shape carries meaning;
- place true before/after states in one side-by-side image with aligned panels and shared visual grammar, not in separate images;
- keep the diagram concise enough to scan at first glance; standalone framing is context, not a second prose document inside the image.

Treat the rendered image as an independently shareable artifact. A viewer should not need the filename, section heading, surrounding paragraph, or spoken narration to identify the process, understand the takeaway, and decode any meaningful color.

## Workflow

### 1. State the intended understanding

Complete this sentence before choosing a layout:

> The viewer should understand that ______.

Also identify:

- audience and expected viewing context;
- supporting messages;
- what the viewer should know within five seconds;
- the final decision, consequence, or ask.

If the sentence has multiple independent answers, use multiple coordinated views. If the intended message is uncertain, mark that as a first-order issue rather than inventing coherence.

### 2. Extract or decode the working model

From source material, identify:

- actors, systems, stores, representations, and external boundaries;
- authoritative state and derived or installed state;
- direction of data, control, translation, persistence, and feedback;
- failure points, stale states, ownership seams, and coordination asks;
- facts, inferences, and open questions;
- essential, supporting, and incidental information.

For an existing visual, also decode its visual grammar:

- what boxes, arrows, colors, shapes, groups, and spatial positions mean;
- where the viewer should begin, move next, and finish;
- which distinctions are intentional and which may be accidental.

Prefer nouns and verbs already used by implementers. Do not smooth over an uncertain boundary merely to make the picture tidy.

### 3. Choose the question, form, and number of views

Create views for questions, not one canonical picture of the entire system. Show important behavior rather than inventories.

| Need | Prefer |
|---|---|
| Simple linear explanation or field comparison | Prose or table |
| Sequence or transformation | Flow or pipeline |
| Interactions over time | Sequence diagram |
| Hierarchy | Tree |
| System or trust boundaries | Architecture/container diagram |
| States and transitions | State diagram |
| Dependencies | Dependency graph |
| Alternatives or before/after states | One side-by-side comparison image |
| Physical arrangement | Spatial schematic |
| One dominant concept | Annotated illustration |
| Substantial complexity | Overview plus focused detail views |

Use Graphviz DOT by default because:

- portrait or page-width composition matters;
- ranks, hierarchy, parallel branches, feedback loops, or cross-links need control;
- state, execution, persistence, risk, or outcomes require distinct treatment;
- predictable PNG or SVG rendering matters;
- iterative control over spacing, constraints, and grouping materially improves comprehension.

Do not introduce Mermaid as an intermediate or final artifact unless the user explicitly requests it. Sketch directly in DOT and revise the DOT source after rendering.

Use a manual diagramming tool when spatial storytelling, annotation, or presentation polish matters more than source-controlled generation.

### 4. Build structure before styling

Lay out major regions before individual nodes. Choose one dominant reading direction and make the primary narrative visually strongest.

Verify:

- every arrow has a clear verb or obvious direction;
- data and control are distinguishable when both appear;
- authoritative and derived states are distinct;
- semantic, process, machine, network, trust, account, region, deployment, and persistence boundaries are labeled only when relevant;
- proximity and whitespace do grouping work before containers and borders;
- loops represent real lifecycle behavior rather than decorative symmetry;
- risks attach to the operation that creates them;
- secondary relationships recede;
- the flow lands on the intended decision, consequence, or ask.

Keep labels concise, specific, and grammatically parallel. Separate identity, important annotation, and detailed explanation rather than placing paragraphs inside nodes. Use annotations to explain why, an unusual edge, a transformation, an exception, or a concrete example—not to narrate obvious geometry.

Give every rendered image enough framing to stand alone:

- **Title:** name the actual process, dependency, lifecycle, or comparison—not the document section or generic form. Prefer “Client model switch: before vs. after” over “Five-second view.”
- **Subtitle:** state the practical change or takeaway in one sentence fragment. It should clarify why the flow matters without repeating the title.
- **Legend:** embed a compact legend when color, border, line style, or shape encodes meaning. Name the semantics directly, such as “Green: behavior added by this PR.” Omit the legend when labels and geometry already explain everything.
- **Identity:** include a PR, project, system, or feature identifier only when it helps a detached image retain context.

Place title and subtitle at the top. Prefer a quiet legend at the bottom so it does not compete with the reading path. Keep all helper text visibly secondary to the diagram.

For before/after work, use one landscape canvas with two clearly labeled panels:

- align comparable entry points and outcomes;
- use the same terminology, colors, shapes, and scale in both panels;
- show the changed behavior, not merely two inventories;
- reserve red or risk treatment for the problematic outcome and green or success treatment for the corrected outcome;
- add one shared legend for the entire image;
- do not make the viewer compare separate files or scroll between images.

### 5. Control complexity

Do not solve density by shrinking everything. Instead remove, group, collapse, sequence, layer, or split.

For complex material, prefer coordinated views:

1. **Orientation:** major actors, boundaries, and primary flow.
2. **Mechanism:** the interaction, relevant components, and important data or control movement.
3. **Detail:** failures, edge cases, protocols, and implementation specifics.

Watch for these failure patterns:

- **Box soup:** similar boxes and arrows with no clear regions or start.
- **Container Russian dolls:** nested panels whose borders carry little meaning.
- **Spaghetti arrows:** crossings, long jumps, backtracking, or ambiguous junctions.
- **Everything is important:** equal visual weight across primary, secondary, and contextual material.
- **Database dump:** every component and edge shown regardless of the question.
- **Legend tax:** viewers repeatedly leave the flow to decode a large legend.
- **Label avalanche:** paragraphs, repeated qualifiers, and tiny metadata.
- **Accidental rainbow:** colors without stable semantic roles.
- **False symmetry:** equal space or emphasis without equal importance.
- **Premature polish:** styling changes applied while structure remains confusing.

When one appears, repair the underlying message, grouping, ordering, relationship, or view boundary before styling it.

### 6. Shape DOT for the destination

For documents, prefer `rankdir=TB` and a portrait canvas. Start from [assets/portrait-system-boundary.dot](assets/portrait-system-boundary.dot) when its shape is useful. For a before/after comparison, start from [assets/side-by-side-comparison.dot](assets/side-by-side-comparison.dot).

Use these techniques deliberately:

- Set `size` near the printable content area, such as `7.0,9.2!`.
- Use a graph-level HTML label for the embedded title and subtitle; keep title around 18–19 pt and subtitle around 10–11 pt.
- Use `rank=same` for true peer nodes, not superficial balance.
- Use `newrank=true` when cross-cluster alignment is necessary in a side-by-side comparison; render immediately because cross-cluster rank constraints can destabilize layout.
- Use `constraint=false` for feedback or pull-back edges that should not distort the main hierarchy.
- Keep node labels to one or two short lines.
- Prefer dedicated annotation or risk nodes over labels on orthogonal edges; Graphviz does not place orthogonal edge labels reliably.
- Let the main success path follow the dominant reading direction. Route risks and feedback around it.
- Avoid overconstraining the graph. Add ranks or constraints only to fix a specific readability problem.
- Use logos only as optional recognition aids; shape should communicate conceptual role and the label should provide identity.

Treat color as an encoding system:

- Start with neutrals plus two or three chromatic families when enough.
- Reuse shades within a family for hierarchy, grouping, selection, or intensity before adding another hue.
- Draw colors from an established application or organization language when one exists; otherwise choose a coherent accessible palette.
- Encode stable categories, not arbitrary node identity or sequence.
- Reserve strong saturation and contrast for emphasis; use quiet tints for large regions.
- Keep meanings consistent throughout the diagram.
- Explain recurring color roles in an embedded legend, preferably a `shape=plain` HTML table at the bottom of the graph.
- Pair color with labels, shape, border, grouping, or position so it is never the only carrier of meaning.
- Verify text contrast, grayscale differentiation, and common color-vision deficiencies.

The starter DOT palette is an example, not a contract.

### 7. Render, inspect, and revise

Check for Graphviz:

```bash
command -v dot
```

Render a document-ready PNG:

```bash
dot -Tpng -Gdpi=180 diagram.dot -o diagram.png
```

Render SVG when downstream editing or infinite scaling matters:

```bash
dot -Tsvg diagram.dot -o diagram.svg
```

Inspect the actual image at its expected display size and original detail. Iterate on source rather than resizing a bad layout into submission.

Apply these tests:

- **Five-second test:** a new viewer can identify the subject, major regions, starting point, and dominant flow.
- **Detach test:** after hiding the surrounding document, the image title, subtitle, and legend still provide enough context to understand what changed and why it matters.
- **Comparison test:** before/after states share one canvas, align comparable points, and can be contrasted without scrolling or remembering another image.
- **Compression test:** the one-sentence message, three-bullet summary, and visual flow agree.
- **Squint test:** major regions, hierarchy, and primary flow remain visible at low detail.
- **Line-trace test:** a major flow can be followed without excessive crossings, direction changes, long jumps, ambiguous junctions, or backtracking.
- **Geography test:** adjacency, hierarchy, distance, isolation, and centrality imply the intended meaning.
- **Remove-one-layer test:** removing containers, icons, annotations, secondary arrows, fills, metadata, or other chrome would not strengthen the message.

Also check that nothing is clipped, labels are readable, arrows imply the correct direction, whitespace is intentional, feedback does not dominate the primary path, helper text remains secondary, and the legend does not shrink the actual flow below normal reading size.

### 8. Build the brief around the diagram

Use the lightest structure that fits:

1. title stating the practical dependency or problem;
2. one short framing paragraph;
3. the lead diagram;
4. concrete support needs, decisions, or consequences;
5. implementer-facing evidence and detail;
6. immediate next steps.

For two audiences, put the orienting diagram-led brief first and the implementer reference below it. Do not make every implementation detail simultaneously visible. The first section should orient; the second should supply evidence, contracts, scenarios, and failure semantics.

When producing DOCX or Google Docs output, use the document skill for structured generation and render every page before upload. Keep editable diagram source and rendered images beside the source brief.

## Review and revision protocol

When reviewing, prioritize a small number of consequential findings:

- **P0 — Comprehension failure:** unclear message, wrong form, missing concepts, ambiguous relationships, no reading path, or unparseable density.
- **P1 — Structural improvement:** regrouping, reordering, reducing nesting, shortening connections, splitting views, simplifying labels, or establishing visual grammar.
- **P2 — Polish:** spacing, dimensions, typography, borders, color tuning, arrowheads, and corner treatment.

Never let P2 distract from P0. For each important finding, state:

1. **Problem:** the observable issue.
2. **Why it matters:** the incorrect inference or cognitive cost it creates.
3. **Change:** a concrete structural or visual revision.

Use this compact review output:

1. **Intended message:** one sentence, with uncertainty marked.
2. **Overall assessment:** strongest choice and biggest comprehension problem.
3. **What works:** specific choices worth preserving.
4. **Highest-impact changes:** roughly three to seven P0/P1/P2 findings in priority order.
5. **Recommended structure:** regions, reading direction, grouping, relative placement, and primary connection path; include an ASCII wireframe when useful.
6. **Simplifications:** what to remove, combine, rename, demote, annotate, or move to another view.
7. **Polish pass:** only after structural recommendations.

Score only when comparison or calibration benefits from it. Use 0–10 and weight comprehension over aesthetics:

| Category | Weight |
|---|---:|
| Message clarity | 20% |
| Reading path | 15% |
| Layout/composition | 15% |
| Hierarchy | 10% |
| Relationship clarity | 10% |
| Grouping/structure | 10% |
| Cognitive load | 10% |
| Legibility/accessibility | 5% |
| Consistency | 3% |
| Visual polish | 2% |

Do not mechanically discuss every category when it adds no value. A beautiful graphic cannot score highly if comprehension is poor.

When comparing a revision with its source, ask whether the message is clearer, the reading path is shorter, relationships are easier to trace, clutter is genuinely reduced, and useful information remains. Do not assume cleaner means better; check whether simplification introduced ambiguity.

## Quality gate

Do not call the artifact done until:

- the main message can be stated in one sentence;
- a new viewer knows where to begin and can identify the dominant path;
- major regions are visible before every label is read;
- the diagram can be understood without narration;
- the image still makes sense when copied out of the document;
- the image contains a practical title and concise subtitle;
- any meaningful color, border, shape, or line encoding is explained by an embedded compact legend;
- every true before/after comparison appears on one aligned canvas;
- the prose remains useful if the image is inaccessible;
- related elements are grouped and equivalent concepts share treatment;
- every important relationship has understandable semantics;
- primary and secondary information have different visual weight;
- no important relationship requires unnecessary visual detective work;
- terms match the implementation and unsupported certainty is marked;
- labels remain readable at the expected display size;
- color distinctions are intentional and nonessential to comprehension;
- the visual fits its destination at normal zoom;
- DOT source is preserved with the rendered asset;
- the final document has been rendered and visually inspected.

When choosing between two revisions, prefer the one that reduces interpretation while preserving the information necessary to construct the correct mental model.
