// Shared helpers for the control audit scripts. Read-only by design.
import { createRequire } from "node:module";
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

// Find Playwright: the current project first, then any project under ~/Projects.
export function loadPlaywright() {
  const roots = [process.cwd(), ...readdirSync(join(homedir(), "Projects")).map((d) => join(homedir(), "Projects", d))];
  for (const r of roots) {
    if (existsSync(join(r, "node_modules", "playwright"))) return createRequire(join(r, "package.json"))("playwright");
  }
  throw new Error("Playwright not found. Run `pnpm add -D playwright` in the project, or in any ~/Projects folder.");
}

export function args(defs) {
  const out = { ...defs };
  const a = process.argv.slice(2);
  for (let i = 0; i < a.length; i++) {
    const k = a[i].replace(/^--/, "");
    if (k in out) out[k] = a[++i];
  }
  out.pages = String(out.pages).split(",").filter(Boolean);
  return out;
}

// A context that cannot change data: every non-GET request is aborted.
export async function readOnlyContext(browser, opts) {
  const ctx = await browser.newContext(opts);
  await ctx.route("**/*", (r) => (r.request().method() === "GET" ? r.continue() : r.abort()));
  return ctx;
}

export const launch = (pw) => pw.chromium.launch({ args: ["--use-mock-keychain", "--password-store=basic"] });

// Selector for one element: tag plus its classes, minus state classes.
export const STATE_CLASSES = /^(on|active|inactive|selected|current|open|checked|disabled|is-[\w-]+)$/;
