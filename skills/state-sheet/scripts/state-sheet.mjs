#!/usr/bin/env node
// State sheet: capture every interactive control of a running app in rest, hover,
// keyboard focus, and pressed states, and lay them out as one contact sheet.
// Read-only: every non-GET request is aborted, and presses release off the element.
//
// usage: node state-sheet.mjs --base http://localhost:3000 --pages /,/settings --out tmp/state-sheet --prefix before
//        [--selectors sel1,sel2 | --selectors-file controls.txt] [--discover] [--max 80]
//        [--width 1440 --height 900 --scale 2] [--dark] [--allow-writes] [--wait 250]
import { createRequire } from "node:module";
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, all) => {
    if (!a.startsWith("--")) return acc;
    const next = all[i + 1];
    acc.push([a.slice(2), next && !next.startsWith("--") ? next : true]);
    return acc;
  }, []),
);
if (!args.base) {
  console.error("missing --base <url>. See SKILL.md for usage.");
  process.exit(2);
}
const base = String(args.base).replace(/\/$/, "");
const pages = String(args.pages ?? "/").split(",").map((p) => p.trim()).filter(Boolean);
const out = resolve(String(args.out ?? "tmp/state-sheet"));
const prefix = String(args.prefix ?? "sheet");
const width = Number(args.width ?? 1440);
const height = Number(args.height ?? 900);
const scale = Number(args.scale ?? 2);
const max = Number(args.max ?? 80);
const settle = Number(args.wait ?? 250);
let selectors = [];
if (args.selectors && args.selectors !== true) selectors = String(args.selectors).split(",").map((s) => s.trim());
if (args["selectors-file"]) selectors = readFileSync(String(args["selectors-file"]), "utf8").split("\n").map((s) => s.trim()).filter((s) => s && !s.startsWith("#"));
const discover = args.discover || !selectors.length;
mkdirSync(out, { recursive: true });

// Find Playwright: the project first, then $PLAYWRIGHT_DIR, then any ~/Projects/*/node_modules.
function loadPlaywright() {
  const tries = [join(process.cwd(), "package.json")];
  if (process.env.PLAYWRIGHT_DIR) tries.push(join(process.env.PLAYWRIGHT_DIR, "package.json"));
  const projects = join(homedir(), "Projects");
  if (existsSync(projects))
    for (const d of readdirSync(projects)) if (existsSync(join(projects, d, "node_modules", "playwright"))) tries.push(join(projects, d, "package.json"));
  for (const t of tries) {
    try {
      return createRequire(t)("playwright");
    } catch {}
  }
  console.error("Playwright not found. Run `pnpm dlx playwright install chromium` in a project that has it, or set PLAYWRIGHT_DIR.");
  process.exit(2);
}
const { chromium } = loadPlaywright();

const browser = await chromium.launch({ args: ["--use-mock-keychain", "--password-store=basic"] });
const ctx = await browser.newContext({
  viewport: { width, height },
  deviceScaleFactor: scale,
  colorScheme: args.dark ? "dark" : "light",
  reducedMotion: "no-preference",
});
if (!args["allow-writes"]) await ctx.route("**/*", (r) => (r.request().method() === "GET" ? r.continue() : r.abort()));
const page = await ctx.newPage();
page.on("dialog", (d) => d.dismiss());
page.on("popup", (p) => p.close());
const errors = [];
page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
page.on("pageerror", (e) => errors.push(String(e)));

const open = async (p) => {
  await page.goto(base + p, { waitUntil: "networkidle" }).catch(() => page.goto(base + p));
  await page.waitForTimeout(settle);
};

