# Page types

Pick the type from one question: what is the strongest real thing this project can show on a static page? Most sites mix a primary type with a second one.

| Type | Use when | Hero | Example |
|---|---|---|---|
| **Live demo** | The product, or a recording of it, runs in the browser with static files | The real product in a bounded frame, already loaded with demo data, with one obvious gesture to try | explorEDA (order book filters 500 rows to 167), Context Recorder (a 48 s session plays with marks, captions and inspector) |
| **Own output** | The tool makes a visual from code or data, and it can run on its own repo at build time | The tool's output on its own source, rendered as HTML from build-time JSON, with a switch and a hover readout | Srcly (a treemap of its own 1,136 files, recolor by complexity, commits or findings) |
| **Screenshot tour** | The app needs a server or database, and has a few main areas | Headline beside a tour: tabs, one screenshot per tab with numbered markers and matching notes | Visual Notes (7 tabs, markers highlight on hover, `#tour/<id>` deep links) |
| **Page-by-page reference** | The app has many views and the reader wants depth | First-timer answers on top, then one section per view with route, screenshot and a list of what each part does | Planboard (23 reference sections under the what / why / worth it / how hard blocks) |
| **Code-first** | A library, CLI or package with no UI of its own | The install line and a short real code sample or real command output, beside what it returns | explorEDA's React section (real files imported with `?raw`, the 3 props of the host boundary) |

## Decision order

1. Can it run statically? Use **Live demo**. A staged recording counts: build a fake demo app, record a session, and play it on the page.
2. Can the frontend run on saved API answers? Use **Live demo** with a static API snapshot (below). Ask this before you call an app server-only.
3. Does it make a picture from code or data? Use **Own output**, computed at build time from the project's own repo.
4. Server-only with 3 to 8 main areas? Use **Screenshot tour**.
5. Server-only with many views, or Byron asked for depth? Put **Page-by-page reference** below a short first-timer block.
6. No UI? Use **Code-first**, with real output from running it on a real input.

## Static API snapshot

Use this when the app has a server, but its frontend reads only a few GET routes (llmly: three JSON routes from a Flask app).

- At build time, run the app's own code on demo data and save each route's answer as JSON under the site.
- Add a small `demo-shim.js` that replaces `fetch` and answers `/api/*` from those files. When a route takes query params, filter and sort in the shim.
- Load the app's real frontend in the page, with the shim first. The hero is then the real product, and a visitor can click it.
- Pin the clock in the shim too (see screenshots.md), so "last 24 hours" views show the demo data.

## Live demo in a frame

- **Scroll trap:** the wheel over an iframe scrolls the app, not the page. When the app scrolls a long way, use a fixed-height frame or a "click to interact" overlay. Otherwise, name it under Limits.
- **Desktop-only app:** show the frame only at widths the app supports (for example 860 px and up). Below that, show a still of the same state that links to the full-window demo, and add a Limits line.

## Mixes that worked

- Live demo hero, then a gallery of the full app, then Agents and Install (Context Recorder).
- First-timer blocks, then the page-by-page reference (Planboard).
- Own-output hero, then the guide, reference generated from the code, and a short "How I built it" (Srcly).
- Tour hero, then Agents, then "How it's built" with real numbers (Visual Notes).

## Signs of the wrong type

- The hero is a static screenshot, but the product could run on the page, or on saved API answers.
- The first screen asks the visitor for data before it shows anything (the old explorEDA page).
- A marketing splash for a tool where Byron wants a working reference.
- A page of long text about a visual tool.
