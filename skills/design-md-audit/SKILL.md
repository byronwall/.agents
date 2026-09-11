# Design.md Web App Audit Skill

## Purpose

Use this skill to audit a web application against a `DESIGN.md` file and surface the most important mismatches between the implemented UI and the intended design system.

The skill is meant to be run repeatedly. Each run should identify the highest-leverage problems, help the team fix systemic drift, and avoid wasting attention on cosmetic one-offs unless the one-off is severe or blocking.

## When To Use This Skill

Use this skill when the user provides one or more of:

- A `DESIGN.md` file.
- Source code for a web application.
- Screenshots of implemented UI.
- A live app URL, if the current environment supports browsing or screenshot capture.
- A diff, branch, PR, or changed file list.
- Prior audit reports to compare progress over time.

Use it especially when the user asks for:

- Design system conformance review.
- UI polish review.
- Screenshot review.
- Styling drift detection.
- Design token adoption review.
- Repeated audits intended to whittle down issues over time.

## Core Goal

Produce an evidence-first design audit report that answers:

1. Where does the implementation most conflict with `DESIGN.md`?
2. Which problems have the largest user, product, or maintenance impact?
3. Which issues are systemic patterns versus isolated defects?
4. What is the smallest useful fix?
5. What hardening change would prevent the same problem from recurring?

## Operating Principles

### Prioritize systemic conflicts

Prefer findings that reveal broad drift across the app:

- Incorrect visual language repeated across many components.
- Ad hoc colors instead of design tokens.
- Spacing scale violations across multiple surfaces.
- Typography families, sizes, weights, or letter spacing that conflict with the design system.
- Shape/radius language that changes the product personality.
- Elevation, shadows, blur, translucency, or borders used against guidance.
- Components that duplicate styling instead of using shared primitives.
- Screenshot evidence that shows many local symptoms of the same root cause.

### Still report important one-offs

A one-off issue is worth reporting when it is:

- In a high-traffic or high-trust surface.
- Visually dominant.
- Accessibility-impacting.
- Confusing to users.
- A likely sign of future copy/paste drift.

When reporting a one-off, explicitly label it as `one-off` and explain why it still matters.

### Treat tokens as normative

If `DESIGN.md` contains YAML frontmatter, treat token values as the source of truth for exact values.

Markdown prose provides rationale and application guidance. Use it to interpret intent, but do not override explicit token values unless the prose exposes a conflict inside the design document itself.

### Prefer evidence over vibes

Avoid vague statements like:

- “Feels off.”
- “Could be more polished.”
- “Spacing is inconsistent.”

Instead write:

- “Toolbar controls use 16px gaps in three places, while `DESIGN.md` calls for tight 4px toolbar gaps. This makes the toolbar read as a loose SaaS header instead of an attached control cluster.”

### Make fixes actionable

Every major finding must include:

- What is wrong.
- Why it matters.
- Evidence.
- Minimal fix.
- Hardening fix.
- Confidence.
- Whether it is systemic or one-off.

## Inputs To Request Or Inspect

### Required

- `DESIGN.md`

### Strongly preferred

At least one of:

- Screenshots of the current UI.
- Relevant source files.
- CSS, Tailwind config, theme tokens, component library primitives, or design-system files.
- A list of pages/components to inspect.

### Optional

- Prior audit report.
- Product context or target audience.
- Known intentional deviations.
- Browser viewport sizes.
- Accessibility requirements.
- PR or commit scope.

## If Inputs Are Incomplete

Do not block unless `DESIGN.md` is missing.

If screenshots are missing, audit the code and clearly mark visual conclusions as code-inferred.

If code is missing, audit screenshots and clearly mark implementation-level fixes as inferred.

If both screenshots and code are present, cross-check them:

- Use screenshots to identify visible drift.
- Use code to identify systemic root causes.
- Prefer fixes that address source-level causes rather than screenshot-level symptoms.

## Audit Workflow

### 1. Parse `DESIGN.md`

Extract:

- Design system name and description.
- Color tokens.
- Typography tokens.
- Spacing tokens.
- Rounded/radius tokens.
- Component tokens.
- Section prose for:
  - Overview.
  - Colors.
  - Typography.
  - Layout.
  - Elevation & Depth.
  - Shapes.
  - Components.
  - Do's and Don'ts.

