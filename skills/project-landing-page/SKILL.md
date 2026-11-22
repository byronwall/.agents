---
name: project-landing-page
description: Build a landing page for one of Byron's programming projects, in the project's own repo, deployed to GitHub Pages by a GitHub Actions workflow, with the repo's website URL set to the new Pages address. Chooses the page type, sections and content from the project itself, and holds the first build to the bar the earlier `/10x` and `/100x` passes reached (Context Recorder, Planboard, Srcly, Visual Notes), so Byron does not have to steer it. Use when Byron says `/project-landing-page`, "give X its own landing page / home page / site", "a GitHub Pages site for X", "like the Draftably / explorEDA / Srcly sites", or asks which projects still need a landing page. Public repos only.
argument-hint: "<repo path or name> [-- audience, focus, or constraints]"
user-invocable: true
---

# Project landing page

Byron gave each of his tools a site in its repo: Context Recorder, Planboard, Srcly and Visual Notes on `byronwall.github.io/<repo>`, explorEDA and Draftably on their own domains. Each one went through a first build, a `/10x` pass and a `/100x` pass, with corrections between them. This skill holds what those rounds taught. Build to the final state on the first try.

Do not ask about scope. Infer the audience, page type and content from the repo, and record each call under **Decisions for you** in the PR. Ask only when one of these is true:

- The repo is private. GitHub Pages is for public repos only here. Stop and report.
- The repo already has a site or a custom domain that the new deploy would replace, and something links to paths you cannot keep.
- The only way to get screenshots is from Byron's real data.

## Inputs

- **Target:** a repo path under `~/Projects`, or a repo name. With no target, run `scripts/candidates.sh` and pick the public repo with the most recent commits and no Pages site. Say which one and why.
- **Focus (optional):** the audience or emphasis, such as "first-time user and portfolio demo" or "the depth, not a marketing splash". It overrides the defaults below.
- **Task ID (optional):** when a planning task such as `TASK-0057` is named, record status and a dated Updates bullet there.

## Compose with

- Always: `byron-ui-taste` and `10x/references/repeat-corrections.md` before any design work. With [references/quality-bar.md](references/quality-bar.md), they caught every defect on the llmly run.
- `write-byron-voice` for the hero lede and the "How I built it" section only. All other text follows ASD-STE100.
- Optional: `impeccable` (it is large) only when the project has no visual language of its own to borrow. `codex-visual-assets` for two or three style mockups in the same case.
- `pr-description` before the PR body. `portfolio-content` for the byroni.us project-page link at the end.

## Process

### 1. Ground (read, run, inventory)

- Read the README, AGENTS.md, DESIGN.md or PRODUCT.md, `docs/`, the changelog, and the entry points. Run the project the way a new user would.
- Write an inventory to `tmp/site/inventory.md`: every view, command, option, metric or API the site could show, each checked against the code. Each claim on the page must trace to this list.
- Check the repo state with `scripts/pages.sh status <owner/repo>`: visibility, the current Pages source, custom domain and website URL. If a legacy `gh-pages` branch exists, list what it serves (`git show origin/gh-pages --stat`) and keep every path that something links to.
- Read the byroni.us project page and posts for the project, if any. They hold the story for "How I built it". The slug is often not the repo name, so find it with `grep -ril <repo> ~/Projects/wall-portfolio`.
- Make sure `.gitignore` covers `tmp/` before you write there ([references/build-and-deploy.md](references/build-and-deploy.md), "Ignore files").

### 2. Choose the page type

Read [references/page-types.md](references/page-types.md). Pick the type from what the project can show without a server: a live demo, the tool's own output on its own repo, a screenshot tour, or a code-first library page. A server app whose frontend reads a few GET routes still gets a live demo, through a static API snapshot. Most sites mix two types. The hero is always the strongest real thing, never decoration.

### 3. Plan the sections for four visitors

Every site serves these four visitors. [references/sections.md](references/sections.md) has the catalog and the order.

1. **First-timer from a link:** what is it, why does it exist, is it worth it, how hard is it to try. All four answers are in or right under the first viewport.
2. **Docs reader:** finds any view, command or setting fast. Use search, anchors, and one section per item.
3. **Coding agent:** gets `llms.txt` and Markdown copies, or a short agent section with real commands.
4. **Portfolio reviewer:** sees who built it, how, and with what numbers, in a short "How I built it".

