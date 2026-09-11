# Static copies and hosted releases

Use this workflow for games, demos, tools, and other static artifacts hosted on the portfolio.
Keep source code in its project. Treat the portfolio copy as generated output.

## Find the release target

1. Inspect source instructions, package scripts, and release documentation. Inspect Git status in both repositories.
2. Find the portfolio entry and its existing public URL. Preserve that URL when replacing a release.
3. Identify the source command, output path, portfolio destination, preview image, and verification command.
4. For a new release, choose a dedicated folder under `public/` that follows nearby examples.

Do not assume every artifact is a game. Inspect the relevant project or game metadata before adding a link.
Do not include unrelated source changes or portfolio drafts in release commits.

## Build a static copy

Run source-project scripts with pnpm. The portfolio production-build restriction does not prohibit these source builds.
Reuse an existing export command when available.

Choose the smallest suitable output:

- A single HTML file works well for small games and demos. Embed required scripts, styles, fonts, and images when practical.
- A static directory works well for larger apps. Include its entry HTML and all required assets.
- Use an existing static-export mode when the framework supports it. Do not convert the application's framework for publishing.

If no export command exists, add a repeatable source-project command when the requested scope permits it.
Keep export changes separate from the development configuration when possible.
Document the command, output, hosting path, and verification steps in the source project.
For repeated releases, prefer source scripts such as `build:static` and `verify:static` over one-off shell transformations.
These are suggested names, not required names.

Check the export's boundaries:

- A static host cannot run server routes, SSR, background jobs, or private API code.
- Do not embed secrets, private records, or credentials. Do not copy `.env` files or `node_modules`.
- Do not silently remove server-dependent features. Report the limitation and resolve the intended static behavior.
- Keep deliberate external dependencies visible. A static build is not necessarily usable offline.
- If an offline copy is requested, verify it without network access.
- Asset URLs must work under the portfolio subpath. Avoid root paths such as `/assets/` unless explicitly required there.
- Check direct navigation and reloads for nested routes. Do not assume the portfolio supplies an SPA fallback.
- Prefer file, hash, or exported routes when these meet the requested behavior.

## Verify and copy

1. Build into a source output directory before replacing the portfolio copy.
2. Test the generated output, not only the source development server.
3. Serve it at the intended URL depth. Check required assets, console errors, and the main interaction.
4. Check desktop and mobile layouts when the artifact supports both.
5. For downloadable HTML, also check `file://` loading when that use is part of the request.
6. Copy only the verified release files into the dedicated portfolio folder.
7. Remove obsolete generated assets only when their ownership is clear. Preserve unrelated files.
8. Refresh the preview image when the current image no longer represents the release.
9. Check the portfolio link and copied artifact through the existing preview server when available.

Do not rebuild the portfolio merely to copy files into `public/`.
Do not edit a generated bundle directly. Correct the source or export process and rebuild it.

## Commit, publish, and confirm

Follow the authorization and Git rules in `SKILL.md`.
Commit source changes when authorized. Commit the portfolio release separately and stage explicit paths.
Use the repository's configured publishing path. Do not create a new hosting service for an existing portfolio release.

After the push, download the public artifact and compare it with the verified output:

- For one file, compare SHA-256 hashes or exact bytes.
- For a directory, compare the entry HTML and required assets against a local file manifest.
- Use a release identifier in a query parameter if a cache could conceal the new release.
- Check the normal public URL after the new content appears. Verify links and critical interaction on the live site.

Allow up to five minutes for automatic publishing. Check every 15–30 seconds without blocking progress updates.
Retry read-only checks, not commits or deployment mutations.
If the files still differ, inspect available deployment status once and report the release as pending or failed.
Do not claim that a release is live merely because Git accepted the push.
Do not force-push, create empty commits, or change hosting configuration to overcome a delay.

## Existing example: Gunk Patrol

Confirm these paths and scripts before reuse:

| Item | Value |
| --- | --- |
| Source | `/Users/byronwall/Projects/gunk-patrol` |
| Build | `pnpm build:single` |
| Verify | `pnpm verify:single` |
| Release output | `dist/gunk-patrol.html` |
| Preview output | `dist/gunk-patrol-preview.png` |
| Portfolio release | `public/games/gunk-patrol/play.html` |
| Portfolio preview | `public/images/games/gunk-patrol/gameplay.png` |
| Entry | `content/games/gunk-patrol.mdx` |
| Public URL | `https://byroni.us/games/gunk-patrol/play.html` |

Run the build, then verification, from the source project. Copy the verified HTML into the portfolio release path.
Use the generated preview when an image refresh is needed. Leave unrelated portfolio content unchanged.
