---
name: codex-visual-assets
description: Outsource raster visual assets to Codex and its built-in `imagegen` skill instead of drawing them by hand. Claude acts as art director (brief, style block, review, integration); `codex exec` does the generating. Use whenever a task needs static visuals such as hero or spot illustrations, empty-state art, textures, backgrounds, app/brand icon explorations, logo directions, icon-set grids, UI or product mockups, OG/social art, or reference comps for a redesign. Also the first step for new SVG icons and logos: generate raster mockups, pick one, then author the SVG against that reference. Not for charts, diagrams, or UI that should be built directly in HTML/CSS/SVG, and not for extending an existing SVG icon set that already has a clear style.
---

# Codex visual assets

Codex's `imagegen` skill (built-in `image_gen` tool, no API key needed) makes much better static visuals than anything Claude can draw in SVG or CSS. When a project needs visual assets, **don't hand-draw them and don't ship placeholders. Send them to Codex.**

Roles:

- **Claude, art director:** works out what assets are needed, writes the shared style block and prompts, runs Codex, looks at every output, picks the best, and wires the final files into the project.
- **Codex, illustrator:** generates images (and edits from reference images), then copies the results to the paths Claude names.

This came from the ComicBam (comic-book site) rebrand. A shared style block plus grid "contact sheet" prompts gave matching editor-tool icons, account icons, spot art, and an app icon in one pass. The chosen raster icon was then turned into a clean SVG logo with favicons.

## Invocation

```bash
codex exec -m gpt-5.6-sol --skip-git-repo-check -s workspace-write \
  -C "<project or output dir>" -o "<dir>/codex-last.txt" \
  'Use $imagegen (built-in image_gen tool). <prompt>. Copy the final PNG to ./tmp/assets/<name>.png. Reply with only the saved path(s).'
```

- **Always pass `-m gpt-5.6-sol`** (or another model from `~/.codex/models_cache.json` with `visibility: list`). The default model in `~/.codex/config.toml` gets rejected by the CLI with "model is not supported when using Codex with a ChatGPT account".
- Say `$imagegen` and "built-in image_gen tool" explicitly. Otherwise Codex may fall back to its CLI path, which needs `OPENAI_API_KEY`.
- Codex saves to `~/.codex/generated_images/<session>/exec-*.png`. **Always tell it where to copy the result** in the workspace. Never reference a file that only exists under `~/.codex`.
- One image takes about 30 seconds; a grid takes 1–2 minutes. For several assets, run several `codex exec` calls with `run_in_background`, each writing its own file. Don't use one huge prompt.
- Reference images: add `-i ref.png` (repeatable) and name each image's role in the prompt ("image 1 is the current logo, use it as a shape reference only").
- Ignore the stderr noise about skills that failed to load or descriptions that were shortened. Check the exit code and the output file instead.
- Keep candidates in an ignored folder (`./tmp/assets/`, `output/branding/`) until one is chosen. Only the final picks go into `public/` or `assets/`.

## Workflow

1. **Inventory.** List every asset needed: its purpose, where it shows, its size or aspect ratio, whether it needs a transparent background, and whether it ends up as SVG.
2. **Style block.** Write one paragraph and start every prompt with it, so the assets look like one set. Include:
   - the use-case slug (`logo-brand`, `ui-mockup`, `illustration`, …)
   - audience and mood
   - line weight as a percentage of width
   - fill rules (flat or gradient, texture)
   - shadow rules
   - an **exact hex palette**, and nothing outside it
   - the background color
   - "no text or letters unless specified", and any exact text written word for word in quotes
   - composition and padding
3. **Explore with contact sheets.** For icons, logos, and spot art, ask for a grid (for example "3×2 grid of 6 directions" or "4×2 grid of 8 tool icons") on a plain background with generous padding and equal visual weight. One sheet makes the set look consistent and lets you compare directions cheaply.
4. **Review it yourself.** `Read` every PNG. Check the subject, the palette, stray text or misspelled letters, consistent stroke weight, and whether it still reads at the size it will ship. Use `consider-contrast` when choosing between directions that are close. Show Byron the sheet when the choice is a matter of taste (brand, logo).
5. **Refine one.** Pass the chosen sheet back with `-i`. Say exactly which cell to use ("the BOTTOM-RIGHT rounded burst") and ask for one standalone, centered, final version. Make one targeted change per pass.
6. **Integrate.**
   - Copy finals into the project with clear names. Never overwrite an existing asset: version it instead (`hero-v2.png`).
   - Optimize for the web (`sips`, `cwebp`, or sharp) and set the real dimensions in markup.
   - Save a `prompts.json` record with file, prompt, and date next to the source assets so the set can be regenerated or extended.
   - Check the result in the running app, not only as a file.
7. **Report** the final paths, the prompts used, and which candidates were rejected and why.

## Icons and logos that ship as SVG

The raster image is the visual reference. The SVG is the deliverable.

1. Generate a contact sheet of directions, then refine the chosen one to a flat, high-contrast, single-subject image with no texture.
2. Write the SVG against that reference, with a clean `viewBox`, few paths, flat fills from the palette, and no embedded raster. Claude can write it, or a second `codex exec` with the reference attached (`-i`). Codex did this well for the ComicBam logo.
3. Render the SVG to PNG (`rsvg-convert`, `resvg`, or sharp) and **compare it side by side with the reference**. Fix the shapes and repeat until they match.
4. Check it at small sizes (16, 32, 48 px). Simplify details that turn to mush. Favicons often need a separate simplified SVG.
5. Derive the remaining files from the SVG: `favicon.svg`, `favicon.ico`, `apple-touch-icon.png` (180), manifest icons (192, 512, plus maskable with safe-zone padding), and update `theme-color` if needed.

For an existing icon library (Lucide, a repo icon set), match it in SVG directly and skip image generation.

## Mockups

For redesigns, generate 2–4 full-page or screen comps from a screenshot of the current UI (`-i current.png`, "keep the layout and content, restyle as …"). Use them as the direction reference, then build the real UI in code. Never ship a mockup image as the UI itself.

## Transparent assets

Ask for "a genuinely transparent background" and check the result with `sips -g hasAlpha file.png`. If there's no alpha, ask Codex to regenerate on a flat chroma-key color and run `~/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py`.

## Prompt reference

Codex's own prompting guides are worth skimming for hard cases:
`~/.codex/skills/.system/imagegen/references/prompting.md` and `sample-prompts.md`.
