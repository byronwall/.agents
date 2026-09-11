# Changelog

## 0.4.0 — Intent to Proof

### Added

- Integrated `intent`, optional `brainstorm`, `shape`, `plan`, `full`, `update`, and `audit` modes.
- One canonical `initiative-map.json` spanning all phases.
- Concise seven-option brainstorming format.
- Mandatory **How to make this go better** section for material work.
- Implementation-success challenge focused on smaller proof, fast local loops, narrow seams, failure injection, valid intermediate systems, and rollback.
- Dependency proof ladder covering deterministic fakes, mocks, emulators/containers, contract tests, live sandboxes, and deployed proof.
- Proof-first implementation plan format derived from thin vertical-slice principles.
- Automatic downstream invalidation after intent, shape, or repository changes.
- Non-destructive v0.3 `intent-map.json` migration.
- Structural validator and heuristic 0–10 audit.
- Full AWS SSM/Secrets Manager example and regression test.
- Concise seven-option product brainstorming example.

### Changed

- The skill now becomes more opinionated as it moves from intent interpretation to implementation strategy.
- `shape-brief.md` is a first-class canonical artifact rather than an informal continuation.
- The implementation plan owns planning quality directly; a separate task-list skill is no longer required to get proof-first milestones.
- Repository facts and external research stay in the JSON sidecar unless they materially change the human recommendation.

### Preserved from 0.3

- Concise intent brief.
- Detailed machine-readable intent map.
- Source authority and supersession discipline.
- Plain-language human frontier.
- Strong readability limits and no evidence-ledger output.

### Intentionally not integrated

- Personal daily-file locations.
- Worktree naming conventions.
- Automatic Linear publication and comment synchronization.

Those remain appropriate for a personal execution/publication skill after the portable implementation plan is approved.
