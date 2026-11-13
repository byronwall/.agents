// Measure control craft on each page and print only the misses.
// usage: node audit-controls.mjs --base http://localhost:3000 --pages /,/settings [--width 1440]
// Checks: hit targets < 24px, pointer cursor, keyboard focus style, mixed heights in one toolbar row,
// and selected states that change font weight (the label gets wider and shifts its neighbors).
// Read-only: non-GET requests are aborted. Transitions are disabled so styles are read at their end state.
import { args, launch, loadPlaywright, readOnlyContext, STATE_CLASSES } from "./lib.mjs";

const o = args({ base: "http://localhost:3000", pages: "/", width: "1440" });
const pw = loadPlaywright();
const browser = await launch(pw);
const ctx = await readOnlyContext(browser, { viewport: { width: +o.width, height: 900 } });
const page = await ctx.newPage();
const errors = [];
page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

let misses = 0;
for (const p of o.pages) {
  await page.goto(o.base + p, { waitUntil: "networkidle" });
  await page.addStyleTag({ content: "*,*::before,*::after{transition:none!important;animation:none!important}" });
  await page.keyboard.press("Shift");
  const r = await page.evaluate((stateRe) => {
    const re = new RegExp(stateRe);
    const name = (e) => (e.tagName.toLowerCase() + [...e.classList].map((c) => "." + c).join("")).slice(0, 70);
    const out = { "hit < 24px": {}, "no pointer cursor": {}, "no focus style": {}, "toolbar heights differ": [], "selection changes weight": [] };
    const ctl = [...document.querySelectorAll("button, a[href], input:not([type=hidden]), select, textarea, [role=tab]")].filter((e) => e.getBoundingClientRect().width);
    for (const e of ctl) {
      const b = e.getBoundingClientRect();
      const cs = getComputedStyle(e);
      const box = e.matches("input") && (b.width < 4 || b.height < 4 || e.matches("[type=checkbox],[type=radio]")) ? e.closest("label") ?? e : e;
      const bb = box.getBoundingClientRect();
      // A ::before with negative inset counts as a larger hit area.
      const pre = getComputedStyle(e, "::before");
      const grow = pre.content !== "none" && pre.position === "absolute" ? -2 * parseFloat(pre.top || 0) : 0;
      if ((e.matches("button, select, input[type=checkbox], [role=tab]") || box !== e) && Math.round(Math.min(bb.width, bb.height) + grow) < 24) out["hit < 24px"][name(box)] = `${Math.round(bb.width)}×${Math.round(bb.height)}`;
      if (e.matches("button, a[href], select, [role=tab]") && !e.disabled && cs.cursor !== "pointer") out["no pointer cursor"][name(e)] = cs.cursor;
      e.focus();
      if (document.activeElement === e) {
        const f = getComputedStyle(e);
        const own = (f.outlineStyle !== "none" && parseFloat(f.outlineWidth) > 0) || f.boxShadow !== "none";
        const wrap = e.parentElement && getComputedStyle(e.parentElement).boxShadow !== "none";
        const sib = e.nextElementSibling && getComputedStyle(e.nextElementSibling).outlineStyle !== "none";
        if (!own && !wrap && !sib) out["no focus style"][name(e)] = "none";
      }
      e.blur();
    }
    // Toolbar rows: bordered controls sharing a parent should share a height.
    const rows = new Map();
    for (const e of ctl) {
      const cs = getComputedStyle(e);
      if (cs.display.includes("inline") === false && cs.display !== "flex" && cs.display !== "grid") continue;
      if (e.matches("a") || cs.borderTopWidth === "0px") continue;
      const k = e.parentElement;
      rows.set(k, [...(rows.get(k) ?? []), [name(e), Math.round(e.getBoundingClientRect().height)]]);
    }
    for (const [k, v] of rows) if (new Set(v.map((x) => x[1])).size > 1) out["toolbar heights differ"].push(`${name(k)}: ${v.map((x) => x.join(" ")).join(", ")}`);
    // Selected vs unselected siblings of the same kind must share font weight.
    const sel = ctl.filter((e) => [...e.classList].some((c) => re.test(c)) || e.matches("[aria-selected=true],[aria-pressed=true],[aria-current]"));
    for (const e of sel) {
      const base = [...e.classList].filter((c) => !re.test(c));
      const peer = [...(e.parentElement?.children ?? [])].find((x) => x !== e && x.tagName === e.tagName && base.every((c) => x.classList.contains(c)) && ![...x.classList].some((c) => re.test(c)));
      // Only peers on the same row: a weight change in a vertical list shifts nothing.
      if (peer && Math.abs(peer.getBoundingClientRect().top - e.getBoundingClientRect().top) < 4 && getComputedStyle(peer).fontWeight !== getComputedStyle(e).fontWeight) out["selection changes weight"].push(`${name(e)} ${getComputedStyle(peer).fontWeight}→${getComputedStyle(e).fontWeight}`);
    }
    return out;
  }, STATE_CLASSES.source);
  const lines = Object.entries(r).flatMap(([k, v]) => {
    const items = Array.isArray(v) ? [...new Set(v)] : Object.entries(v).map(([n, x]) => `${n} (${x})`);
    return items.length ? [`  ${k}:`, ...items.slice(0, 12).map((x) => `    - ${x}`)] : [];
  });
  misses += lines.length;
  console.log(lines.length ? `${p}\n${lines.join("\n")}` : `${p}: clean`);
}
if (errors.length) console.log(`console errors:\n  ${[...new Set(errors)].slice(0, 8).join("\n  ")}`);
await browser.close();
process.exitCode = misses ? 1 : 0;