Create a compact `Design Intent Map`:

- Personality keywords.
- Must-preserve traits.
- Must-avoid traits.
- Exact token requirements.
- Component-specific rules.
- Ambiguous or conflicting guidance.

### 2. Build an implementation evidence map

From code, collect:

- Token/theme files.
- Global CSS.
- Tailwind config.
- Component primitives.
- Page-level layout files.
- Repeated class names.
- Hardcoded colors.
- Hardcoded spacing.
- Hardcoded radius values.
- Shadow, blur, opacity, gradient, and border usage.
- Font-family, font-size, font-weight, line-height, and letter-spacing usage.
- Component variants and size systems.

From screenshots, inspect:

- Overall visual personality.
- Page hierarchy.
- Color use.
- Typography.
- Density and spacing.
- Shapes and radii.
- Elevation and depth.
- Component states.
- Repetition of the same mismatch across surfaces.
- Areas that look correct and should be preserved.

### 3. Compare by design dimension

Evaluate the app against these dimensions:

1. Visual identity and product personality.
2. Color discipline.
3. Typography conformance.
4. Layout density and spacing rhythm.
5. Shape and radius language.
6. Elevation, shadows, borders, blur, and depth.
7. Component token adoption.
8. Interaction states.
9. Information hierarchy and scanability.
10. Responsiveness, if screenshots or code indicate it.
11. Accessibility impact, especially contrast, focus states, text size, and target size.
12. Maintainability and design-system enforcement.

### 4. Cluster symptoms into root causes

Before writing findings, group related evidence into systemic patterns.

Examples:

- `Hardcoded visual values bypass tokens`.
- `Soft SaaS card language conflicts with industrial drafting language`.
- `Toolbar controls are implemented as independent buttons instead of attached instrumentation clusters`.
- `Typography scale is mixed because components define font styles locally`.
- `Table density is inconsistent because row heights and padding are not centralized`.

Only create separate findings for symptoms when they require materially different fixes.

### 5. Rank findings

Rank by combined impact:

- Severity of design conflict.
- Visibility to users.
- Blast radius across pages/components.
- Maintenance cost.
- Accessibility impact.
- Ease of fixing.
- Whether fixing it unlocks many downstream improvements.

Use priorities:

- `P0`: Major contradiction of the design system, high-visibility or accessibility-impacting, or blocks reliable future work.
- `P1`: Important systemic drift or visible one-off on a primary surface.
- `P2`: Lower-impact cleanup, localized polish, or hardening after P0/P1 fixes.

Do not include more than 10 major findings unless the user asks for exhaustive review. Prefer the top 5-8.

## Evidence Standards

Use the strongest available evidence:

- File paths and component names for code findings.
- Screenshot names and visible regions for screenshot findings.
- Token names and section names from `DESIGN.md`.
- Exact implemented values when known.
- Repeated examples to prove systemic drift.

When exact values cannot be verified from screenshots, state that the issue is visual/inferred.

Confidence levels:

- `High`: direct code or token evidence plus visible screenshot support.
- `Medium`: direct code evidence or clear screenshot evidence, but not both.
- `Low`: plausible issue from partial evidence; requires verification.

## Mandatory Report Format

Create a new markdown report for each run. Do not overwrite prior reports.

Preferred locations:

- `tmp/design-audit/YYYY-MM-DD-<scope>-design-audit.md`
- `docs/design-audits/YYYY-MM-DD-<scope>-design-audit.md` if the user wants committed reports.

Use this exact section order.

### 1. Executive Summary

Include 3-8 bullets.

Each bullet must include:

- Risk.
- Impact.
- Where.
- What is wrong.
- How to fix.

### 2. Design Intent Map

Summarize the key design requirements extracted from `DESIGN.md`.

Include:

- Product personality.
- Must-use tokens.
- Must-avoid patterns.
- Component rules.
- Ambiguities or conflicts inside `DESIGN.md`, if any.

### 3. Highest Priority Findings

For each finding:

#### Finding N: <specific title>

- **Priority:** `P0`, `P1`, or `P2`.
- **Classification:** `systemic` or `one-off`.
- **Confidence:** `High`, `Medium`, or `Low`.
- **Where:** files/components/screenshots/regions.
- **What is wrong:** concrete mismatch against `DESIGN.md`.
- **Why it matters:** user impact, product impact, and maintenance impact.
- **Evidence:** exact code values, screenshot observations, or repeated examples.
- **Minimal fix:** smallest safe corrective change.
- **Hardening fix:** reusable token, component primitive, lint rule, visual regression, or checklist improvement.
- **Suggested owner:** design-system, feature team, infra/tooling, or product surface owner.

