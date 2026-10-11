#!/usr/bin/env node

// Applies the common initiative-map.json edits, stamps last_updated, and runs
// the validator, so lifecycle updates need no hand-written JSON scripts.
//
// Usage: node update-map.mjs <initiative-dir> [options]
//   --phase <phase>               initiative.current_phase
//   --status <status>             initiative.status (planned|active|paused|completed|cancelled)
//   --next "<text>"               initiative.next_action
//   --artifact <key>=<status>     artifacts.<key>.status and updated_at; key may be
//                                 intent_brief or intent-brief.md style
//   --milestone <id>=<status>     implementation.milestones[id].status
//   --evidence <id>="<text>"      append to that milestone's evidence
// Repeat any option. Prints the validator result and exits with its code.

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    phase: { type: 'string' },
    status: { type: 'string' },
    next: { type: 'string' },
    artifact: { type: 'string', multiple: true, default: [] },
    milestone: { type: 'string', multiple: true, default: [] },
    evidence: { type: 'string', multiple: true, default: [] },
  },
});

const dir = path.resolve(positionals[0] || '.');
const mapPath = path.join(dir, 'initiative-map.json');
if (!fs.existsSync(mapPath)) {
  console.error(`No initiative-map.json in ${dir}`);
  process.exit(1);
}
const map = JSON.parse(fs.readFileSync(mapPath, 'utf8'));
const now = new Date();
const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

const pair = (option, value) => {
  const index = value.indexOf('=');
  if (index < 1) {
    console.error(`--${option} takes <key>=<value>, got "${value}"`);
    process.exit(1);
  }
  return [value.slice(0, index), value.slice(index + 1)];
};

const milestone = (id) => {
  const found = (map.implementation?.milestones || []).find((item) => item.id === id);
  if (!found) {
    const ids = (map.implementation?.milestones || []).map((item) => item.id).join(', ') || 'none';
    console.error(`No milestone "${id}". Milestones: ${ids}`);
    process.exit(1);
  }
  return found;
};

map.initiative ??= {};
if (values.phase) map.initiative.current_phase = values.phase;
if (values.status) map.initiative.status = values.status;
if (values.next) map.initiative.next_action = values.next;
for (const value of values.artifact) {
  const [raw, status] = pair('artifact', value);
  const key = raw.replace(/\.md$/, '').replace(/-/g, '_');
  if (!map.artifacts?.[key]) {
    console.error(`No artifact "${key}". Artifacts: ${Object.keys(map.artifacts || {}).join(', ')}`);
    process.exit(1);
  }
  map.artifacts[key].status = status;
  map.artifacts[key].updated_at = today;
}
for (const value of values.milestone) {
  const [id, status] = pair('milestone', value);
  milestone(id).status = status;
}
for (const value of values.evidence) {
  const [id, text] = pair('evidence', value);
  const target = milestone(id);
  target.evidence = [...(target.evidence || []), text];
}
map.initiative.last_updated = today;

fs.writeFileSync(mapPath, `${JSON.stringify(map, null, 2)}\n`);

const validator = path.join(path.dirname(fileURLToPath(import.meta.url)), 'validate-sleuth.mjs');
const result = spawnSync(process.execPath, [validator, dir], { stdio: 'inherit' });
process.exit(result.status ?? 1);
