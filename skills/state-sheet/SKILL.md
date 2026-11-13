---
name: state-sheet
description: Audit and fix the interaction states of every control in a running web app, in place, without Storybook or any added tooling. A read-only Playwright script finds each kind of control on real pages, captures it at rest, on hover, with keyboard focus, and pressed, and lays the results out as a contact sheet. It flags states that look the same as rest and lists the computed-style changes. Then you define a token set and one state model, apply it in the app's own stylesheet, and prove the change with a before/after sheet. Use when Byron says `/state-sheet`, asks to audit or "make amazing" the hover, press, or focus states, wants every button and interactive element to follow design tokens, or asks for a contact sheet of component states.
---

# State sheet

Byron wants to see every control in every state, side by side, on the real app, and then make all of them follow one system. This skill does that **in place**. Add no Storybook, no component gallery package, no test harness, and no new dependency in the project. The only tool is `scripts/state-sheet.mjs`, which drives the running app with Playwright.

## Safety first (read before you run anything)

Pressing a control for a screenshot can fire a real click. In the first use of this method, a press shortlisted and dropped real job postings. The script protects against this in three ways. Keep all three:

- It aborts every non-GET request (`--allow-writes` turns this off; never use it on real data).
- It holds the mouse down for the capture, then moves away before it releases, so no `click` reaches the control.
- It dismisses dialogs and closes popups.

Client-only state (local storage, an in-memory toggle) can still change. Before and after each run, check `git status` for data files the app writes, and restore anything the run changed. Say so in your reply if it happened.

## Process

### 1. Inventory

- Start the app with the project's normal dev command or launch config. Find the pages that hold the most kinds of controls: usually the home page, a list, a detail view, and a form.
- Read the stylesheet's tokens and its state rules. Count them so you can report the before state:
  ```bash
  grep -cE ':(hover|active|focus|focus-visible|focus-within)' src/**/*.css
  grep -oE 'transition: [^;]*' -r src --include='*.css' | sort | uniq -c | sort -rn
  grep -oE 'font-size: [^;]*' -r src --include='*.css' | sort | uniq -c | sort -rn
  ```
- Note multiple `:root` blocks, hard-coded colors and durations, `outline: none` with no replacement, and controls hidden with `display: none` (a keyboard dead end).

### 2. Capture the before sheet

```bash
node ~/.agents/skills/state-sheet/scripts/state-sheet.mjs \
  --base http://localhost:3000 --pages /,/list,/detail/1 \
  --out tmp/state-sheet --prefix before
```

- With no `--selectors`, it **discovers** controls: buttons, links, fields, ARIA widgets, focusable elements, and anything with `cursor: pointer`. It keeps one instance per kind (tag, role, and classes without state classes), and prefers an instance at rest over one that is current, selected, or checked.
- To audit a known list, pass `--selectors '.btn,.tab:not(.on),.row'` or `--selectors-file controls.txt` (one selector per line, `#` comments allowed). The output lists any selector it could not find on the given pages.
- Other options: `--dark` (prefers-color-scheme: dark), `--width/--height/--scale`, `--max 80`, and `--wait 250` (ms to settle after each state).
- Output in `--out`: `<prefix>-states[-N].png` (pages of 20 controls), `<prefix>-states.html` (all controls), `<prefix>-states.json` (flags and style changes), and `<prefix>-page-*.png` (one screenshot of each page).
- Make sure `tmp/` is ignored by git. If it isn't, add it to `.git/info/exclude`.

Look at every sheet page. Read the flags in the terminal output:

| Flag | Meaning |
|---|---|
| `no hover` | hover pixels equal rest |
| `no press` | pressed pixels equal hover |
| `no focus ring` | keyboard focus pixels equal rest, or the element is not focusable |
| `focus ring may clip at viewport edge` | an outer ring on an element at the window edge |

A flag is a lead, not a verdict. A row with no focus ring may be correct when the list uses J/K keys, but say so.

### 3. Define the system

Write one token block and one state model before you edit any rule. Reuse the app's existing colors and names; organize them, don't rebrand.

- **Scales:** neutral and accent ramps (25–900), status ramps (50/100/200/600/700). Semantic names point at the scales: `--text`, `--muted`, `--line`, `--accent`, `--accent-tint`, `--hover`, `--press`.
- **Type:** a size scale (for example 10/11/12/13/15/20/24), weights, and line heights.
- **Space and size:** a 4px space scale, control heights (xs–lg), an icon-button size, and a radius scale.
- **Motion:** durations (instant 80, fast 120, base 160, slow 240, slower 320 ms) and easings (standard, out, in, in-out). Use explicit property lists, never `transition: all`.
- **Focus:** color, width, and offset tokens, plus a field halo.

The state model, applied to every control family:

| State | Rule |
|---|---|
| Hover | One step stronger. Wrap it in `@media (hover: hover)` so touch never sticks. |
| Press | Two steps stronger, plus `scale(0.97)` on compact controls (0.9 on icons, none on rows and tabs). Snap in with the instant duration. |
| Selected | Accent tint. It switches at once; only hover fades. Selected plus hover deepens the tint. |
| Focus | Keyboard only (`:focus-visible`). A 2px ring outside compact controls, and inset (negative offset) on rows and full-width items so scroll containers don't clip it. Fields get a border plus a halo instead. |
| Disabled | 45% opacity and `cursor: not-allowed`, with no hover or press. |
| Reduced motion | Keep color feedback; drop the press scale and thumb motion. |

Group controls into families and give each family one rule set: bordered buttons, primary, danger, quiet (text and icon) buttons, segmented controls, tabs, nav items, rows (lists and table rows), fields, and marks (checkbox, switch). Controls on a tinted sidebar lift to translucent white instead of darkening.

### 4. Apply it in place

- Put the token block at the top of the main stylesheet. Merge any later `:root` blocks into it and delete them.
- Add one "Controls" section at the end of the stylesheet that implements the state model for every family.
- Delete the old, scattered hover/active/focus rules that the Controls section now owns. Do it with a script that prints each rule it removes, and review that list. Keep rules where the state is on a parent (`.row:hover .icon-btn` reveals a button) or inside `:not()`.
- Replace hard-coded durations, font sizes, and colors with tokens. Every scripted replace must assert its match count.
- Fix the dead ends you found: a hidden input that a keyboard can't reach, `outline: none` with nothing in its place, and native checkboxes or selects that ignore the system.
- If another session has uncommitted edits in the same stylesheet, keep their lines out of your scripted changes and out of your commit.
- Optional, when the app has routing: add a small, unlinked `/system` page that shows the tokens and one of each control live. It is a page in the app itself, not new machinery.

### 5. Prove it

Run the same command with `--prefix after`, and look at every page of the sheet. Compare it with the before sheet: every row should show a visible, deliberate change in each state, and the flags should only cover cases you can explain. Then:

- Tab through a page and confirm that the focus order works and every ring is visible.
- Take full-page screenshots at about 1440px and check that nothing shifted or changed size.
- Run the project's typecheck and lint.
- Confirm in `git status` that the runs changed no data.

### 6. Deliver

Commit per the project's rules. In the reply, cover what each state now does, the token groups, the bugs you fixed (for example keyboard dead ends), the flags you left and why, and the before/after sheet paths. Send the two sheets with `SendUserFile` so Byron can compare them.