### 4. Systemic Patterns

Cluster repeated issues into root causes.

For each pattern include:

- Pattern name.
- Symptoms.
- Root cause.
- Affected surfaces.
- Recommended system-level fix.
- How to verify improvement on the next run.

### 5. One-Off Issues Worth Fixing

Only include one-offs that are important.

For each:

- Location.
- What is wrong.
- Why it is not systemic.
- Why it still matters.
- Minimal fix.

### 6. Token And Component Adoption Review

Include:

- Tokens used correctly.
- Tokens missing or bypassed.
- Hardcoded values that should become tokens.
- Component variants that should be centralized.
- Places where `DESIGN.md` may need additional component tokens.

### 7. Screenshot Review Notes

If screenshots were provided, include:

- What visually matches the design system.
- What visibly conflicts.
- Which visible issues appear systemic.
- Which require code inspection to confirm.

If no screenshots were provided, write:

- `No screenshots were provided. This section is limited to code-inferred visual risks.`

### 8. Code Review Notes

If source code was provided, include:

- Files inspected.
- Styling architecture observations.
- CSS/theme/Tailwind/component primitive concerns.
- Repeated implementation patterns.
- Suggested refactors.

If no code was provided, write:

- `No source code was provided. This section is limited to screenshot-inferred implementation risks.`

### 9. Suggested Fix Plan

Group fixes into phases:

#### Phase 1: Highest leverage corrections

- 1-3 changes that reduce the most visible or systemic drift.

#### Phase 2: Component hardening

- Shared primitives, tokens, wrappers, or theme changes.

#### Phase 3: Regression prevention

- Lints, visual tests, screenshot baselines, Storybook/preview coverage, PR checklist additions.

### 10. Re-run Checklist

Include a compact checklist for the next audit run:

- Screens/pages to re-check.
- Files/components expected to change.
- Specific conflicts expected to disappear.
- Metrics or visible signs of improvement.
- Remaining known risks.

### 11. Top Issues Table

Include at least the top 5 issues when available.

| Issue | Classification | What is wrong | Recommended fix | Priority |
| ----- | -------------- | ------------- | --------------- | -------- |

### 12. Confidence And Gaps

Include:

- Overall confidence.
- Missing inputs.
- Assumptions.
- What would improve the next audit.

## Finding Writing Template

Use this template for every major issue:

```markdown
#### Finding N: <specific mismatch>

- **Priority:** P1
- **Classification:** systemic
- **Confidence:** High
- **Where:** `path/to/file.tsx`, `path/to/styles.css`, screenshot `<name>` top toolbar
- **What is wrong:** <specific mismatch against token/prose>
- **Why it matters:** <user/product/maintenance impact>
- **Evidence:**
  - `DESIGN.md` says <token/rule>.
  - Implementation uses <value/pattern>.
  - Screenshot shows <visible symptom>.
- **Minimal fix:** <smallest safe code/design change>
- **Hardening fix:** <token/component/lint/visual regression/checklist>
- **Suggested owner:** <owner>
```

## Scoring Rubric

Optionally include a score table when the user wants a measurable baseline.

Scores should be 1-10, where 10 means strong alignment with `DESIGN.md`.

Recommended dimensions:

| Dimension             | Score | Why it scored this way | Top fix |
| --------------------- | ----: | ---------------------- | ------- |
| Visual identity       |       |                        |         |
| Color discipline      |       |                        |         |
| Typography            |       |                        |         |
| Layout and density    |       |                        |         |
| Shape language        |       |                        |         |
| Elevation and depth   |       |                        |         |
| Component consistency |       |                        |         |
| Interaction states    |       |                        |         |
| Maintainability       |       |                        |         |

Only include scores when useful. Do not let scoring replace concrete findings.

## Suggested Commands For Agentic Environments

When the environment supports shell commands, use a run sheet like this and adapt paths to the project.

