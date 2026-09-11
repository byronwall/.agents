---
name: webpage-review-and-redesign
description: Use when the user provides a running URL and asks for a detailed webpage critique, UX/UI review, landing page audit, conversion review, scoring, redesign concepts, or generated mockup improvements. Captures desktop and mobile screenshots with Playwright, extracts page gist and structure, scores key design dimensions, and uses image generation for 3-4 improved mockups.
---

# Webpage Review and Redesign

Use this skill when the user provides a URL and asks for a critique, UX review, design review, landing page review, website audit, conversion analysis, or improved visual mockups.

The expected result is a detailed, evidence-based review of the running page plus 3-4 redesign directions and generated mockups when image generation is available.

## Required Capabilities

- Playwright MCP or equivalent browser automation.
- Screenshot capture.
- Screenshot-aware visual reasoning.
- Image generation skill or image generation tool for mockups.

If image generation is unavailable or fails, complete the review and provide mockup-ready redesign prompts instead.

## Inputs

Required:

- A URL to review.

Optional context to incorporate:

- Target audience.
- Business goal.
- Brand constraints.
- Competitors.
- Desired design style.
- Focus area: conversion, clarity, accessibility, branding, mobile UX, or another priority.
- Whether to preserve the current visual identity or explore a larger redesign.

## Workflow

### 1. Normalize and Validate the URL

- Trim whitespace.
- Add `https://` if the URL has no protocol.
- Reject empty, obviously invalid, or unsupported URLs.
- Do not bypass login, paywalls, CAPTCHA, or access controls.
- Avoid interacting with pages that require login unless the user explicitly provides access context.

Example normalization:

```ts
function normalizeUrl(input: string): string {
  const trimmed = input.trim();
  if (!trimmed) throw new Error("URL is required.");
  return /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
}
```

### 2. Capture the Page

Use Playwright MCP to gather visual and textual evidence.

Recommended viewports:

```ts
const desktopViewport = { width: 1440, height: 1200 };
const mobileViewport = { width: 390, height: 844 };
```

Required screenshots:

- Desktop above-the-fold screenshot.
- Desktop full-page screenshot.
- Mobile above-the-fold screenshot.
- Mobile full-page screenshot.

Capture flow:

1. Navigate to the normalized URL.
2. Wait for DOM content loaded.
3. Attempt to wait for network idle; continue if it times out.
4. Dismiss obvious cookie banners or popups only if they block the page.
5. Capture desktop top and full-page screenshots.
6. Resize to mobile viewport.
7. Capture mobile top and full-page screenshots.
8. Evaluate page JavaScript to extract structured content.
9. Collect console errors and basic technical signals.

Do not endlessly wait for analytics, ads, chat widgets, or other third-party scripts.

### 3. Extract Compact Page Data

Extract a compact representation of the page. Do not dump the full DOM.

Required capture shape:

```ts
interface CaptureOutput {
  url: string;
  finalUrl: string;
  title: string;
  metaDescription?: string;
  headings: { h1: string[]; h2: string[]; h3: string[] };
  navItems: string[];
  ctas: string[];
  formFields: string[];
  visibleTextSnippets: string[];
  screenshots: {
    desktopTop: string;
    desktopFull: string;
    mobileTop: string;
    mobileFull: string;
  };
  technicalSignals: {
    consoleErrors: string[];
    brokenImagesCount?: number;
    hasHorizontalScrollMobile?: boolean;
    pageLoadNotes: string[];
  };
}
```

Use this extraction script as the default:

