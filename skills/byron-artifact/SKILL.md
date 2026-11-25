---
name: byron-artifact
description: >-
  Byron's house style and starting template for Claude artifacts (claude.ai pages published with the Artifact
  tool) that explain a large body of evidence: a PR stack, an investigation, a migration, a review, a system
  before and after. Covers structure (spine table, parts by kind then by item, "what it leaves" closer), visual
  hierarchy, the one table style, color rules, plain-language copy, and the full-screen pan/zoom diagram carousel
  he asks for every time. Ships `template/page.html` to copy. Use whenever you are about to build, restyle, or
  "10x" a Claude artifact or explainer page for Byron, when he says "make a Claude artifact", "put this in an
  artifact", "explainer page", "my preferred artifact styles", or shares a claude.ai/artifact link to rework,
  even when he doesn't name this skill.
---

# Byron's Claude artifacts

Byron reads these pages to understand a large change or a pile of evidence fast, then asks follow-up questions on specific areas. Every rule below is a correction he has already given at least once; [references/feedback-log.md](references/feedback-log.md) has his words and the pages they came from. Start from the template and these rules so the first version is close to done.

## Start

1. Follow the Artifact tool's own steps (quickstart, or `artifact-design`), then build from this skill instead of designing from scratch. A deck, document or dashboard type still wins when Byron asks for one of those; this skill is for a page.
2. Copy [template/page.html](template/page.html) into the scratchpad as `site/<slug>.html`, with diagrams beside it in `site/d/`. Keep its tokens, table, nav, viewer and hover-card code; replace the content and the `ITEMS`, `STACKS` and `LEFT` data. Delete the parts the page doesn't need rather than leaving them empty.
3. Read `byron-ui-taste` before changing the look, and run the anti-slop pass from `write-byron-voice` on all text before the first publish (see Copy).
4. Byron's earlier pages, with what is special about each, are indexed in `/Users/byronwall/repos/daily-planning/reference/claude-artifacts/README.md`. Read the closest one with the Artifact tool's `read` (pass `path: "index.html"` to save the full page) before building a page of the same kind.
5. A page people write to (a picker of mock-ups, a proposals board) keeps their picks in the page's shared collection, not in browser storage, and Claude reads them back from there; Full View Design Calls and Rel app Wave 4 Candidates work this way. Load `artifact-capabilities` for it. The rest of this skill still governs the look.
6. When the page's shape is a real choice (one big change versus many items, reviewer versus user audience), run `consider-contrast` inline for the structure, then continue.

## Structure

