# Markup artifact

The markup artifact shows the review on top of the real resume page. Each reviewed line gets a highlight and a numbered pin. A click opens a popover with the note. A side column holds the main finding, the priority key, the section order, and a list of questions to copy. Byron called this layout "excellent" and "nearing perfect" (Nov 2026). Do not redesign it; fill it with a new review.

## Make one

1. Get a PDF. For a DOCX, convert it first: `soffice --headless --convert-to pdf --outdir <scratch> resume.docx`.
2. Set up PyMuPDF once, in a cached venv:

   ```sh
   V=~/.cache/review-resume/venv
   [ -x "$V/bin/python" ] || { python3 -m venv "$V" && "$V/bin/pip" -q install pymupdf; }
   ```

3. Extract the page into a scratch folder:

   ```sh
   "$V/bin/python" -I ~/.agents/skills/review-resume/scripts/extract.py resume.pdf <scratch>/markup
   ```

   The script blanks phone numbers and emails in the image and leaves their line out of `lines.json`. It prints every line with an index, and every wrapped item with the word count of its last line, marking `DANGLING` at 3 words or fewer. It covers page 1 only and warns when there are more pages.
4. Do the review with the rubric, then write `<scratch>/markup/review.json` (format below). Point each note at line indices from step 3.
5. Build and publish:

   ```sh
   python3 -I ~/.agents/skills/review-resume/scripts/build.py <scratch>/markup <scratch>/markup/review.json <name>-resume-markup.html
   ```

   The build checks the notes and stops with a list of errors (bad line range, missing tier, proposal over 14 words). Write the HTML in the session's working folder. Publish it with the Artifact tool, `icon: "document"`, and a one-sentence description. The artifact is private; tell Byron the candidate can't open it until he shares it.
6. Look at it once in a browser at about 1440 px wide with one popover open (serve the folder and open `#n1`). Fix what you see, rebuild, and republish. Don't loop.

## review.json

```json
{
  "meta": {
    "name": "Jordan Lee",
    "first": "Jordan",
    "readFirst": [
      { "b": "Overclaiming is the main issue.", "text": "\"Led\" and \"owned\" claim more than the bullets show." },
      { "text": "5 items wrap to a second line. A wrap is not fatal, but each one here comes from filler." }
    ],
    "order": {
      "now": ["Summary", "Skills", "Projects", "Education", "Jobs"],
      "better": ["Summary", "Education", "Projects", "Jobs", "Skills"],
      "moved": ["Education", "Skills"]
    }
  },
  "notes": [
    {
      "at": [12, 13], "s": "revise", "pr": "first",
      "t": "\"Shipped\" overclaims", "ctx": "Vision project",
      "w": "The model trained on 60 images. \"Built\" is accurate and still strong.",
      "p": ["Built real-time face recognition for live video in Python and OpenCV."],
      "q": "Did anyone besides you use it?"
    },
    { "at": [19, 19], "s": "keep", "t": "Specific and honest" }
  ]
}
```

Meta fields:

- `name` (required): shown in the title. `first`: used in "Questions for <first>".
- `readFirst`: one to three short paragraphs. The first one names the main issue. Include one sentence on wraps, and name any dangling line.
- `order`: optional. Leave it out when the section order is already right. `moved` colors those names in the "Better" row.

Note fields:

- `at`: `[first, last]` line indices, inclusive. Cover the whole item, both lines of a wrapped bullet included. A heading line with its date is one index; the date is a separate index on the same row, so include it when the note is about the date.
- `s`: the action — `cut`, `clarify`, `revise`, `move`, or `keep`. It shows as a small gray label.
- `pr`: the priority tier — `first`, `next`, or `opt` (see the rubric). Required unless `s` is `keep`. The tier sets the color.
- `t`: the title. Name the problem in six words or fewer ("\"100% readiness\" can't be checked").
- `w`: optional. One or two sentences on why.
- `p`: optional proposals. Each one is a single line of 14 words or fewer. Two entries mean "split into two bullets". Set `"long": true` only for a summary paragraph; it then shows "2 lines" instead of a word count.
- `q`: optional. One question for the candidate, tied to this line.
- `ctx`: a short label for the line ("Lab assistant"). The copied question list uses it, so write it for the candidate.

Order the notes top to bottom. The note number is its position.

## Fixed design choices

Byron tuned these. Keep them.

- Pins sit in a gutter left of the page, never on the text. On phones they become color ticks.
- The note opens in a popover anchored under its highlight (or above it when there's no room). On phones it is a bottom sheet. Only one is open. Esc, ×, or an outside click closes it. ← and → step through the visible notes, and the selection is kept in the URL (`#n7`).
- The priority tier sets the color and weight: Do first is red and filled, Do next is amber, Optional is a dashed outline, Keep is a thin gray outline. The legend at the top filters by tier.
- No line-wrap marks or word counts on the page. Mention wraps and dangling lines in the note text and in "Read first" instead. (Byron removed on-page wrap marks.)
- The proposal box shows its word count and a copy button.
- The phone number and email are blanked in the image before publishing.
