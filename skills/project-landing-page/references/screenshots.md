# Screenshots and demo data

## Data

- Use demo data only. Never use Byron's real planning folder, notes, recordings, repos with private code, or sign-ins.
- Give the demo data a goal, not only a size: the first screen must show every item in the product's legend (llmly: sub-agent lines, compaction marks, all cache colors, every source, a non-zero cost). Check the first screenshot against the legend, and tune the generator until it matches. Read `10x/references/repeat-corrections.md` on demo data too.
- Use the project's own demo source first: an `examples/` workspace, a fixture, a seed script, a `dev:demo` command, or a demo database (such as `visual_notes_audit_portfolio_demo`). If none exists, build a small fictional one (Context Recorder used a fake shop app and a staged session with `say` narration).
- For a developer tool, run it on its own repo. That is real and public.
- Hide or crop the parts that leak real data: a Recent list, a dev toolbar, an account menu, a cloud list from other machines (point the cloud at nothing).
- Replace the local user name in API responses and file paths before capture.

## Capture script

- Commit a capture script: `site/scripts/capture.mjs` (Node), or `site/scripts/capture.py` (Python, through `uv run --with`). It starts the app on the demo data, sets the state for each shot, and writes WebP files to `site/images/` or `site/public/shots/`.
- Use Playwright or Chrome for Testing. When you launch Chrome yourself, pass `--use-mock-keychain --password-store=basic`.
- Pin Playwright to a browser build that is already cached. List `~/Library/Caches/ms-playwright`, then pick the Playwright version whose `browsers.json` names a cached build (Python `playwright==1.58.0` uses `chromium_headless_shell-1208`). Download a browser only when no version matches.
- Capture at a 2× device scale. Use 1440 × 900 for full screens, and tight crops for step images.
- Pin the clock and the file dates so a reshoot gives the same images:
  - **Browser clock:** use Playwright `page.clock.install({ time })`, or, for a live demo, replace `Date` in the page with a subclass offset to a fixed day.
  - **Server clock:** anchor the demo data to a fixed date, then use the app's absolute-window URL params, or answer from a static API snapshot (page-types.md) with the browser clock pinned.
- Capture `og.png` (1200 × 630) last, from the built site's own first viewport.
- Put the reshoot command and how long it takes in `site/README.md`.

## Video and live demos

- Serve local previews with a server that supports Range requests (`pnpm dlx http-server@14.1.1`). Python's `http.server` cannot seek video.
- Before a commit, check every JSON file you copy into `site/` for local paths. One commit with a local path means the PR must squash-merge.

## Markers

- Put numbered markers on the one shot that teaches the product's visual language (a chart card, a canvas). For full-window tour shots, use notes beside the shot. Many markers on many large shots are fragile.
- Number the markers on the shot to match the list beside it. Hover on a list item highlights its marker.
- Store marker positions as percentages, and note in `site/README.md` that a reshoot means a recheck.