Weight the content to the project type. The defaults: about 60% user guide, 30% reference, 10% "How I built it". Cut every section that does not serve one of the four visitors. Shorter wins. Earlier first drafts lost half to two thirds of their length in the 10x pass, with no loss of content.

### 4. Choose the style

- Take the look from the product itself: its colors, its signature visual (a treemap, a timeline, a canvas), its DESIGN.md tokens. Do not copy a sibling site's look.
- Support dark mode with the OS setting.
- Pick the stack from [references/build-and-deploy.md](references/build-and-deploy.md): static `site/` with no build; static plus one build script in the repo's own language (the default for a non-Node repo); or Vite + SolidJS + TSX in `site/` with its own `package.json`.

### 5. Capture real screenshots

Follow [references/screenshots.md](references/screenshots.md). In short: use demo data only, use a capture script committed to the repo so a reshoot is one command, use WebP, and scrub local paths and user names.

### 6. Build

- Build the sections in order. Use real commands, real output and real code from the repo (import code with `?raw` so it must compile).
- Put no hand-typed number on the page when the build can compute it. Substitute numbers into the HTML at build time where there is a build ("Computed numbers" in build-and-deploy.md).
- Add the deploy workflow from [references/build-and-deploy.md](references/build-and-deploy.md). Add a short `site/` entry to the README and AGENTS.md, and make the README tagline match the hero.
- Add a favicon and a descriptive `<title>`. Capture `og.png` (1200 × 630) last, from the built site's own first viewport.
- Commit as you go on a `claude/` branch.

### 7. Self-review as the 10x pass

Before the PR, do the pass Byron would otherwise ask for. Score the page on the 10x lenses (job clarity, information architecture, density, disclosure, interaction, stability, fit and finish). Act as each of the four visitors and walk each job once. Fix the two lowest lenses. Then run [references/quality-bar.md](references/quality-bar.md) as a checklist. It is the list of defects the 100x passes found, and the first build must already pass it.

### 8. Verify

- Check at 1440, about 800, and 390 px, and in dark mode. `scrollWidth` must equal the window width at each size. There must be no console errors and no failed requests.
- Script the interactions: tabs and keys, lightbox open, zoom and close, copy buttons, deep links, and search.
- Check that every image, local link, `#anchor` and external link resolves.
- Run `grep -rn "/Users/\|/var/folders\|/home/$(whoami)" site/` on the source, the build output, and every JSON the site copies. Fix every hit. (A bare `$(whoami)` matches every `github.com/byronwall` link.)
- Serve the build under the Pages base path (`/<repo>/`) before you trust the links.
- Run the workflow's build commands locally. The PR cannot run the deploy, so say in Limits that the first deploy runs at merge.

### 9. Open the PR and turn on Pages

- Run `scripts/pages.sh enable <owner/repo>`. It sets the Pages source to GitHub Actions, or switches it from a legacy branch. It changes nothing on a private repo. The site goes live when the PR merges.
- Open one PR (or a `gh stack` when the work has clear separate layers) with screenshots attached by `gh --attach`: the first viewport at 1440 px, each main section, 390 px, and dark mode. Load `pr-description` first. List each judgment call under **Decisions for you**, and add a **Limits** section.
- Do not merge until Byron says so.

### 10. Ship (after Byron approves the merge)

- Squash-merge, so no commit with a local path reaches `main`.
- Watch the Pages run: `gh run watch` on the newest `pages.yml` run.
- Run `scripts/pages.sh homepage <owner/repo>`. It sets the repo's website to the Pages URL and prints the `homepage` fields in `package.json` or `pyproject.toml` that still point somewhere else. Update those in a follow-up commit.
- Load the live URL. Check the hero, images and one interaction. Report the live URL.
- Offer the byroni.us project-page link (`portfolio-content`) as the next step.

## Output

Reply with the PR link, the page type and style you chose and why, the sections and which visitor each serves, the Pages state, and **Decisions for you**. After shipping, give the live URL and the website URL now set on the repo.
