# Sections

Use these in this order. Leave out any section that has nothing real to say for this project. Each section names the visitor it serves: **F** first-timer, **D** docs reader, **A** coding agent, **P** portfolio reviewer.

## 1. Header (all)

- The name and icon, then a few links: Docs (if any), Agents (if any), GitHub. Add `/` search when the site has docs or more than about 10 sections.
- Make it sticky, full window width, with a hairline only after the visitor scrolls.
- Do not repeat in the header the section list that a contents rail or path bar already shows.

## 2. Hero (F, P)

- One headline that says what the product does, in the user's terms. Then at most two sentences. Keep the lede to 62–68 characters a line.
- The strongest real thing (see page-types.md), above the fold at 1440 × 900.
- The primary action and the try-it cost together: the command with a copy button, the one requirement ("Node 22.15+"), and the time. Time the command from a cold cache (for example `uvx --no-cache <tool> --help`) and use that number. Do not guess. Add a second action only for the source or the tour.
- Quick facts the visitor needs to decide: version, platforms, supported languages, "no account, no database".

## 3. Why it exists (F)

- The problem in a few lines, from the README or Byron's posts.
- An optional short "Without it / With it" contrast. Use no feature-card grid.

## 4. How it works, or how a day goes (F)

- 3 to 5 steps with tight crops of real screens. Make one step a real live moment where you can (a toast, a file change, a filter result).

## 5. Is it worth it? (F)

- **Worth it if** and **Skip it if**. Be honest about limits: platform, single user, no phone, needs a server.
- What it asks of you (a file format, a runtime, your own sign-ins) and what it never does (send data, run without consent).

## 6. How hard is it to start? (F)

- Levels with times: a 2-minute demo, a 10-minute real setup, then integrations as needed. State what each level needs.
- If there is no release, say "build from source" and give the exact commands.

## 7. Tour or guide (D, F)

- One part for each view or area: a screenshot, then a list of what each part shows and what you can do there. Use notes beside the shot, and numbered markers only on the one shot that teaches the visual language (screenshots.md).
- Workflows as short recipes, such as "find the refactor" or "review a PR".
- Give each part an anchor. Make the tab or section state follow the URL.

## 8. Reference (D, A)

- CLI options, configuration, metrics, API routes, keyboard shortcuts. Generate these at build time from the code, a catalog, or `--help` output wherever possible.
- Give each row an anchor (`#metric-churn_lines`) so a chat or report can link it.

## 9. For coding agents (A)

- Include this when agents use the tool (a CLI, an MCP server, a skill, a file format). Show the real loop with commands, the stdout contract, and the repo's skill.
- Publish `llms.txt` (an index), `llms-full.txt` (everything), and a Markdown copy beside each docs page, with a `rel="alternate"` link. A one-page site needs only `llms.txt`.

## 10. Install (F, D)

- Show the commands with copy buttons, every requirement, and the alternative path (clone and run). Make this match the README order.

## 11. How I built it (P)

- About 10% of the page, in Byron's first-person voice (`write-byron-voice`). Say why it exists, give an architecture diagram, real numbers (commits, files, notes), and two or three lessons.
- Link the byroni.us project page and posts. Each claim comes from those or from the code.
- List the source for each first-person claim in the PR. When the sources are thin (one post, the README, the git log), keep the section short and factual. Do not invent first-person reasons or feelings.

## 12. Footer

- Repo, license, docs, the byroni.us project page, and the date or commit the page reflects.

## Do not add

- Step cards, feature-card grids, testimonial blocks, stat tiles with no source, or a pricing section.
- Big dark code blocks repeated in each section. Use one panel style for code and output.
- A section that repeats another section in other words.
