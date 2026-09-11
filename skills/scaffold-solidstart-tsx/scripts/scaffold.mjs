#!/usr/bin/env node

import { access, cp, mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import { constants } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const templateRoot = join(skillRoot, "assets", "template");
const args = parseArgs(process.argv.slice(2));

if (args.help) {
  printHelp();
  process.exit(0);
}

const target = resolve(process.cwd(), args.dir || ".");
const packageName = slugify(args.name || basename(target));
const appTitle = args.title || titleCase(packageName);

if (!packageName) fail("A valid package name is required.");
if (Number(process.versions.node.split(".")[0]) < 20) fail("Node.js 20 or newer is required.");

await mkdir(target, { recursive: true });
const files = await listFiles(templateRoot);
const conflicts = [];

for (const relativePath of files) {
  const destination = join(target, relativePath);
  if (await exists(destination)) conflicts.push(relativePath);
}

if (conflicts.length && !args.force) {
  const shown = conflicts.slice(0, 12).map(path => `  - ${path}`).join("\n");
  const remainder = conflicts.length > 12 ? `\n  - …and ${conflicts.length - 12} more` : "";
  fail(`Template paths already exist:\n${shown}${remainder}\nUse --force only when overwriting them is authorized.`);
}

for (const relativePath of files) {
  const source = join(templateRoot, relativePath);
  const destination = join(target, relativePath);
  await mkdir(dirname(destination), { recursive: true });
  await cp(source, destination, { force: Boolean(args.force) });
  const content = await readFile(destination, "utf8");
  await writeFile(destination, content
    .replaceAll("__PACKAGE_NAME__", packageName)
    .replaceAll("__APP_TITLE__", appTitle));
}

console.log(`Created ${files.length} files in ${target}`);

if (args.install) await run("pnpm", ["install"], target);
if (args.verify) {
  await run("pnpm", ["typecheck"], target);
  await run("pnpm", ["build"], target);
}

if (!args.install) console.log("Next: pnpm install");
if (!args.verify) console.log("Then: pnpm typecheck && pnpm build");

function parseArgs(values) {
  const parsed = { dir: ".", force: false, help: false, install: false, verify: false };
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (value === "--dir") parsed.dir = requiredValue(values, ++index, value);
    else if (value === "--name") parsed.name = requiredValue(values, ++index, value);
    else if (value === "--title") parsed.title = requiredValue(values, ++index, value);
    else if (value === "--force") parsed.force = true;
    else if (value === "--install") parsed.install = true;
    else if (value === "--verify") parsed.verify = true;
    else if (value === "--help" || value === "-h") parsed.help = true;
    else fail(`Unknown option: ${value}`);
  }
  return parsed;
}

function requiredValue(values, index, option) {
  const value = values[index];
  if (!value || value.startsWith("--")) fail(`${option} requires a value.`);
  return value;
}

async function listFiles(root, prefix = "") {
  const entries = await readdir(join(root, prefix), { withFileTypes: true });
  const paths = [];
  for (const entry of entries) {
    const relativePath = join(prefix, entry.name);
    if (entry.isDirectory()) paths.push(...await listFiles(root, relativePath));
    else if (entry.isFile()) paths.push(relativePath);
  }
  return paths.sort();
}

async function exists(path) {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

function slugify(value) {
  return value.toLowerCase().trim().replace(/[^a-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "");
}

function titleCase(value) {
  return value.split(/[-_.]+/).filter(Boolean)
    .map(part => part[0].toUpperCase() + part.slice(1)).join(" ");
}

function run(command, commandArgs, cwd) {
  const executable = process.platform === "win32" ? `${command}.cmd` : command;
  return new Promise((resolvePromise, reject) => {
    const child = spawn(executable, commandArgs, { cwd, stdio: "inherit" });
    child.on("error", reject);
    child.on("exit", code => code === 0
      ? resolvePromise()
      : reject(new Error(`${command} ${commandArgs.join(" ")} exited with ${code}.`)));
  });
}

function printHelp() {
  console.log(`Usage: scaffold.mjs [options]

Options:
  --dir <path>     Target directory. Default: current directory.
  --name <name>    Package name. Default: target directory name.
  --title <title>  Visible app title. Default: package name in title case.
  --install        Run pnpm install after copying.
  --verify         Run pnpm typecheck and pnpm build after copying.
  --force          Overwrite template paths. Never deletes other files.
  --help, -h       Show this help.`);
}

function fail(message) {
  console.error(message);
  process.exit(1);
}