// Discovery: one representative per "kind" (tag + role + sorted classes), visible, not huge.
async function discoverOn(p) {
  await open(p);
  return page.evaluate(() => {
    const sel = 'button, a[href], input:not([type=hidden]), select, textarea, summary, [role=button], [role=tab], [role=link], [role=menuitem], [role=option], [role=switch], [role=checkbox], [tabindex]:not([tabindex="-1"]), [onclick]';
    const found = new Map();
    const pointer = [...document.querySelectorAll("body *")].filter((n) => getComputedStyle(n).cursor === "pointer" && !getComputedStyle(n.parentElement || document.body).cursor.includes("pointer"));
    for (const n of [...document.querySelectorAll(sel), ...pointer]) {
      const r = n.getBoundingClientRect();
      if (!r.width || !r.height || r.width > 900 || r.height > 160) continue;
      const cls = [...n.classList].filter((c) => !/^(on|off|active|inactive|current|selected|checked|disabled|is-|has-|open|closed|done|zero)$|^(is|has)-/.test(c)).sort();
      const kind = `${n.tagName.toLowerCase()}${n.getAttribute("role") ? `[role=${n.getAttribute("role")}]` : ""}${n.type && n.tagName === "INPUT" ? `[type=${n.type}]` : ""}${cls.map((c) => "." + CSS.escape(c)).join("")}`;
      // Prefer an instance at rest: not current, selected, pressed, or disabled.
      const stateful = [...n.classList].some((c) => /^(on|active|current|selected|checked|open|pressed)$/.test(c)) || n.matches('[aria-current]:not([aria-current="false"]), [aria-selected=true], [aria-pressed=true], :checked, :disabled, [aria-disabled=true]');
      const prev = found.get(kind);
      if (prev && (!prev.stateful || stateful)) continue;
      const all = [...document.querySelectorAll(kind)];
      found.set(kind, { kind, index: all.indexOf(n), stateful });
    }
    return [...found.values()];
  });
}

const targets = []; // { label, selector, index, page }
const seen = new Set();
for (const p of pages) {
  if (discover) {
    for (const d of await discoverOn(p)) if (!seen.has(d.kind)) seen.add(d.kind), targets.push({ label: d.kind, selector: d.kind, index: Math.max(0, d.index), page: p });
  } else {
    await open(p);
    for (const s of selectors) if (!seen.has(s) && (await page.locator(s).first().isVisible().catch(() => false))) seen.add(s), targets.push({ label: s, selector: s, index: 0, page: p });
  }
  await page.screenshot({ path: join(out, `${prefix}-page-${p.replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "") || "root"}.png`) });
}
const missing = discover ? [] : selectors.filter((s) => !seen.has(s));

// Computed-style fingerprint, so the report can say what changed, not only that pixels moved.
const STYLE = ["borderTopWidth", "backgroundColor", "backgroundImage", "color", "borderColor", "boxShadow", "outlineStyle", "outlineColor", "outlineOffset", "transform", "opacity", "textDecorationLine", "fontWeight"];
const styleOf = (loc) => loc.evaluate((n, keys) => Object.fromEntries(keys.map((k) => [k, getComputedStyle(n)[k]])), STYLE).catch(() => ({}));
// Skip values that only follow currentColor: a border color with no border, an outline color with no outline.
const diff = (a, b) =>
  STYLE.filter((k) => a[k] !== b[k] && k !== "borderTopWidth")
    .filter((k) => !(k === "borderColor" && b.borderTopWidth === "0px") && !(k === "outlineColor" && b.outlineStyle === "none"))
    .map((k) => `${k}: ${b[k]}`);

const rows = [];
for (const t of targets.slice(0, max)) {
  await open(t.page);
  const el = page.locator(t.selector).nth(t.index);
  if (!(await el.isVisible().catch(() => false))) continue;
  await el.scrollIntoViewIfNeeded().catch(() => {});
  const box = await el.boundingBox();
  if (!box) continue;
  const pad = 10;
  const clip = { x: Math.max(0, box.x - pad), y: Math.max(0, box.y - pad), width: Math.min(box.width + pad * 2, 560), height: Math.min(box.height + pad * 2, 120) };
  const mid = { x: box.x + Math.min(box.width / 2, 40), y: box.y + box.height / 2 };
  const shot = async () => (await page.screenshot({ clip, animations: "allow" })).toString("base64");

  await page.mouse.move(1, 1);
  await page.waitForTimeout(settle);
  const restStyle = await styleOf(el);
  const rest = await shot();

  await page.mouse.move(mid.x, mid.y);
  await page.waitForTimeout(settle);
  const hoverStyle = await styleOf(el);
  const hover = await shot();
  await page.mouse.move(1, 1);

  // Keyboard modality: focus the element, then press a modifier so :focus-visible matches.
  await el.evaluate((n) => n.focus({ focusVisible: true })).catch(() => {});
  await page.keyboard.press("Shift");
  await page.waitForTimeout(settle);
  const focusStyle = await styleOf(el);
  const focus = await shot();
  await page.evaluate(() => document.activeElement && document.activeElement.blur());

  // Press and hold, capture, then release away from the element so no click fires.
  await page.mouse.move(mid.x, mid.y);
  await page.mouse.down();
  await page.waitForTimeout(Math.min(settle, 150));
  const pressStyle = await styleOf(el);
  const press = await shot();
  await page.mouse.move(1, 1);
  await page.mouse.up();
  await page.keyboard.press("Escape");

  const flags = [];
  if (hover === rest) flags.push("no hover");
  if (focus === rest) flags.push("no focus ring");
  if (press === hover) flags.push("no press");
  const fClip = focusStyle.outlineStyle !== "none" && Number.parseFloat(focusStyle.outlineOffset) >= 0 && (box.x < 4 || box.x + box.width > width - 4) ? ["focus ring may clip at viewport edge"] : [];
  rows.push({
    label: t.label,
    page: t.page,
    imgs: [rest, hover, focus, press],
    flags: [...flags, ...fClip],
    changes: { hover: diff(restStyle, hoverStyle), focus: diff(restStyle, focusStyle), press: diff(hoverStyle, pressStyle) },
  });
}

