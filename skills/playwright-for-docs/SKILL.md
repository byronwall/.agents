# Playwright Documentation Screenshot Skill

Use this skill when a user wants screenshots generated from a working app and added to documentation, such as a README, docs page, or release notes.

The user will usually provide a short hint about the purpose, for example:

- “Show the onboarding flow.”
- “Capture the dashboard for the README.”
- “Document the new settings UI.”
- “Take screenshots of the payment flow.”

Use that hint to decide which screenshots are useful. Prefer a small, curated set of screenshots over exhaustive coverage.

## Goal

Run the application, capture high-quality screenshots with Playwright, save them in the repo, and update the README or relevant docs with links to those screenshots.

Unless the user specifies another location, save screenshots to:

```text
docs/screenshots
```

## Expected Outputs

At the end of the task, the repo should contain:

- Screenshot image files in `docs/screenshots`.
- A Playwright script, temporary script, or MCP-driven capture process used to create them.
- Updated documentation that references the screenshots.
- A short summary of what was captured and which docs were changed.

## Screenshot Strategy

Start from the user’s hint and inspect the app to identify the most useful visual states.

Default screenshot set:

- One full-app screenshot that gives readers context.
- Targeted screenshots of important UI areas, cropped to relevant elements when possible.
- Additional screenshots for distinct flows or states only when they add documentation value.

Avoid too many full-page or full-app screenshots. If the important content is a card, modal, table, chart, form, sidebar, or panel, crop to that element instead.

Good screenshot candidates:

- Landing page or primary app shell.
- Main dashboard or home state.
- Empty state, loading state, or error state, if important.
- Modals, popovers, drawers, and command palettes.
- Forms with validation or completed inputs.
- Tables, charts, timelines, maps, or other data-heavy widgets.
- Before/after states in flows.
- New or user-mentioned functionality.

Avoid capturing:

- Redundant full-page screenshots.
- Low-value intermediate states.
- Screens with private tokens, personal data, credentials, or secrets.
- Broken loading states unless the goal is to document an error.
- Browser chrome unless explicitly requested.

## Setup

First inspect the repo to understand how to run the app.

Look for:

- `package.json`
- `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, or `bun.lockb`
- `vite.config.*`, `next.config.*`, `astro.config.*`, `remix.config.*`, etc.
- Existing Playwright config or tests.
- README instructions.
- `.env.example` or documented environment variables.

Use the repo’s package manager when obvious:

```bash
# Prefer the lockfile/package manager already used by the repo.
pnpm install
pnpm dev

# Or:
npm install
npm run dev

# Or:
yarn install
yarn dev

# Or:
bun install
bun dev
```

If dependencies are already installed, do not reinstall unnecessarily.

## Running the App

Start the app using the project’s documented development command.

Common commands:

```bash
npm run dev
pnpm dev
yarn dev
bun dev
npm start
```

If the app exposes a local URL in terminal output, use that URL.

Common defaults:

- Vite: `http://localhost:5173`
- Next.js: `http://localhost:3000`
- Astro: `http://localhost:4321`
- Storybook: `http://localhost:6006`

Wait until the app is reachable before taking screenshots.

## Playwright Options

Use either Playwright MCP or a scripted Playwright capture.

Prefer Playwright MCP when:

- You need to explore the app interactively.
- The screenshot targets are not yet obvious.
- You need to inspect selectors, accessibility names, or element bounds.

Prefer a scripted Playwright capture when:

- The flow is repeatable.
- Multiple screenshots are required.
- You need deterministic viewport sizes, crops, or file names.
- The repo already has Playwright installed.

## Installing Playwright When Needed

If Playwright is not available and the user has not forbidden dependency changes, use the least intrusive option.

For one-off scripts, prefer running Playwright through the repo’s package manager without permanently changing app code when possible.

Examples:

```bash
# npm
npx playwright install chromium

# pnpm
pnpm exec playwright install chromium

# yarn
yarn playwright install chromium
```

If Playwright is not listed as a dependency and a script is needed, either:

- Use the environment’s available Playwright tooling, or
- Add a temporary script outside the app source, such as `scripts/capture-screenshots.mjs`, when appropriate.

Do not make broad dependency or config changes unless necessary.

## File Naming

Use stable, descriptive, lowercase file names.

Recommended pattern:

```text
NN-short-description.png
```

Examples:

```text
docs/screenshots/01-full-app.png
docs/screenshots/02-dashboard-summary.png
docs/screenshots/03-settings-modal.png
docs/screenshots/04-empty-state.png
```

Use numbering to preserve documentation order.

## Viewport and Rendering Guidelines

Use a consistent viewport unless the docs need responsive examples.

Recommended default viewport:

```ts
await page.setViewportSize({ width: 1440, height: 1000 });
```

For README screenshots, prefer desktop unless the user asks for mobile.

Use mobile screenshots only when:

- The app has a meaningful mobile layout.
- The user specifically mentions mobile or responsive behavior.
- The documentation needs to show responsive UI.

Before taking screenshots:

- Wait for the page to settle.
- Wait for important network calls or UI states.
- Disable animations when possible if they cause flaky captures.
- Seed or select stable demo data if available.
- Prefer light mode unless the app is clearly dark-mode-first or the user asks for dark mode.

## Cropping Targeted Screenshots

For interesting elements, prefer locator screenshots over full-page screenshots.

Examples:

```ts
await page.getByRole("dialog").screenshot({
  path: "docs/screenshots/03-settings-modal.png",
});
```

```ts
await page
  .locator('[data-testid="dashboard-card"]')
  .first()
  .screenshot({ path: "docs/screenshots/02-dashboard-card.png" });
```

Use semantic locators first:

- `getByRole`
- `getByLabel`
- `getByText`
- `getByTestId`

