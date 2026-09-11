# Frontend Component System Audit Skill

## Purpose

Use this skill to audit a frontend web application and identify where the codebase would benefit from a stronger shared component system.

The audit should focus on:

- Repeated UI patterns implemented inconsistently
- One-off or ad hoc components
- Duplicate layout, form, table, modal, navigation, card, and feedback patterns
- Styling drift across files
- Components that are too tightly coupled to business logic
- Missing shared primitives and reusable feature components
- Opportunities to improve maintainability, consistency, accessibility, and velocity

The output should be an actionable audit report prioritized by impact.

---

## When to Use This Skill

Use this skill when the user asks to:

- Audit a frontend or web app
- Review legacy UI code
- Identify component duplication
- Propose a design system or component system
- Find one-off components that should be shared
- Improve frontend maintainability
- Standardize UI patterns
- Refactor UI into reusable components

---

## Inputs

Ask for or inspect any available source material:

- Frontend source files
- Component directories
- Page or route files
- CSS, SCSS, Tailwind, CSS-in-JS, or style files
- Storybook files, if present
- Design tokens, theme files, or style constants
- Package structure
- Screenshots, if available
- Existing design system docs, if available

If the user provides a repo or files, prioritize the actual code over assumptions.

---

## Audit Goals

The audit should answer:

1. Where is the frontend repeating itself?
2. Which repeated patterns should become shared components?
3. Which existing components are too narrow, duplicated, or inconsistent?
4. Which areas have the highest maintenance cost?
5. Which fixes would create the most leverage?
6. What should be refactored first?
7. What should not be abstracted yet?

---

## Audit Method

### 1. Map the UI Surface Area

Identify major UI categories in the codebase:

- Pages and routes
- Layouts
- Navigation
- Forms
- Inputs
- Buttons and actions
- Tables and data grids
- Cards and panels
- Modals, drawers, popovers, and dialogs
- Toasts, alerts, banners, and empty states
- Loading, error, and skeleton states
- Tabs, filters, search, and pagination
- User/account/settings UI
- Admin/internal tooling UI
- Marketing or public-facing UI

Summarize where each category appears.

---

### 2. Detect Duplication and Drift

Look for repeated patterns such as:

- Similar JSX/TSX markup repeated across files
- Repeated Tailwind class strings
- Similar CSS modules or style objects
- Multiple button implementations
- Multiple input wrappers
- Repeated modal shells
- Repeated card layouts
- Repeated table scaffolding
- Repeated loading/error/empty states
- Repeated page headers
- Repeated form field labels, hints, errors, and validation UI
- Similar conditional rendering logic
- Similar accessibility attributes implemented inconsistently

Call out both obvious duplication and semantic duplication.

Semantic duplication means the code looks different but serves the same UI purpose.

---

### 3. Evaluate Existing Components

For each existing component area, evaluate:

- Is it reusable?
- Is it too specific to a page or feature?
- Does it mix UI rendering with business logic?
- Does it accept sensible props?
- Does it expose too many props?
- Does it duplicate another component?
- Does it enforce consistent styling?
- Does it handle accessibility correctly?
- Does it support loading, disabled, error, and empty states?
- Does it compose well with children?
- Does it belong in shared UI, feature UI, or local page code?

Classify components into one of these categories:

| Category | Meaning |
|---|---|
| Keep | Component is useful and appropriately scoped |
| Promote | Local component should become shared |
| Merge | Multiple similar components should become one |
| Split | Component does too much and needs smaller pieces |
| Replace | Component should be replaced by a better shared primitive |
| Leave local | Too feature-specific to abstract right now |

---

### 4. Identify Missing Component System Layers

Look for gaps in these layers:

#### UI Primitives

Examples:

- Button
- IconButton
- LinkButton
- Text
- Heading
- Badge
- Avatar
- Divider
- Spinner
- Tooltip
- Popover
- Dialog
- Drawer

#### Form Components

Examples:

- TextInput
- TextArea
- Select
- Checkbox
- RadioGroup
- Switch
- DateInput
- SearchInput
- FormField
- FieldLabel
- FieldError
- FieldHint

#### Layout Components

