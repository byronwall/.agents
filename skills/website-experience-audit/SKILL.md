---
name: website-experience-audit
description: Audit a running website through realistic browser use, with special depth for information architecture, explanatory content, diagrams, interactive examples, accessibility, responsive behavior, and visual quality. Use when Codex must inspect a URL and produce an evidence-based usability report and prioritized improvement backlog. Do not use for a source-only code review or when the main request is to implement a redesign.
---

# Website Experience Audit

## Purpose

Evaluate whether a website helps its intended audience orient, understand, explore, and act. Inspect the live experience as a user would. Do not reduce the audit to visual taste or automated checks.

The default result is a report. Do not edit the website unless the user also asks for implementation.

## Required context

Collect or infer:

- target URL and any important routes
- intended audience and their likely prior knowledge
- the website's purpose and primary outcomes
- important diagrams, demonstrations, or interactive examples
- viewport, authentication, and data constraints
- allowed actions and areas that must stay read-only

If the user supplies only a URL, infer a competent first-time visitor. State the inferred audience and purpose in the report. Ask only when access or risk prevents safe inspection.

## Required references

Before a deep audit, read:

- [references/audit-framework.md](references/audit-framework.md) for evaluation criteria and scoring anchors
- [references/report-template.md](references/report-template.md) for evidence and report structure

For a quick audit, use the same categories but reduce route coverage and report depth.

## Operating rules

- Use an available browser control tool to inspect the rendered website.
- Prefer visible controls and ordinary navigation.
- Do not inspect source code unless the user requests a combined product and implementation audit.
- Do not use hidden controls, direct DOM mutation, internal APIs, or guessed routes to overcome usability problems.
- Treat difficulty finding or operating a control as evidence.
- Separate observed behavior, heuristic judgment, and inference.
- Capture screenshots for important findings and key states.
- Stop before destructive, financial, private, or production-changing actions without explicit authorization.
- Report access, authentication, browser, or test-data limits.

## Artifact policy

- Return the audit in the conversation by default.
- When durable evidence helps, save reports and screenshots under `tmp/evals/website-experience-audit/<run-slug>/`.
- Write under `docs/` only when the user requests commit-ready documentation.
- Produce one report by default. Create a separate backlog only when the user requests it or the backlog is too large for the report.
- Keep generated browser evidence and operating-system metadata out of source folders.
- Use focused viewport screenshots for findings. Avoid full-page captures when large blank areas or dense content make the evidence unreadable.
- Pair screenshots with text or measurements when the defect is not visually self-explanatory.

## Audit workflow

### 1. Establish the website model

From the initial page and navigation, identify:

- intended audience
- stated value or purpose
- primary content types
- major navigation groups
- expected learning or task sequence
- important diagrams and interactive surfaces
- likely visitor questions

Record the model before exploring deeply. This prevents internal knowledge from hiding poor orientation.

### 2. Define representative journeys

For a deep audit, attempt at least three journeys when the site supports them:

1. Orient: determine what the website offers and where to begin.
2. Find: locate a specific concept, answer, feature, or example.
3. Understand or use: interpret a diagram or complete an interactive example.

Add comparison, return-visit, mobile, or conversion journeys when they matter. State success criteria before each journey.

Before selecting samples, inventory the available route, content, diagram, and interaction types. Choose samples that cover distinct complexity and risk. State the sample count and total population. Do not select only the easiest examples.

### 3. Inspect the information architecture

Evaluate:

- global and local navigation
- naming, grouping, and information scent
- page hierarchy and reading order
- conceptual progression across pages
- cross-links between explanation, reference, and examples
- location awareness and recovery from wrong turns
- support for novice scanning and expert retrieval
- duplication, dead ends, and content hidden in unexpected places

Use the visible experience as evidence. A complete sitemap does not prove that users can understand it.

### 4. Evaluate content and learning flow

Check whether the website:

- states prerequisites and defines unfamiliar terms
- moves from purpose to concept to example to application
- uses headings, summaries, examples, and references with clear roles
- keeps prose, diagrams, and controls synchronized
- provides enough context before asking users to interact
- supports skimming without breaking the explanation
- separates essential guidance from optional depth
- makes success and next steps clear

Test comprehension by writing a short statement of each sampled page's main message. Record when the page does not support one clear statement.

### 5. Evaluate diagrams

For each representative diagram, determine:

- its intended message and whether that message is evident
- the entry point and reading order
- whether labels, legends, symbols, and relationships are clear
- whether surrounding prose prepares and interprets the diagram
- whether density, scale, color, motion, or layout increases cognitive burden
- whether detail appears at the correct time
- whether the diagram remains useful on narrow screens and zoomed text
- whether an accessible text equivalent exists

If the diagram is interactive, also apply the interactive-example checks.

### 6. Exercise interactive examples

Use realistic pointer, keyboard, scroll, hover, drag, and touch-equivalent actions as applicable. Check:

- discoverability and clear affordances
- initial state and instructions
- cause-and-effect clarity
- feedback, latency, and state transitions
- valid, invalid, empty, loading, and reset states
- reversibility and recovery
- keyboard operation, focus order, and visible focus
- touch target size and hover-independent access
- reduced-motion behavior where motion carries meaning
- whether the example teaches something that static content does not
- whether the result connects back to the surrounding explanation

Do not count an animation as useful interactivity unless user input changes understanding or outcome.

### 7. Review the complete experience

Also assess:

- visual hierarchy, typography, spacing, and density
- consistency and trust
- accessibility semantics, contrast risks, and color-only meaning
- responsive layout and interaction at representative widths
- loading stability, broken media, console-visible failures, and obvious performance friction
- interruptions such as banners, overlays, or sticky elements

Use automated accessibility or performance evidence when available. Do not treat automated tools as a substitute for browser use.

For a deep responsive audit, test a narrow and wide viewport. Add an intermediate width when the layout changes materially. Test near an observed breakpoint when a defect might exist only within a small range.

### 8. Score and prioritize

Use the scoring anchors in the audit framework. Tie every material deduction to evidence. Add a coverage or confidence label to each score. Mark untested categories as untested instead of estimating false precision.

For each P0, P1, or P2 finding, record the URL or surface, viewport, starting state, actions, observed result, and recovery. Reproduce important defects when safe. Mark intermittent results as intermittent.

Prioritize findings by:

1. effect on comprehension or task completion
2. number and importance of affected users
3. frequency and reach across the website
4. recovery cost and risk
5. implementation effort, when it can be estimated responsibly

Separate quick wins from structural changes. Explain the user outcome, not only the interface defect.

Treat comprehension scores as expert heuristic judgments unless representative users were observed. Do not claim that users learned or understood a concept from auditor interpretation alone.

## Completion standard

A deep audit is complete only when it includes:

- representative route and journey coverage
- direct browser interaction
- sampled diagrams and interactive examples
- desktop and narrow-screen evidence when supported
- keyboard and accessibility observations
- scores with evidence and stated limits
- prioritized findings with concrete recommendations
- reproducible evidence for high-priority findings
- strengths worth preserving

Do not claim complete coverage when authentication, browser limits, time, or site size restricted the audit.