```js
(() => {
  const text = (node) => node?.textContent?.trim().replace(/\s+/g, " ") ?? "";
  const pickTexts = (selector, limit = 30) =>
    Array.from(document.querySelectorAll(selector))
      .map(text)
      .filter(Boolean)
      .slice(0, limit);

  const getMeta = (name) =>
    document.querySelector(`meta[name="${name}"]`)?.getAttribute("content") ??
    document.querySelector(`meta[property="${name}"]`)?.getAttribute("content") ??
    undefined;

  const ctaSelector = [
    "button",
    "a",
    "input[type='button']",
    "input[type='submit']",
    "[role='button']",
  ].join(",");

  const ctas = Array.from(document.querySelectorAll(ctaSelector))
    .map((el) => {
      if (el instanceof HTMLInputElement) return el.value?.trim() ?? "";
      return text(el);
    })
    .filter(Boolean)
    .filter((value) => value.length <= 80)
    .slice(0, 40);

  const formFields = Array.from(document.querySelectorAll("label, input, textarea, select"))
    .map((el) => {
      if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
        return el.placeholder || el.name || el.id || "";
      }
      if (el instanceof HTMLSelectElement) return el.name || el.id || "";
      return text(el);
    })
    .filter(Boolean)
    .slice(0, 40);

  const images = Array.from(document.querySelectorAll("img"));
  const brokenImagesCount = images.filter((img) => {
    return img instanceof HTMLImageElement && img.complete && img.naturalWidth === 0;
  }).length;

  return {
    finalUrl: window.location.href,
    title: document.title,
    metaDescription: getMeta("description") ?? getMeta("og:description") ?? undefined,
    headings: {
      h1: pickTexts("h1", 20),
      h2: pickTexts("h2", 30),
      h3: pickTexts("h3", 30),
    },
    navItems: pickTexts("nav a, header a", 30),
    ctas,
    formFields,
    visibleTextSnippets: pickTexts("h1, h2, h3, p, li", 60).filter(
      (value) => value.length > 20,
    ),
    technicalSignals: {
      brokenImagesCount,
      hasHorizontalScrollMobile: document.documentElement.scrollWidth > window.innerWidth + 8,
    },
  };
})();
```

### 4. Create the Page Gist

Infer from screenshots and extracted data:

- What the page appears to be.
- Likely audience.
- Primary conversion/action.
- Main CTA.
- Sections present.

Keep this concise and specific.

```ts
interface PageGist {
  summary: string;
  audienceGuess: string;
  primaryIntentGuess: string;
  primaryCtaGuess: string;
  notableSections: string[];
}
```

### 5. Critique and Score the Page

Review desktop screenshots, mobile screenshots, extracted page data, and user context.

Feedback must be:

- Specific and evidence-based.
- Balanced and practical.
- Design-oriented.
- Clear enough for a product/design team to act on.

Avoid generic feedback such as "make it more modern" or "improve the design." Prefer concrete observations tied to visible evidence.

Score every dimension from `0` to `10`:

| Score | Meaning |
|---:|---|
| 0-2 | Poor. Major usability, clarity, or credibility issues. |
| 3-4 | Weak. Useful elements exist, but significant issues remain. |
| 5-6 | Average. Functional but not especially compelling or polished. |
| 7-8 | Good. Clear and usable with room for improvement. |
| 9-10 | Excellent. Strong, polished, clear, and effective. |

Required dimensions:

- `visualHierarchy`: Does the page guide the eye through priority content?
- `valueProposition`: Is the main offer or purpose immediately clear?
- `ctaEffectiveness`: Are primary actions clear, prominent, and persuasive?
- `layoutSpacing`: Do spacing, alignment, and composition feel intentional?
- `readability`: Are typography, contrast, and density easy to consume?
- `trustCredibility`: Does the page feel legitimate, polished, and reassuring?
- `accessibility`: Does the design appear usable for differing needs?
- `mobileFriendliness`: Does the page work well on small screens?
- `brandConsistency`: Do visuals, tone, and interactions feel cohesive?
- `overallUx`: Holistic usability, clarity, polish, and effectiveness.

Use these weights unless the user asks for a different focus:

```ts
const dimensionWeights = {
  visualHierarchy: 1.0,
  valueProposition: 1.2,
  ctaEffectiveness: 1.0,
  layoutSpacing: 0.9,
  readability: 1.0,
  trustCredibility: 0.8,
  accessibility: 1.0,
  mobileFriendliness: 1.0,
  brandConsistency: 0.7,
  overallUx: 1.3,
};
```

Round the weighted overall score to one decimal place.

### 6. Generate Redesign Concepts

Create exactly 4 concepts unless the user asks for a different count.

Default concepts:

1. **Polished Evolution**: Preserve brand direction while improving spacing, hierarchy, CTA prominence, and readability.
2. **Conversion-Focused Landing Page**: Optimize hero, proof, objections, and CTA flow.
3. **Content Clarity Redesign**: Improve information architecture and scanability.
4. **Premium Modern Refresh**: Push visual polish, trust, typography, and rhythm further.

Each concept must include:

- `id`
- `name`
- `goal`
- `styleDirection`
- `layoutChanges`
- `contentChanges`
- `ctaChanges`
- `imagePrompt`

Concept rules:

