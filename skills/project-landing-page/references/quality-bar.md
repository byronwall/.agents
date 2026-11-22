# Quality bar

The 10x and 100x passes on the earlier sites found these defects. The first build must pass every line. Check each one against the screenshots and the scripted checks, not against the code.

## First viewport (1440 × 900)

- [ ] The hero visual fits fully above the fold.
- [ ] The visitor can tell what it is, why it matters, and how to try it, with no scroll.
- [ ] The try-it command has a copy button, the requirement and the time, timed from a cold cache.
- [ ] The headline tracking is not tight. The lede stays under 68 characters a line.

## Length and structure

- [ ] Each section serves one of the four visitors. No section repeats another.
- [ ] No step cards, feature grids, stat tiles with no source, or repeated dark code blocks.
- [ ] The prose width is at most 68 characters. Paragraphs are short.

## Stability

- [ ] A tab change, mark change or hover readout never moves the content below it. Measure the position below the widget across every tab, at each width.
- [ ] Readout strips and legends have a fixed height.
- [ ] Copy buttons keep their width when they change to "✓ Copied".

## Screenshots and lightbox

- [ ] A click on a screenshot opens a full-size view that is fitted to the window on open, not cropped and not smaller than the inline image.
- [ ] A click zooms in at that point, to `min(2 × fit, max(1.5 × fit, 1))` of the fitted size (so a 2× capture caps near 1:1), and a drag pans. "Actual size" shows 1:1.
- [ ] Esc and a click outside close it. Focus moves to Close on open, stays in the dialog, and goes back to the image on close.
- [ ] Arrow keys step between images when there is more than one.
- [ ] The dialog bar names the open screenshot.
- [ ] Numbered markers do not cover the image on a phone. Use dots or a list there.

## Interaction and keyboard

- [ ] Tabs: left and right arrows, Home and End. Use roving `tabindex` and `aria-selected`.
- [ ] Deep links: `#tour/<id>` opens that tab, and the URL follows the selection.
- [ ] Search (if present): `/` focuses it. Arrows and Enter work, and the match is highlighted.
- [ ] The live demo has no scroll trap, or Limits names it. A desktop-only demo shows a still with a link on a phone.
- [ ] Media players: Space plays, a click on the timeline seeks and selects, and there is a fallback when the video cannot load.

## Responsive

- [ ] At 1440, 1100, 800 and 390 px, `document.documentElement.scrollWidth === innerWidth`.
- [ ] At about 800–1000 px, the hero headline moves above the visual. It never covers the legend or controls.
- [ ] At 390 px, the play buttons are icon-only, tabs wrap, nothing clips, and tool arguments wrap on their own line.
- [ ] Long URLs and commands in code do not break mid-word. They scroll inside their block.

## Code and text

- [ ] Code blocks have normal line height, not double spacing.
- [ ] Markdown shown as text: headings and bold in the text color, markup dimmed, and a file bar with the name and Copy above the code, so Copy covers no text.
- [ ] Each number on the page comes from the build or from a source you can name.

## Theme and assets

- [ ] Dark mode follows the OS and the hero still reads. Check every section in dark mode.
- [ ] `og.png` shows the real hero. The favicon and apple-touch-icon are present. The `<title>` describes the page.

## Privacy

- [ ] `grep -rn "/Users/\|/var/folders\|/home/$(whoami)" site/ <build output>` finds nothing. (Do not grep for the bare user name: it matches every `github.com/byronwall` link.)
- [ ] No local paths, user names, real notes, real recordings or real sign-ins in any image, JSON or HTML.
- [ ] Demo names are fictional, and a real first name in a seed is renamed.

## Deploy

- [ ] The site works under `/<repo>/`. Assets use relative paths or the Vite `base`.
- [ ] GitHub Pages serves `404.html` for unknown paths. A single-page app needs a copy of `index.html` there, or a real 404 page.
- [ ] Every path the old site served still resolves, or the PR says what goes away.