const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]);
const sheet = (part, title) => `<!doctype html><meta charset="utf-8"><title>${esc(prefix)} state sheet</title>
<style>
body{font:12px/1.4 system-ui,sans-serif;margin:16px;background:${args.dark ? "#111" : "#fff"};color:${args.dark ? "#ddd" : "#222"}}
table{border-collapse:collapse}td,th{padding:6px 10px;vertical-align:top;border-bottom:1px solid #8883;text-align:left}
img{height:45px;display:block}code{font-size:11px;word-break:break-all}td:first-child{width:200px;max-width:260px}.page{color:#888;display:block}
.flag{color:#c2413a;font-weight:600;display:block}.chg{color:#888;font-size:10px;max-width:240px;display:block;margin-top:2px}
</style>
<h3>${esc(title)}</h3>
<table><tr><th>control</th><th>rest</th><th>hover</th><th>focus (keyboard)</th><th>pressed</th></tr>
${part
  .map(
    (r) => `<tr><td><code>${esc(r.label)}</code><span class="page">${esc(r.page)}</span>${r.flags.map((f) => `<span class="flag">${esc(f)}</span>`).join("")}</td>${r.imgs
      .map((i, k) => `<td><img src="data:image/png;base64,${i}">${k ? `<span class="chg">${esc((r.changes[["", "hover", "focus", "press"][k]] || []).join("; ").slice(0, 160))}</span>` : ""}</td>`)
      .join("")}</tr>`,
  )
  .join("\n")}
</table>`;
const head = `${prefix} · ${base} · ${rows.length} controls${args.dark ? " · dark" : ""}`;
writeFileSync(join(out, `${prefix}-states.html`), sheet(rows, head));
writeFileSync(join(out, `${prefix}-states.json`), JSON.stringify(rows.map(({ imgs, ...r }) => r), null, 2));
// PNG pages of 20 rows, so each image stays readable and under screenshot limits
const per = 20;
const sheets = [];
const view = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: scale });
for (let i = 0; i < rows.length; i += per) {
  const n = rows.length > per ? `-${i / per + 1}` : "";
  const file = join(out, `${prefix}-states${n}.png`);
  await view.setContent(sheet(rows.slice(i, i + per), `${head} · ${i + 1}–${Math.min(i + per, rows.length)}`));
  await view.screenshot({ path: file, fullPage: true, timeout: 120000 });
  sheets.push(file);
}
await browser.close();

console.log(`${rows.length} controls\nsheets:\n  ${sheets.join("\n  ")}\nhtml: ${join(out, `${prefix}-states.html`)}`);
const flagged = rows.filter((r) => r.flags.length);
console.log(`flagged: ${flagged.length}`);
for (const r of flagged) console.log(`  ${r.label} (${r.page}): ${r.flags.join(", ")}`);
if (missing.length) console.log(`not found: ${missing.join(" | ")}`);
if (errors.length) console.log(`console errors: ${errors.length}\n  ${[...new Set(errors)].slice(0, 5).join("\n  ")}`);
