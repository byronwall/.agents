#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.argv[2] || '.');
const errors = [];
const warnings = [];

function fail(message) {
  errors.push(message);
}

function warn(message) {
  warnings.push(message);
}

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

function read(relativePath) {
  const absolutePath = path.join(root, relativePath);
  if (!fs.existsSync(absolutePath)) {
    fail(`Missing ${relativePath}`);
    return '';
  }
  return fs.readFileSync(absolutePath, 'utf8');
}

function stripFrontmatter(text) {
  return text.replace(/^---\s*\n[\s\S]*?\n---\s*\n?/, '');
}

function words(text) {
  return (stripFrontmatter(text).match(/\b[\p{L}\p{N}][\p{L}\p{N}'’-]*\b/gu) || []).length;
}

function count(text, regex) {
  return (text.match(regex) || []).length;
}

function section(text, heading) {
  const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = text.match(new RegExp(`^## ${escaped}\\s*$([\\s\\S]*?)(?=^## |\\Z)`, 'm'));
  return match?.[1] || '';
}

function requireHeadings(file, text, headings) {
  for (const heading of headings) {
    if (!text.match(new RegExp(`^## ${heading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*$`, 'm'))) {
      fail(`${file}: missing "## ${heading}"`);
    }
  }
}

function validateIntent(file, text, map) {
  const wordCount = words(text);
  const majorSections = count(text, /^## /gm);
  const bullets = count(text, /^\s*(?:[-*]|\d+\.)\s+/gm);
  const questions = map.intent?.human_questions?.filter((item) => item.status !== 'resolved').length || 0;

  if (wordCount > 1500) fail(`${file}: ${wordCount} words exceeds the 1,500-word hard limit`);
  if (majorSections > 10) fail(`${file}: ${majorSections} major sections exceeds the limit of 10`);
  if (bullets > 35) fail(`${file}: ${bullets} bullets/items exceeds the limit of 35`);
  if (questions > 3) fail(`initiative-map.json: ${questions} open human questions exceeds the limit of 3`);

  const forbidden = [
    'Evidence ledger',
    'Source inventory',
    'Source coverage',
    'Risk register',
    'Concept independence',
    'Capability map',
    'Autonomous work frontier',
    'Active human frontier',
    'Uncertainty profile'
  ];
  for (const term of forbidden) {
    if (text.toLowerCase().includes(term.toLowerCase())) {
      fail(`${file}: exposes internal process section "${term}"`);
    }
  }

  requireHeadings(file, text, ['My read', 'What matters most', 'Boundaries', 'What seems settled', 'Next step after confirmation']);

  if (wordCount < 250) warn(`${file}: only ${wordCount} words; verify that the durable intent and boundaries are actually captured`);
}

function validateBrainstorm(file, text, map) {
  const optionCount = count(text, /^## Option \d+\s+[—-]/gm);
  const requested = map.brainstorm?.requested_count || 7;
  const lower = Math.max(3, requested - 1);
  const upper = requested + 1;

  if (optionCount < lower || optionCount > upper) {
    fail(`${file}: expected about ${requested} options, found ${optionCount}`);
  }

  const requiredLabels = ['**Core move:**', '**Makes easier:**', '**Main catch:**', '**Best fit:**'];
  for (const label of requiredLabels) {
    const labelCount = text.split(label).length - 1;
    if (labelCount < optionCount) fail(`${file}: ${label} appears ${labelCount} times for ${optionCount} options`);
  }

  if (/\b(?:SRC|OBS|INF|ASM|DEC|RISK|PROBE)-\d+\b/.test(text)) {
    fail(`${file}: exposes machine IDs in the human brainstorming artifact`);
  }
  if (/^\s*(?:Source|Evidence):/gmi.test(text)) {
    fail(`${file}: includes source/evidence notes; keep provenance in initiative-map.json`);
  }
  if (words(text) > 1800) fail(`${file}: brainstorming artifact exceeds 1,800 words`);

  const premises = (map.brainstorm?.options || []).map((option) => option.premise?.trim().toLowerCase()).filter(Boolean);
  if (new Set(premises).size < Math.min(4, optionCount)) {
    fail('initiative-map.json: brainstorm options do not contain at least four distinct governing premises');
  }
}

function validateShape(file, text, map) {
  requireHeadings(file, text, [
    'Recommendation',
    'Problem and appetite',
    'Core shape',
    'Current fit',
    'How to make this go better',
    'First proof',
    'Rabbit holes and no-gos',
    'Plan handoff'
  ]);

  const wordCount = words(text);
  if (wordCount > 1800) fail(`${file}: ${wordCount} words exceeds the 1,800-word shape limit`);

  const success = map.shape?.success_moves || [];
  if (success.length < 3 || success.length > 6) {
    fail(`initiative-map.json: shape.success_moves must contain 3–6 concrete moves; found ${success.length}`);
  }
  if (!map.shape?.first_proof?.question || !map.shape?.first_proof?.artifact || !map.shape?.first_proof?.decision_rule) {
    fail('initiative-map.json: shape.first_proof must include question, artifact, and decision_rule');
  }
  if ((map.shape?.open_decisions || []).length > 2) {
    fail('initiative-map.json: shape has more than two remaining human decisions');
  }

  const successText = section(text, 'How to make this go better');
  if (count(successText, /^\s*[-*]\s+/gm) < 3) {
    fail(`${file}: "How to make this go better" needs at least three concrete recommendations`);
  }
}

function validatePlan(file, text, map) {
  requireHeadings(file, text, [
    'Plan at a glance',
    'Implementation strategy',
    'Below the cut line'
  ]);

  const milestoneHeadings = [...text.matchAll(/^## Milestone (\d+):\s+(.+)$/gm)];
  if (milestoneHeadings.length < 2) fail(`${file}: needs at least two outcome milestones`);
  if (milestoneHeadings.length > 10) warn(`${file}: ${milestoneHeadings.length} milestones may be too fragmented`);

  const desiredEnds = count(text, /^### Desired end state\s*$/gm);
  if (desiredEnds !== milestoneHeadings.length) {
    fail(`${file}: found ${milestoneHeadings.length} milestones but ${desiredEnds} Desired end state sections`);
  }

  const wordCount = words(text);
  if (wordCount > 6000) fail(`${file}: ${wordCount} words exceeds the 6,000-word hard limit`);
  if (wordCount > 4500) warn(`${file}: ${wordCount} words is heavy; consider moving secondary detail below the cut line or into spikes`);

  const implementation = map.implementation || {};
  const dependencies = implementation.dependencies || [];
  const materialDependencies = dependencies.filter((dependency) => dependency.material);

  if (materialDependencies.length > 0 && !implementation.fast_local_loop?.command) {
    fail('initiative-map.json: material dependencies exist but implementation.fast_local_loop.command is missing');
  }

  for (const dependency of materialDependencies) {
    const prefix = `initiative-map.json dependency ${dependency.id || dependency.name || '<unknown>'}`;
    if (!dependency.application_seam) fail(`${prefix}: missing application_seam`);
    if (!dependency.first_proof_role?.mode || !dependency.first_proof_role?.rationale) fail(`${prefix}: missing first_proof_role.mode or rationale`);
    if (!Array.isArray(dependency.failure_modes) || dependency.failure_modes.length === 0) fail(`${prefix}: missing failure_modes`);
    if (!Array.isArray(dependency.proof_rungs) || dependency.proof_rungs.length === 0) fail(`${prefix}: missing proof_rungs`);
    if (!dependency.local_proof) fail(`${prefix}: missing local_proof or explicit explanation`);
    if (!dependency.live_proof) fail(`${prefix}: missing live_proof or explicit explanation`);
    if (!dependency.rollout) fail(`${prefix}: missing rollout strategy`);
  }

  const milestones = implementation.milestones || [];
  if (milestones.length !== milestoneHeadings.length) {
    fail(`initiative-map.json has ${milestones.length} milestones but ${file} has ${milestoneHeadings.length}`);
  }

  for (const milestone of milestones) {
    const prefix = `initiative-map.json milestone ${milestone.id || milestone.title || '<unknown>'}`;
    if (!milestone.outcome) fail(`${prefix}: missing outcome`);
    if (!milestone.proof) fail(`${prefix}: missing proof`);
    if (!milestone.valid_intermediate_state) fail(`${prefix}: missing valid_intermediate_state`);
    if (!milestone.rollback) fail(`${prefix}: missing rollback/bypass`);
  }

  if (materialDependencies.length > 0 && milestones[0]?.dependencies_introduced?.length > 0) {
    warn('initiative-map.json: first milestone introduces a material dependency; verify that a provider-free or dependency-light proof is impossible');
  }

  if ((implementation.open_decisions || []).length > 3) {
    fail('initiative-map.json: implementation has more than three unresolved decisions/spikes');
  }
}

let map;
try {
  map = JSON.parse(read('initiative-map.json'));
} catch (error) {
  fail(`initiative-map.json: invalid JSON (${error.message})`);
  map = {};
}

if (map.schema_version !== '0.4.0') warn(`initiative-map.json: expected schema_version 0.4.0, found ${map.schema_version || '<missing>'}`);
if (!map.initiative?.title) fail('initiative-map.json: missing initiative.title');
if (!map.initiative?.slug) fail('initiative-map.json: missing initiative.slug');
if (!map.initiative?.current_phase) fail('initiative-map.json: missing initiative.current_phase');

for (const source of map.sources || []) {
  if (!source.id || !source.type || !source.location || !source.anchor || !source.authority) {
    fail(`initiative-map.json: every source needs id, type, location, anchor, and authority (${source.id || '<unknown>'})`);
  }
}

const artifacts = map.artifacts || {};
const phaseOrder = ['intent', 'brainstorm', 'shape', 'plan'];
const currentPhase = map.initiative?.current_phase;

const artifactDefinitions = [
  ['intent_brief', 'intent-brief.md', validateIntent],
  ['brainstorm', 'brainstorm.md', validateBrainstorm],
  ['shape_brief', 'shape-brief.md', validateShape],
  ['implementation_plan', 'implementation-plan.md', validatePlan]
];

for (const [key, fallbackPath, validator] of artifactDefinitions) {
  const artifact = artifacts[key];
  if (!artifact) {
    if (key === 'intent_brief') fail(`initiative-map.json: missing artifacts.${key}`);
    continue;
  }

  const relativePath = artifact.path || fallbackPath;
  if (artifact.status === 'current') {
    const text = read(relativePath);
    if (text) validator(relativePath, text, map);
  } else if (artifact.status === 'stale' && currentPhase === phaseOrder[artifactDefinitions.findIndex(([candidate]) => candidate === key)]) {
    warn(`${relativePath}: marked stale while initiative current_phase is the same phase`);
  }
}

if (artifacts.implementation_plan?.status === 'current' && artifacts.shape_brief?.status !== 'current') {
  fail('initiative-map.json: implementation plan is current while shape brief is not current');
}
if (artifacts.shape_brief?.status === 'current' && artifacts.intent_brief?.status !== 'current') {
  fail('initiative-map.json: shape brief is current while intent brief is not current');
}
if (artifacts.brainstorm?.status === 'current' && artifacts.intent_brief?.status !== 'current') {
  fail('initiative-map.json: brainstorm is current while intent brief is not current');
}

for (const warning of warnings) console.warn(`WARN: ${warning}`);
for (const error of errors) console.error(`ERROR: ${error}`);

if (errors.length > 0) {
  console.error(`\nValidation failed: ${errors.length} error(s), ${warnings.length} warning(s).`);
  process.exit(1);
}

console.log(`Validation passed: ${warnings.length} warning(s).`);
