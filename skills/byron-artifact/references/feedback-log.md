# Feedback log

The corrections behind each rule in `SKILL.md`, with Byron's words and where they came from. Add new rounds at the bottom with a date, and fold the rule into `SKILL.md` in the same change.

## Client Rewrite page (TASK-0101, November 20, 2026)

The page whose look became the default. Artifact `4d49f3ae-c725-4024-8ed0-88b25d40aa5e`, "Rel app Client Rewrite".

- Viewer: "revise the artifact so that all of the images open in a view box that way you can pan and zoom and make sense of them. And ideally the view box would be carousel style where you can just [arrow] and go through them all."
- Look: "make it stylistically look like this example here, where the colors are much more blue-tinted and the main reading surface is a white background." This produced the blue-grey `--page`, white `--surface` sheet and the token set in the template.
- Content: asked for the missing diagram of how the data is actually stored, old versus new. A page about a change needs the before/after drawing of the thing that changed.

## PyRel-only stack page (TASK-0191, RAI-56099, November 24, 2026)

Artifact `2VTZv1Hgon25in9YD2LExb`. Six rounds, in order.

1. Brief: explain an eight-PR stack, pair the diagrams with explanation and code or call-stack diffs, and "give me a feel for where we've removed whole categories of stuff versus where we've removed branches." Purpose: "make sure that it all visually checks out. That way I can just ask follow-up questions on specific areas." Ran `consider-contrast` on the page shape first.
2. "Make it 10 times better… think deeply about the most useful information for somebody who's coming in to review this… get all that information kind of just within reach… use my preferred styles," pulled from the Client Rewrite page. Then: "make sure that all of the images and diagrams open up in a view box that allows for panning and zooming." Result: the layer table as the spine, a popover per row, hover cards on PR links, deep links `#pr-N`, the carousel viewer.
3. Grouping: by category is right for what goes, how calls change and who notices, but "once we get to diagrams… I want to switch over to a PR-specific view," because the questions, the code-vs-description gaps and the unproven parts each listed every PR. The closing "what's left" section is "a really good section… what are the changes implied by everything we just did?" Split it into future work to capture versus legitimate gaps. And "avoid having this turn into a giant review document. This is just meant to motivate the review… a separate document… is the actual review."
4. Visuals: "The striping on the tables is just confusing. I don't like having color alteration going down the page… use padding, grouping, typography to indicate togetherness or separation." "These things are like a columnar layout, but they're not really a table because we don't have headings." "Color is just changing all over the place… banded columns on text color." And the red code-name lists (`FileAdapter · OplogPersistenceAdapter · file_migrations.py`): "for most people it just looks like random symbols and file names… either translate it into… a normal description of what's going on, or just not show it… ground it in what the user actually experiences or maybe a top level dev thing."
5. "Pick a single style for tables… The one that has a background color on the header and has horizontal lines looks the best… use that one everywhere." "We've got tons of horizontal lines just separating content. Let's get rid of all those… typography, grouping, padding, spacing… without adding lines all over the place."
6. "Use the anti-slop skills from my Byron Voice skill… pull down the latest version." Fixes were colon reveals, one "not X, but Y", an announcement sentence, jargon in parentheses, and an em dash in the viewer title.

Agent-side lessons from the same session:

- The built-in browser isn't signed in to claude.ai, so check the page through a local static server.
- The local copy needs its own `<meta charset>` and viewport meta; without them middots turn into mojibake and the phone check runs at 981px.
- A wide row of columns overlapped (size over reviewers) until checked at desktop width.
- The part nav highlighted the wrong part with an observer; a scroll check fixed it.
- Use a cache-busting query when reloading the local copy, or the screenshot shows the old version.

## Earlier asks that point the same way

- October 14 and 23, 2026 (plan viewer graphs): an expand control into a full-viewport modal with drag to pan and wheel to zoom; "allow for overpan so that I can place items from the far left edge of [the] graph on the… right edge of my screen"; then "add fit to graph and reset zoom."
- November 5, 2026 (map zoom): "when you zoom in really tight, the text is blurry, almost like it's an image… I really, really don't like the blurry text when I'm zoomed in." The template's viewer resizes the image rather than CSS-scaling it for this reason.
- November 19, 2026 (plan viewer images): an inline image is never taller than about 90% of the viewport; the full image is one click away.
- October 26, 2026: artifacts hold no unique facts. Durable findings go to PR bodies, the repository or the planning task, and the artifact links to them.