```bash
# 1. Confirm design source exists
find . -maxdepth 4 -iname 'DESIGN.md' -o -iname 'design.md'

# 2. Find likely styling entry points
find . -maxdepth 5 \( -iname 'tailwind.config.*' -o -iname 'theme.*' -o -iname '*tokens*' -o -iname '*.css' \) | sort

# 3. Search for hardcoded colors
rg --line-number --no-heading '#[0-9A-Fa-f]{3,8}|rgb\(|rgba\(|hsl\(|hsla\(' . \
  --glob '!node_modules' \
  --glob '!dist' \
  --glob '!build' \
  --glob '!coverage'

# 4. Search for shadows, blur, gradients, opacity-heavy styling
rg --line-number --no-heading 'shadow|box-shadow|drop-shadow|blur|backdrop|gradient|opacity' . \
  --glob '!node_modules' \
  --glob '!dist' \
  --glob '!build' \
  --glob '!coverage'

# 5. Search for radius and spacing drift
rg --line-number --no-heading 'rounded|border-radius|padding|margin|gap|space-|p-|m-|px-|py-|mt-|mb-|ml-|mr-' . \
  --glob '!node_modules' \
  --glob '!dist' \
  --glob '!build' \
  --glob '!coverage'

# 6. Search for typography drift
rg --line-number --no-heading 'font-family|font-size|font-weight|line-height|letter-spacing|font-' . \
  --glob '!node_modules' \
  --glob '!dist' \
  --glob '!build' \
  --glob '!coverage'
```

## Common Design Drift Patterns To Check

### Token bypass

Symptoms:

- Hardcoded hex colors repeated in components.
- Tailwind arbitrary values where tokens exist.
- Local CSS variables that duplicate `DESIGN.md` tokens.

Fix:

- Map `DESIGN.md` tokens into the app theme.
- Replace local values with semantic tokens.
- Add a stylelint or eslint rule for disallowed raw values.

### Personality mismatch

Symptoms:

- The app uses a visual mood that contradicts the overview.
- Example: friendly SaaS cards in an industrial drafting interface.

Fix:

- Identify the surface language that creates the wrong personality.
- Change shared panels/buttons/tables first.
- Avoid per-page cosmetic patches.

### Density drift

Symptoms:

- Repeated oversized padding.
- Inconsistent table row heights.
- Loose toolbar groups.
- Too much whitespace between related controls.

Fix:

- Centralize spacing in component primitives.
- Create density variants if multiple densities are legitimate.
- Update table, toolbar, inspector, and card primitives.

### Shape drift

Symptoms:

- Pilly controls where the design calls for rectilinear controls.
- Large radii on utilitarian surfaces.
- Mixed radii without a clear role.

Fix:

- Map each component category to rounded tokens.
- Replace shape styling in primitives.
- Reserve full radius only for explicit allowed cases.

### Elevation drift

Symptoms:

- Heavy shadows.
- Glassmorphism.
- Backdrop blur.
- Floating cards where the design calls for borders and tonal layers.

Fix:

- Replace depth with borders, tonal fills, and selected states.
- Restrict shadows to popovers/dialogs.
- Add a lint/checklist item for blur/shadow usage.

### Typography drift

Symptoms:

- Mixed font families.
- Marketing-style display fonts in workspace UI.
- Inconsistent label casing and tracking.
- Local font sizes instead of typography tokens.

Fix:

- Define text primitives.
- Route headings/body/labels/table cells/node labels through shared classes.
- Add a token usage checklist.

## Report Tone

Be direct and implementation-oriented.

Do not be mean. Do not flatter. Do not hedge when evidence is strong.

Use language like:

- “This conflicts with…”
- “The root cause appears to be…”
- “Fix this at the primitive level, not per page.”
- “This looks like a one-off because…”
- “This should be deferred until the systemic issue above is fixed.”

## Anti-Patterns

Avoid:

- Exhaustive lists of tiny visual nits.
- Recommending one-off CSS patches for systemic problems.
- Reporting screenshot-only impressions as certain code facts.
- Treating prose as less important than tokens for high-level personality.
- Treating tokens as optional when exact values are provided.
- Creating a report without a re-run checklist.
- Writing findings without fixes.

## Completion Criteria

A successful run produces:

- A clear audit report.
- The top design conflicts ranked by importance.
- Systemic root causes separated from one-off issues.
- Minimal and hardening fixes for every significant issue.
- A practical next-run checklist so repeated audits can show progress.
