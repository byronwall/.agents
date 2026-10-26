---
name: portfolio-content
description: Create or update content and static releases for Byron Wall's portfolio at /Users/byronwall/Projects/wall-portfolio. Use for project entries, blog posts, images, and building or publishing static copies of games, demos, and tools hosted on the portfolio.
---

# Portfolio Content

Use this skill for portfolio content and static releases.

For static copies, read [references/static-releases.md](references/static-releases.md). Build in the source project; publish the verified output through the portfolio.

## Site map

- Repo: `/Users/byronwall/Projects/wall-portfolio`
- Projects: `content/projects/*.mdx`
- Blog posts: `app/blog/posts/*.mdx`
- Game entries: `content/games/*.mdx`
- Hosted games: `public/games/<slug>/...`
- Public site: `https://byroni.us`
- Local images: `public/images/...`
- Shared content loader: `app/blog/utils.ts`
- Project index/detail pages: `app/projects/page.tsx`, `app/projects/[slug]/page.tsx`
- Blog index/detail pages: `app/blog/page.tsx`, `app/blog/[slug]/page.tsx`

## Content workflow

1. Make content edits in `/Users/byronwall/Projects/wall-portfolio`. Static source builds use the separate release workflow.
2. Inspect nearby MDX examples before writing. Match their frontmatter and tone.
3. Choose the target:
   - Project entry: create `content/projects/<slug>.mdx`.
   - Blog post or placeholder: create `app/blog/posts/<slug>.mdx`.
   - Game entry: inspect `content/games/*.mdx` and preserve its existing play URL.
4. Connect posts and projects whenever the relationship is known:
   - Inspect `content/projects/*.mdx` before creating or editing a post.
   - Add `project: <project-slug>` to the post frontmatter using the exact project filename slug.
   - Add a controlled `type`: `update`, `feature`, `debugging`, `experiment`, `tooling`, `failure`, `reflection`, or `reference`.
   - Do not guess a relationship. If it is unclear, leave `project` unset for later review.
   - When creating a project, check existing posts for obvious matches and backfill their `project` and `type` fields in the same change.
   - Project detail pages automatically use this metadata to render related-post cards; preserving the exact slug is therefore important.
5. Prefer concise content that can publish immediately. For placeholders, state what exists now and what will be expanded later.
6. Follow the validation and publishing rules below.

## Frontmatter

Project entries should normally use:

```mdx
---
title: "Project Name"
description: "One sentence description for project lists"
date: "YYYY-MM-DD"
publishedAt: "YYYY-MM-DD"
summary: "One sentence summary for metadata"
tags: ["Tech", "Category"]
image: "https://raw.githubusercontent.com/byronwall/repo/main/path/image.png"
status: "active"
repo: "https://github.com/byronwall/repo"
demo: "https://example.com"
---
```

Blog posts can be lighter:

```mdx
---
title: Post title
publishedAt: YYYY-MM-DD
summary: 'Short summary for metadata and previews.'
image: "/images/posts/slug/image.png"
project: project-slug
type: update
---
```

The parser is simple and line-oriented. Keep frontmatter values on one line. Use array syntax for `tags`.

Project metadata may also include `featured`, `package`, `docs`, and `logo`. Use explicit lifecycle values such as `active`, `shipped`, `paused`, `experimental`, or `archived` only when the source material establishes them; use a visible content placeholder instead of inferring status from a publication date.

## Images

- Prefer GitHub raw URLs for project screenshots when available:
  `https://raw.githubusercontent.com/byronwall/<repo>/<branch>/<path>`
- Look for likely images in the source repo first, especially `docs/`, `public/`, `assets/`, `screenshots/`, and README references.
- If a GitHub image is not easy to use, create or copy an image into the portfolio repo under:
  - `public/images/projects/<slug>/...` for projects
  - `public/images/posts/<slug>/...` for blog posts
- Reference local images with root-relative URLs such as `/images/projects/<slug>/screenshot.png`.
- If frontmatter `image` is omitted, the site uses the first markdown or HTML image in the MDX body as the thumbnail.

## Content Pattern

For project entries, usually include:

- One opening paragraph explaining what the project is.
- Links such as `Source: [byronwall/repo](https://github.com/byronwall/repo)` when known.
- An `## Interface` section with the main screenshot when available.
- `## How it works` and `## Highlights` sections for published entries.

For quick placeholders, keep it short:

- Frontmatter with title, date, publishedAt, summary, and tags if known.
- A paragraph describing the intended project or post.
- A source/demo link if available.
- A note about what will be added later only if useful.

## Validation and publishing

- Do not run a portfolio production build unless Byron explicitly requests that build. It disrupts the active development server.
- This restriction applies to the portfolio repository. Source-project builds are part of preparing a requested static release.
- Preserve running development servers. Use the existing portfolio server, normally `http://localhost:3010`, for relevant browser checks.
- Start a portfolio preview server only when requested and no suitable server is running.
- Use `pnpm exec tsc --noEmit` when needed. For content or copied assets, prefer direct checks and browser verification.
- Inspect Git status before editing. Preserve unrelated drafts and changes. Stage only files that belong to this request.
- Honor existing authorization. A request to publish or update the live release permits the required portfolio commit and push.
- A request to commit alone does not authorize publishing. A request to build a static copy alone does not authorize publishing.
- Without publishing authorization, prepare and verify the result first. Then ask whether to commit and push it.
- Before each commit, verify author and committer are `Byron Wall <byron@byroni.us>`.
- Do not verify the live site after pushing. The build and deploy pipeline is reliable, and a push to `main` reaches `https://byroni.us` within a few minutes. Stop after the push; do not poll the public URL.
- Report changed paths, validation, commit identifiers when applicable, and the live URL the change will appear at (or the local artifact path). Mention preview-server status when relevant.