Examples:

- PageShell
- PageHeader
- Section
- Stack
- Inline
- Grid
- SidebarLayout
- EmptyState
- LoadingState
- ErrorState

#### Data Display Components

Examples:

- Table
- DataTable
- DescriptionList
- StatCard
- MetricCard
- ListItem
- Timeline
- Pagination

#### Feedback Components

Examples:

- Alert
- Toast
- Banner
- ConfirmDialog
- ValidationSummary

#### Feature-Level Shared Components

Examples:

- UserPicker
- AccountSwitcher
- BillingCard
- PermissionGate
- AuditLogTable
- SettingsPanel

Make recommendations at the correct layer.

Do not force every reusable component into the lowest-level shared UI package.

---

### 5. Prioritize by Impact

Rank findings by:

- Frequency of duplication
- User-visible inconsistency
- Developer maintenance cost
- Accessibility risk
- Bug risk
- Refactor complexity
- Breadth of reuse
- Alignment with product roadmap, if known

Use this priority scale:

| Priority | Meaning |
|---|---|
| P0 | Critical inconsistency, accessibility issue, or high-risk duplicated behavior |
| P1 | High-leverage shared component opportunity |
| P2 | Useful cleanup with moderate impact |
| P3 | Nice-to-have polish or future abstraction |

---

### 6. Avoid Over-Abstraction

Flag cases where abstraction may be premature.

Do not recommend shared components when:

- The pattern appears only once
- The UI is likely to change soon
- The components are visually similar but behaviorally different
- The abstraction would require many boolean props
- The shared component would encode feature-specific business rules
- Composition would be worse than local clarity

Prefer composable primitives over rigid mega-components.

---

## What to Look For

### High-Impact Smells

Flag these strongly:

- Multiple button styles implemented manually
- Repeated form field wrappers
- Inconsistent validation error rendering
- Multiple modal implementations
- Repeated page header patterns
- Tables with duplicated sorting, loading, empty, or pagination logic
- Inline Tailwind or CSS strings repeated many times
- Components named after pages but reused elsewhere
- Components with too many optional flags
- Styling hardcoded instead of using tokens
- Accessibility handled manually and inconsistently
- Loading/error/empty states implemented differently on each page
- Copy-pasted card or panel markup
- UI primitives mixed with API calls or business logic
- Shared components importing feature-specific modules

---

## Audit Output Format

Produce the audit in this structure.

# Frontend Component System Audit

## Executive Summary

Briefly describe the current state of the frontend component system.

Include:

- Overall maturity
- Main sources of duplication
- Highest-risk inconsistencies
- Best opportunities for shared components
- Recommended first refactor

## Top Findings

List the highest-impact issues first.

Each finding should include:

### Finding: `<short title>`

- **Priority:** P0 / P1 / P2 / P3
- **Area:** Forms / Tables / Layout / Navigation / Styling / Feedback / etc.
- **Evidence:** Files, components, or code patterns observed
- **Problem:** Why this is costly or risky
- **Recommendation:** What to create, merge, split, or standardize
- **Suggested abstraction:** Name and rough API shape
- **Migration path:** How to adopt it incrementally
- **Risk:** Low / Medium / High
- **Estimated effort:** Small / Medium / Large

## Component Opportunities

Use a table when helpful.

| Opportunity | Current pattern | Recommended component | Priority | Effort |
|---|---|---|---|---|
| Repeated page headers | Inline title/actions layout | `PageHeader` | P1 | Small |
| Duplicate modal shells | Multiple custom dialogs | `Dialog` / `ConfirmDialog` | P1 | Medium |

## Suggested Component Architecture

Recommend a structure such as:

```txt
src/
  components/
    ui/
      Button.tsx
      Dialog.tsx
      FormField.tsx
      Input.tsx
      Select.tsx
      Table.tsx
    layout/
      PageShell.tsx
      PageHeader.tsx
      Section.tsx
      EmptyState.tsx
    feedback/
      Alert.tsx
      Toast.tsx
      ConfirmDialog.tsx
    data-display/
      DataTable.tsx
      StatCard.tsx
    feature/
      users/
      billing/
      settings/