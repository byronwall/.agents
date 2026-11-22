# Build and deploy

## Stack

| Choose | When | Layout |
|---|---|---|
| **Static** | The page needs no data at build time: a few interactions in plain JS, screenshots, a recorded demo | `site/index.html`, `site/site.css`, an optional `site/*.js`, `site/images/`. Deploy with `templates/pages-static.yml`. Context Recorder and Planboard use this. |
| **Static + one build script** | The page is static, but it needs data the repo computes: demo API answers, page numbers, a commit count. Use this for a non-Node repo. | `site/index.html` and friends, plus `site/scripts/build_*` in the repo's own language (Python: `site/scripts/build_demo.py`). The build writes into an ignored folder such as `site/demo/`. Deploy with `templates/pages-static.yml` and turn on its build step. llmly uses this. |
| **Vite + SolidJS + TSX** | The hero or reference is computed from the repo at build time, the site has docs pages, search, or `llms.txt`, or it imports real code with `?raw` | `site/package.json` (pnpm), `site/vite.config.ts` with `base: process.env.SITE_BASE ?? "/"`, `site/src/`, `site/public/`, `site/scripts/` (capture, prerender), `site/tests/`. Deploy with `templates/pages-vite.yml`. Srcly and Visual Notes use this. |

- Write the capture and check scripts in the repo's own toolchain. A Python repo gets `site/scripts/capture.py` and `check_site.py`, run with `uv run --with playwright==<v> --with pillow python ...` (pin `<v>` as screenshots.md says). Do not add a `package.json` to a repo that has none only for the site.
- Keep the site apart from the app. Its own `package.json` in `site/` means app dependencies never touch it.
- Prerender to static HTML when the site is a SolidJS app, so the content is in the HTML for search engines and agents.
- Add one Playwright check (`site/tests/site.spec.ts`, or `site/scripts/check_site.py` in a Python repo). It checks that the page renders its sections, that every image, local link and `#anchor` resolves, and that the main interaction works. Run it locally before the PR. Add it to CI only when the repo already installs Playwright browsers there.
- Copy the template to `.github/workflows/pages.yml`. Check the action versions with `gh api repos/<action>/releases/latest --jq .tag_name` and use the latest major, so GitHub does not warn about an old Node runtime.
- Confirm that the major tag exists before you use it: `gh api repos/<action>/git/ref/tags/v<N>`. Some actions publish only full versions (`astral-sh/setup-uv` has no `v8`+ major tags). Pin the full version then. The PR cannot run the deploy, so a bad tag shows up only after the merge (llmly's first deploy failed this way).

## Computed numbers

The page shows no hand-typed number that the build can compute. Pick one way:

- **Vite, or a static build step:** substitute the numbers into the HTML at build time. Crawlers and agents see the real values. Prefer this.
- **Static with no build:** fill `data-stat` spans from a JSON file in JS. The HTML keeps fallback values that can go stale, and crawlers see them. Use this only when the site has no build step at all.

## Ignore files

- Make sure `.gitignore` covers `tmp/` and any build output under `site/`.
- Before you append, check that the file ends with a newline (`tail -c1 .gitignore | xxd`). If it does not, add one first. Otherwise the last line joins the new one, and `.env` becomes `.envtmp/`.

## Base path and domain

- Project Pages serve at `https://<owner>.github.io/<repo>/`. GitHub does not redirect it when the repo is renamed. Update every link after a rename.
- Static sites: use only relative asset paths (`images/x.webp`, not `/images/x.webp`).
- Vite: set `base` from `SITE_BASE`. Preview locally with `SITE_BASE=/<repo>/ pnpm build && pnpm preview`, and check the links there.
- Custom domain: keep `base: "/"`, add `site/public/CNAME`, and set the domain in the Pages settings. Do this only when Byron names a domain.

## Pages settings (scripts/pages.sh)

```bash
~/.agents/skills/project-landing-page/scripts/pages.sh status   owner/repo   # visibility, Pages source, domain, website
~/.agents/skills/project-landing-page/scripts/pages.sh enable   owner/repo   # source -> GitHub Actions (create or switch)
~/.agents/skills/project-landing-page/scripts/pages.sh homepage owner/repo   # website -> Pages URL, after the first deploy
```

- `enable` refuses a private repo.
- It creates Pages with `build_type=workflow`, or switches a legacy `gh-pages` source with a `PUT`. A switch adds `main` to the `github-pages` environment's branch rules. The script prints those rules, so you can confirm `main` is there.
- The PR cannot prove the deploy: the workflow deploys only from `main`, and the `github-pages` environment allows only `main`. Run the workflow's build commands locally, and say in Limits that the first deploy runs at merge.
- The first deploy runs when the PR merges. If it does not start, run `gh workflow run pages.yml --ref main`.
- After the switch from `gh-pages` is live, the old branch can go. Offer that to Byron, and do not delete it yourself.

## Ship

```bash
gh pr merge <n> --squash --delete-branch
id=$(gh run list --workflow pages.yml --branch main --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$id" --exit-status
~/.agents/skills/project-landing-page/scripts/pages.sh homepage owner/repo
curl -sI https://<owner>.github.io/<repo>/ | head -1
```

The `homepage` step sets the GitHub website field. It also prints the `homepage` field in `package.json` and the URLs in `pyproject.toml`. Change any that point to an old URL or to nothing.