- Keep the same website/business context.
- Preserve important brand cues unless clearly harmful.
- Make the concepts distinct.
- Do not invent unrelated products, services, or audiences.

### 7. Generate Mockups

Generate one mockup per redesign concept.

Default count: 4 mockups. Acceptable count: 3-4 mockups if constrained.

Use the original desktop screenshot as visual reference, plus the full-page screenshot and critique recommendations when useful.

Prompt template:

```txt
Create a high-fidelity desktop website mockup redesign for the referenced webpage.

Use the provided screenshot as the visual reference for the current site.
Preserve the site's general business/domain context, but improve the design.

Concept name:
{{concept.name}}

Goal:
{{concept.goal}}

Style direction:
{{concept.styleDirection}}

Required layout changes:
{{concept.layoutChanges}}

Required content changes:
{{concept.contentChanges}}

Required CTA changes:
{{concept.ctaChanges}}

UX goals:
- Improve clarity of the value proposition.
- Improve visual hierarchy.
- Improve spacing and readability.
- Make CTAs more prominent.
- Modernize the visual design.
- Improve trust and usability.
- Keep the page realistic and production-ready.

Output requirements:
- High-fidelity landing page mockup.
- Desktop website view.
- Light theme unless the reference site is clearly dark.
- Polished typography.
- Strong section hierarchy.
- Realistic UI.
- No unrelated company, product, or audience.
```

Optional mobile mockup prompt:

```txt
Create a high-fidelity mobile website mockup redesign for the referenced webpage.

Use the provided mobile screenshot as the visual reference.
Preserve the business context, but improve mobile clarity, scanability, CTA visibility, spacing, and readability.

Output a realistic mobile webpage design.
```

## Review Output Shape

Use this structure in the final response:

1. Page gist.
2. Overall score.
3. Score table.
4. What is working well.
5. What needs improvement.
6. Priority recommendations.
7. Redesign concepts.
8. Generated mockups or mockup-generation failure note.

Recommended Markdown:

```md
## Page Gist

{summary}

- Audience: {audienceGuess}
- Primary action: {primaryIntentGuess}
- Main CTA: {primaryCtaGuess}

## Overall Score

{overallScore}/10

## Ratings

| Dimension | Score | Rationale |
|---|---:|---|
| Visual hierarchy | 7 | ... |
| Value proposition | 6 | ... |
| CTA effectiveness | 5 | ... |
| Layout / spacing | 7 | ... |
| Readability | 8 | ... |
| Trust / credibility | 6 | ... |
| Accessibility | 6 | ... |
| Mobile friendliness | 5 | ... |
| Brand consistency | 7 | ... |
| Overall UX | 6 | ... |

## What's Working Well

- ...

## What Needs Work

- ...

## Priority Recommendations

### High Priority

- **Issue:** ...
  - **Recommendation:** ...
  - **Expected impact:** ...

## Redesign Concepts

### 1. {concept.name}

- Goal: ...
- Style direction: ...
- Key changes:
  - ...

## Mockups

1. {concept.name}
2. {concept.name}
3. {concept.name}
4. {concept.name}
```

## Error Handling

- Invalid URL: "I could not review the page because the URL was invalid. Please provide a full URL or domain."
- Page does not load: "I could not fully load the page. I captured what was available, but the review may be incomplete."
- Screenshots fail: "I was able to extract page text, but screenshot capture failed. I can provide a structural critique, but not a full visual critique."
- Image generation fails: "The page review completed, but mockup generation failed. I can still provide redesign briefs that can be used to generate mockups later."
- Login required: "The page appears to require login or restricted access. I can only review what is publicly visible unless access is provided through the browser session."

## Safety and Privacy

- Do not bypass paywalls, authentication, CAPTCHA, or access controls.
- Do not submit forms unless the user explicitly asks and the action is safe.
- Do not make purchases.
- Do not change account settings.
- Do not scrape private information.
- If private user data appears, summarize and critique UX without exposing sensitive details.

## Quality Checklist

Before responding, verify:

- The URL was normalized and loaded or the failure is clearly disclosed.
- Desktop and mobile screenshots were attempted.
- The page gist is specific.
- Scores are 0-10.
- Every score has a rationale.
- Feedback references actual page evidence.
- Recommendations are prioritized.
- Redesign concepts are distinct.
- Mockup prompts preserve the original business context.
- Generated mockups correspond to the redesign concepts.
