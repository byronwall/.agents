# Website Experience Audit Framework

Use this framework for consistent audits. Adjust category weight to the website's purpose. Do not hide a critical failure inside an average score.

## Evidence types

Label important claims when the distinction matters:

- **Observed:** Direct browser behavior, visible content, screenshot, or measured result.
- **Heuristic:** Expert judgment based on a recognized usability or communication principle.
- **Inferred:** A conclusion about audience, intent, or likely effect that was not stated directly.
- **Untested:** A relevant area that could not be checked.

## Scoring scale

Score each relevant category from 0 to 5.

| Score | Meaning |
| --- | --- |
| 5 | Excellent. Clear, robust, and unusually effective. Only minor refinements remain. |
| 4 | Good. Users should succeed with limited friction. Some meaningful improvements remain. |
| 3 | Adequate. The experience works, but recurring friction or ambiguity reduces quality. |
| 2 | Weak. Important users will struggle, misunderstand, or need recovery. |
| 1 | Severe. The experience frequently blocks understanding or completion. |
| 0 | Failed or absent. The required capability does not work or does not exist. |

Prefer whole-number scores. Use one decimal place only when repeated evidence supports the distinction. Give a short rationale and coverage label beside every score.

Use these coverage labels:

- **High:** Multiple representative journeys or surfaces were tested directly.
- **Medium:** One representative journey or a limited sample was tested directly.
- **Low:** The score relies mainly on partial checks or heuristic inspection.
- **Untested:** No defensible score is available.

A low-confidence score is a hypothesis, not a product measurement.

## Core categories

### Orientation and purpose

- Can a first-time visitor explain what the website is and who it serves?
- Is the starting point clear?
- Does the first screen set accurate expectations?
- Are primary and secondary actions distinct?

### Information architecture

- Do labels match user concepts?
- Are related items grouped together?
- Can users predict where a link leads?
- Do global and local navigation show location and scope?
- Can users recover from a wrong turn?
- Can novices learn and experts retrieve information quickly?

### Content hierarchy and learning flow

- Does each page have one clear purpose?
- Does the sequence match prerequisite knowledge?
- Are summaries, explanations, examples, and references distinct?
- Can users skim without losing the argument?
- Are terms defined before use?
- Are next steps visible at natural stopping points?

### Diagram communication

- Is the question or claim clear before the diagram?
- Is there an obvious entry point and reading order?
- Are labels close to what they describe?
- Are legends, scales, colors, and symbols necessary and clear?
- Does the design reveal relationships instead of adding decoration?
- Does the surrounding text interpret the important conclusion?
- Can users access an equivalent explanation without vision or color perception?

An auditor can assess communication risk and state their own interpretation. Only observed user research can prove comprehension or learning.

### Interactive examples

- Can users discover what is interactive?
- Do instructions state what input changes?
- Does feedback show cause and effect immediately?
- Can users reset, undo, retry, or compare states?
- Do keyboard and touch users receive equivalent access?
- Does the example teach a concept or support a real task?
- Does the result connect to the page's explanation?

### Navigation and wayfinding

- Are active location, breadcrumbs, previous, and next paths useful?
- Do anchors, tables of contents, search, and deep links work as expected?
- Do links preserve context?
- Are there dead ends or circular paths?

### Visual hierarchy and readability

- Do size, weight, spacing, and position reflect importance?
- Are line length, typography, contrast, and density readable?
- Are cards, borders, color, and motion used for meaning?
- Do diagrams and controls fit the surrounding page?

### Interaction quality

- Are targets stable, clear, and large enough?
- Do hover, focus, active, loading, success, and error states exist?
- Is feedback prompt and predictable?
- Are state changes reversible when appropriate?
- Do focus, scrolling, and layout remain stable?

### Accessibility

- Do landmarks, headings, names, labels, and states expose useful semantics?
- Can users complete representative paths with a keyboard?
- Is focus visible and ordered logically?
- Is meaning available without color, hover, fine pointer control, sound, or motion?
- Do zoom, narrow screens, and reduced motion preserve understanding?

### Responsive experience

- Does the content hierarchy survive smaller screens?
- Do diagrams remain legible or offer a useful alternative?
- Do interactive examples remain operable?
- Do navigation, overlays, and sticky controls avoid obstruction?
- Does the site redesign the flow instead of only compressing it?

### Trust and quality

- Are claims supported and sources visible where needed?
- Are terminology, patterns, and behaviors consistent?
- Are broken links, media, errors, or stale content visible?
- Does the interface make system status and limitations clear?

## Severity

| Priority | Meaning |
| --- | --- |
| P0 | Unsafe, destructive, or complete site failure. |
| P1 | Blocks a primary journey or causes a major misunderstanding. |
| P2 | Repeatedly slows users, harms comprehension, or excludes an important group. |
| P3 | Local friction or quality problem with a practical effect. |
| P4 | Refinement with limited effect on outcomes. |

Do not assign priority from visual prominence alone. Use user effect and reach.

## Overall result

Report category scores, then give an overall assessment in words. A weighted average is optional. If used, disclose the weights.

Call out critical weaknesses separately. One P1 problem can outweigh several strong category scores.

## Finding evidence standard

For P0, P1, and P2 findings, capture:

- route or named surface
- viewport and input method
- starting state and required data
- steps to reproduce
- observed result and expected result
- recovery path and whether state or data survived
- screenshot, measurement, or browser evidence
- repeatability: repeatable, intermittent, or observed once

Use focused screenshots. A very tall full-page image is useful for document-length or scroll-position defects. It is usually weak evidence for local state and interaction defects.