Use CSS selectors when semantic locators are not practical.

When cropping, include enough surrounding context that the screenshot is understandable.

## Full-App Screenshots

Capture a full-app screenshot only when it gives useful context.

Example:

```ts
await page.screenshot({
  path: "docs/screenshots/01-full-app.png",
  fullPage: true,
});
```

If the full page is very tall, consider a viewport screenshot instead:

```ts
await page.screenshot({
  path: "docs/screenshots/01-app-shell.png",
  fullPage: false,
});
```

Avoid multiple full-page screenshots unless they show genuinely different pages or flows.

## Example Script

Create a script like this when scripted capture is useful:

```ts
import { chromium } from "playwright";
import fs from "node:fs/promises";

const BASE_URL = process.env.SCREENSHOT_BASE_URL ?? "http://localhost:5173";
const OUT_DIR = "docs/screenshots";

async function main() {
  console.log(`Creating screenshot directory: ${OUT_DIR}`);
  await fs.mkdir(OUT_DIR, { recursive: true });

  console.log("Launching browser");
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
  });

  try {
    console.log(`Opening ${BASE_URL}`);
    await page.goto(BASE_URL, { waitUntil: "networkidle" });

    console.log("Capturing full app screenshot");
    await page.screenshot({
      path: `${OUT_DIR}/01-full-app.png`,
      fullPage: true,
    });

    // Replace these examples with targets based on the user's hint and app structure.
    const mainRegion = page.getByRole("main");
    if (await mainRegion.count()) {
      console.log("Capturing main content region");
      await mainRegion.screenshot({
        path: `${OUT_DIR}/02-main-content.png`,
      });
    }

    const dialog = page.getByRole("dialog");
    if (await dialog.count()) {
      console.log("Capturing dialog");
      await dialog.first().screenshot({
        path: `${OUT_DIR}/03-dialog.png`,
      });
    }
  } finally {
    console.log("Closing browser");
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

If the repo is TypeScript-only but does not support direct TS execution, use `.mjs` instead of `.ts`.

## Capturing Flows

For multi-step flows:

1. Capture the starting state if it is visually useful.
2. Interact with the app using user-like actions.
3. Capture each important final or decision state.
4. Skip obvious intermediate states unless they clarify the docs.

Example:

```ts
await page.getByRole("button", { name: /new project/i }).click();
await page.getByLabel(/project name/i).fill("Documentation Demo");
await page.getByRole("button", { name: /create/i }).click();
await page.waitForLoadState("networkidle");

await page.getByRole("main").screenshot({
  path: "docs/screenshots/03-created-project.png",
});
```

## Authentication and Demo Data

If the app requires authentication:

- Check for documented demo credentials.
- Check for seeded local accounts.
- Check for a mock/demo mode.
- Ask the user only if credentials are required and no safe local path exists.

Never invent real credentials.

Do not capture sensitive data.

If screenshots require realistic data, prefer existing seed commands or demo fixtures.

Common commands to look for:

```bash
npm run seed
pnpm seed
npm run db:seed
pnpm db:seed
```

## Documentation Updates

After screenshots are saved, update the most relevant documentation file.

Default priority:

1. `README.md`
2. `docs/README.md`
3. A docs page matching the feature or user hint.
4. A new docs page only when there is no appropriate existing file.

Use relative links from the documentation file to the images.

README example:

```md
## Screenshots

### App overview

![App overview](docs/screenshots/01-full-app.png)

### Dashboard summary

![Dashboard summary](docs/screenshots/02-dashboard-summary.png)

### Settings modal

![Settings modal](docs/screenshots/03-settings-modal.png)
```

If the docs file is inside `docs/`, adjust links accordingly:

```md
![Dashboard summary](screenshots/02-dashboard-summary.png)
```

Add short captions when they help explain what the screenshot shows.

## README Placement

When updating a README, place screenshots in the most natural section.

Good locations:

- After the project description.
- After a “Features” section.
- Before “Installation” or “Development”.
- In an existing “Screenshots”, “Demo”, or “Usage” section.

Avoid interrupting setup instructions or API references.

If a screenshots section already exists, update it instead of creating a duplicate.

## Quality Checks

After capture, verify that each screenshot:

- Exists at the expected path.
- Is not blank.
- Shows the intended UI.
- Is not mostly whitespace.
- Does not contain secrets or private data.
- Has a useful filename.
- Is linked correctly from documentation.

If possible, open or inspect the generated images before finalizing.

## Final Response

Summarize the work completed.

Include:

- The screenshot folder used.
- The screenshots created.
- The docs files updated.
- Any limitations, skipped screenshots, or app states that could not be reached.

Example:

```md
Done.

- Saved screenshots in `docs/screenshots`:
  - `01-full-app.png`
  - `02-dashboard-summary.png`
  - `03-settings-modal.png`
- Updated `README.md` with a new Screenshots section.
- I skipped the billing screen because it required credentials that were not available locally.
```

## Failure Handling

If the app cannot run:

- Report the command attempted.
- Include the relevant error summary.
- Check the README or package scripts for the correct command.
- Try one reasonable alternative if available.
- Do not fabricate screenshots.

If Playwright cannot access the app:

- Confirm the app URL.
- Confirm the dev server is still running.
- Check for console or page errors.
- Try the detected localhost URL from the dev server output.

If no useful UI can be reached:

- Explain what blocked capture.
- Leave any script or notes only if they are useful.
- Do not update docs with missing or placeholder images unless the user requested placeholders.

## Principles

- Use the user’s hint to decide what matters.
- Prefer useful, cropped screenshots over many full-page images.
- Keep screenshots stable and documentation-friendly.
- Avoid secrets and personal data.
- Make minimal repo changes.
- Update docs with clear relative links.