- **Header:** an eyebrow with the tracker key, owner and date; a short `h1` (the `<title>` is two to four words); a two- or three-sentence lede saying what changed and what is true afterwards; a `facts` row of four or five bold numbers (items, CI state, lines removed and added, who is asked to review); then one muted line saying what the page is for, such as "This page says where to look in the review and why. Findings belong in a separate document."
- **Sticky part nav** with numbered pills. The highlight follows a scroll check, not an IntersectionObserver.
- **Part 1 is the spine:** one row per item (PR, layer, finding) with number, name, one-line outcome, risk and size. A row opens a popover over the content, so nothing below moves, holding what it changes, the code to read first (labelled in plain words, with the file and line small underneath, linked to the exact line), the proof, what the proof didn't cover, and an amber "Not in the description" note where the code does more than claimed. `#item-X` in the URL opens that row. For a PR stack, the size column is a small bar of lines deleted that splits product code from fixtures and tests, with the numbers under it, and a Reviewers column marks the reader's own requests as "you" in the accent color (PyRel-only stack page). Under the spine, show how we get from here to there: the system as it is today, the system as intended, and the proposed delivery slices, side by side. A single before/after drawing of one concept misses that big picture; move it to the how-it-works part.
- **Group by kind first, then switch to by item.** Overview parts (what goes, how it works now, who notices) group by category and cite items inline. Once a part would list every item again (questions to ask, code-vs-description gaps, unproven areas, per-item diagrams), switch to one section per item in order: its diagram on the left; what to ask, the flag and what's unproven on the right.
- **Show kinds of change separately.** When the work removes things, separate whole subsystems removed (callers go too) from branches pruned (one option inside a step that stays) from paths rewritten (same job, new way). Define each kind in one sentence at the top of the part, then give each its own What / Before / After table.
- **Storage gets its own drawing.** When the work changes what is stored or where, add a before and after pair that names every store (tables, rows, files, outboxes), who writes each one and when, plus a table of Where / What it holds / Before / After.
- **Answer "rewritten or reused?" for the core subsystem.** When readers will ask how much of an existing system was rewritten, give a short section on how the two representations relate before and after, and a bucket table (reused unchanged, rewritten in part, trimmed, moved, deleted, new) with line counts.
- **Leave out what another in-flight change already covers.** When a parallel stack removes the same things, say so in one line with a link and drop the detail, rather than describing it twice.
- **A system explainer keeps the same bones.** When the page explains how something works rather than a change (Core PyRel Explained), the spine lists the operations or concepts instead of PRs; a "Reading the …" part defines the notation in a Notation / In plain words / Source table before any section uses it; then one section per operation, its diagram on the left and what to notice on the right; then a part that puts them together, the edge cases (missing values, errors), and "What it doesn't cover" in place of "What it leaves behind". Anything the page invents to save space (a condensed display, an abbreviation) says in its own heading that it is the page's, not the system's.
- **Name page sections "Section N" when the items are "parts".** Two numbered sequences both called "part" make links like "part 6" ambiguous.
- **"Who notices":** a Who / What happens / Action needed table in users' terms.
- **Close with "What it leaves behind":** a table of What / Kind / From / Tracked / Next move, where Kind is a red **Gap** (people hit it once this lands; raise it now) or a blue **Future work** (capture it so it isn't lost). Say nothing is tracked unless the row says so.
- **Footer provenance:** what was read and as of when (commit, date), and that nothing was posted or run live.
- **The page motivates the work and holds no verdict.** A page that sets up a review points at where to look; the review itself is a separate document. Keep durable facts in their system of record (task, PR body, repository) and link to them; the artifact holds no fact found nowhere else.

## Diagrams and the viewer

Every diagram opens full screen in the template's viewer. Never ship a diagram that only opens in a new tab or at its inline size. The viewer must:

- gather every diagram on the page into one carousel, in page order, with a "3 / 12" count and "Title · caption" (a middot, never an em dash);
- open fitted to the whole image, with −, Fit, 100%, + and Close buttons and large ‹ › buttons on a dark backing;
- zoom at the cursor with the wheel (pinch on trackpads and touch), zoom in on double-click, and pan by dragging, with no clamp so any edge can be pulled to the middle of the screen;
- take ← → to step, + − to zoom, 0 to fit, Esc to close, return focus to the thumbnail, and lock page scroll while open;
- never select text while dragging, and keep text sharp at any zoom. The template resizes the image instead of CSS-scaling it, because scaled SVG goes blurry when it settles.

When the diagrams already draw the code (colored ranges, annotations, before and after), don't add raw code panes or example browsers beside them. Unhighlighted text in nested rounded boxes with their own scroll bars reads worse than the diagram and clashes with the page; point to the source file in the task instead.

Inline, diagrams are `button.pic` thumbnails on a light `--figure-bg` panel (kept light in dark mode), in a grid of about 340px columns; one wide figure per page at most, capped near 90% of the viewport height. Each caption starts with a bold name and then says what the drawing found. **Pair every before/after drawing.** When two drawings show the same structure before and after (or today and intended, today and proposed), put them side by side in one `.pair` block: a header row with BEFORE at top left, the shared name in the middle and AFTER at top right, the two figures under it, stacking on a phone, where each thumbnail carries its own corner tag instead. A drawing that shows only the before or only the after, or both in one drawing, gets a `.corner` tag (Before, After, Before and after) in its top-right corner and says so in its title, and points to its partner when there is one. The template has the CSS. Render draftably diagrams with `draftably inspect <file.draft> --svg > site/d/<name>.svg` and publish them through the Artifact tool's `files` with `root` set to `site/`.

## Look

- **Tokens:** the template's `:root` set: a blue-grey `--page` (#e9edf3) under a white `--surface` sheet with a 14px radius, `--panel` (#f5f7fb) for header cells and callouts, ink #161d2b, muted #5a6577, rules #dde3ec, accent #34557f, with the dark set under both the media query and `[data-theme="dark"]`. Inter for text, JetBrains Mono for numbers and code.
- **Type does the hierarchy:** `h1` 800 weight, tight tracking; `h2` 1.7rem 800; `h3` 1.15rem 700; small uppercase muted eyebrows and `h4` labels; body 16px, line height 1.6, prose capped near 760px.
- **Space separates; lines don't.** Parts sit 64px apart and per-item sections 52px apart. No `<hr>`, no border under the nav, no rule above parts or between items or above the footer. The only lines are row lines inside tables and the outer border of a table, popover or card.
- **One table style everywhere:** a rounded outer border, a `--panel` header row with small uppercase muted labels, a line between rows, no stripes and no banded column colors. A columnar list with no headings is a table missing its headings; give it headings.
- **Color means one thing each.** Content text is all `--ink`. Muted is only for small meta (numbers, sizes, file paths, captions). Red is only for high risk, removed and Gap; amber only for medium risk and "Not in the description"; green only for added lines in a code diff; blue only for links, the active nav pill, the reader's own "you" and Future work. Fills are pale tints; saturated color is for marks and small labels.
- Tabular numbers (`font-variant-numeric: tabular-nums`) wherever numbers line up.
- Monospace text turns ligatures off, so `!=`, `->` and `>=` show the characters the code has (Core PyRel Explained).

## Copy

- **Plain words first.** Describe what a user or developer sees or does ("Keeping models on disk", "Refusing a link with a reason"), not class, file or function names. Code names appear only in the labelled code-level view or small under a plain label. Never a bare list of identifiers.
- **Ground every reference on first mention** in each part: `#2385 Snowflake oplog only`, `RAI-56099 PyRel-only stack`. Hover cards on reference links carry the details (size, risk, reviewers, proof) so the reader keeps their place.
- **Anti-slop pass** with the latest `write-byron-voice` from `bdw-agents` (`git -C ~/repos/bdw-agents pull` first): no colon reveals, no "not X, but Y", no announcement sentences ("Changes implied by everything above."), no moral closers, no puffery or importance labels, no em dashes, no jargon in parentheses. Colons that introduce a list or a label ("Not proven: …") stay.
- Questions the agent suggests, rather than ones somebody asked, say so.

## Check before you publish

The built-in browser isn't signed in to claude.ai, so check a local copy over HTTP. Never open a `file://` path: the browser pane's page tools refuse local files ("page tools can't act on it here") and screenshots come back blank. Serve `site/` with `python3 -m http.server <port> --directory site` in the background under the `deadline` wrapper where one exists, `navigate` a fresh tab to `http://localhost:<port>/`, reload with a cache-busting query each time, and stop the server when you're done.

- Desktop width and 375px in dark mode: no sideways scroll, no overlapping columns, the nav stays one scrollable row on a phone.
- Open a spine row, a hover card and the viewer: fitted on open, drag pans without selecting text, arrows step through every diagram, Esc closes.
- Scroll to the last part and confirm the nav highlights it.
- The console shows no errors.

Publish with a one-sentence `description`, then say in the reply what you checked and what you didn't (for example, the published page itself). Republish to the same path for each later round.

## After a round of feedback

When Byron corrects something this skill didn't cover, fix the page, then add the correction to [references/feedback-log.md](references/feedback-log.md) and the rule here in the same commit to `bdw-agents`, so the next page starts from it.
