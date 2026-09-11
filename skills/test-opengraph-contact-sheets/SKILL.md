---
name: test-opengraph-contact-sheets
description: Render, collect, compare, and visually verify representative OpenGraph or social-card image variants as a labeled contact sheet. Use when creating or changing OG image routes, metadata-image templates, dynamic social previews, `ImageResponse` output, or branded share cards in any web repository, especially when several content types, fallback states, titles, descriptions, or source-image ratios must remain coherent.
---

# Test OpenGraph Contact Sheets

Test the image response itself, not a mockup or a screenshot of the browser's raw-image viewer. Produce a small visual regression set that makes repeated layout failures obvious.

## Workflow

1. Inspect the repository's metadata and OG-image pipeline. Identify the real image endpoint or generated files, expected dimensions, and meaningful template branches.
2. Choose the smallest representative matrix. Usually include:
   - the site or index default;
   - one content item with featured artwork;
   - one fallback without artwork;
   - one long title or description;
   - one source image with a substantially different aspect ratio, when relevant.
3. Render each case through the production code path. Keep inputs deterministic and record the URL or command used.
4. Verify every response before comparison:
   - successful image response;
   - expected MIME type;
   - expected natural dimensions, commonly `1200 × 630`;
   - nonzero source-image dimensions;
   - no relevant server or browser errors.
5. Collect the raw rendered PNG or JPEG assets. Avoid treating a screenshot of a scaled, centered, or cropped raw-image viewer as the source artifact.
6. Assemble the collected files into a labeled contact sheet with `scripts/build_contact_sheet.py` when Pillow is available. Otherwise use an equivalent repository-native image tool.
7. Review the set at contact-sheet scale, then open individual images for detail. Check:
   - title wrapping and hierarchy;
   - description length and clipping;
   - shared gutters and card geometry;
   - image containment versus intentional crop;
   - fallback consistency;
   - footer, author, logo, and portrait alignment;
   - missing, stale, or format-incompatible assets.
8. Fix the template or asset pipeline, rerender the same matrix, and replace the contact sheet. Do not accept a fix based only on source inspection.

## Browser asset collection

When direct HTTP download is unavailable but the images render in a browser, create a temporary localhost-only page containing the endpoint variants as ordinary `<img>` elements. Confirm their `naturalWidth` and `naturalHeight`, then use the browser's observed asset inventory or network tooling to export the image responses themselves.

Remove the temporary page after capture unless the repository benefits from a permanent preview gallery.

## Build the sheet

Run:

```bash
python scripts/build_contact_sheet.py \
  --item "Site default=/tmp/og-default.png" \
  --item "Article with image=/tmp/og-article.png" \
  --item "Fallback=/tmp/og-fallback.png" \
  --output /tmp/og-contact-sheet.png
```

Use `--columns`, `--tile-width`, and `--title` only when the defaults do not fit the review set. The script preserves each image's aspect ratio and refuses empty or unreadable inputs.

## Handoff

Include the contact sheet inline when the client supports images. Report the cases covered, source dimensions, failures found, fixes made, and validation performed. Keep individual full-resolution renders when a reviewer may need to inspect typography or cropping.
