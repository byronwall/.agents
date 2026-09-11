---
name: pnpm-11-upgrade
description: Upgrade JavaScript and TypeScript repositories to pnpm 11 compatibility. Use when a repo is moving to pnpm 11, pnpm reports that package.json#pnpm settings are ignored, patchedDependencies stop applying, ERR_PNPM_IGNORED_BUILDS appears, build-script approvals are needed, Corepack/Docker pins are stale, or a reusable pnpm 11 migration checklist is requested.
---

# pnpm 11 Upgrade

## Goal

Migrate a repo to pnpm 11 while keeping the change set narrow. Preserve unrelated worktree changes, avoid unnecessary installs, and move pnpm policy into the pnpm 11 settings file.

## First Pass

1. Inspect current state with read-only commands first:
   - `rg -n "pnpm|packageManager|patchedDependencies|onlyBuiltDependencies|ignoredBuiltDependencies|neverBuiltDependencies|ignoreDepScripts|allowBuilds|approve-builds|pnpm@" .`
   - `rg --files -g "package.json" -g "pnpm-workspace.yaml" -g ".npmrc" -g "pnpm-lock.yaml" -g "Dockerfile" -g "*.md"`
   - `git status --short`
2. Identify the package root. In single-package repos this is usually the repo root. In nested apps, it is the directory with `package.json` and `pnpm-lock.yaml`.
3. Check whether there are unrelated uncommitted changes. Do not overwrite or stage them. If mixed files must be committed later, stage only the pnpm hunks.

## Required Migration Edits

### Move `package.json#pnpm` Settings

pnpm 11 no longer reads settings from the `pnpm` field in `package.json`. Move settings to `pnpm-workspace.yaml` at the pnpm project root.

Common move:

```json
"pnpm": {
  "patchedDependencies": {
    "pkg@1.2.3": "patches/pkg@1.2.3.patch"
  }
}
```

becomes:

```yaml
patchedDependencies:
  "pkg@1.2.3": patches/pkg@1.2.3.patch
```

Then remove the `pnpm` object from `package.json`. Keep valid JSON and preserve all non-pnpm fields.

### Replace Removed Build-Script Settings

pnpm 11 replaced older build-script settings with `allowBuilds`:

```yaml
allowBuilds:
  esbuild: true
  "@parcel/watcher": true
  unrs-resolver: true
```

Migration map:

- `onlyBuiltDependencies` entries usually become `allowBuilds.<name>: true`.
- `ignoredBuiltDependencies` and `neverBuiltDependencies` entries usually become `allowBuilds.<name>: false`.
- `ignoreDepScripts` should not be blindly replaced with `dangerouslyAllowAllBuilds`; review the actual packages.

If pnpm has inserted placeholders such as `set this to true or false`, replace each placeholder intentionally with `true` or `false`. Approve only packages expected to run install scripts, such as native binary tooling already present in the lockfile. Avoid `dangerouslyAllowAllBuilds` unless the user explicitly accepts the supply-chain risk.

### Pin pnpm 11

Add or update the package manager pin at the package root:

```json
"packageManager": "pnpm@11.9.0"
```

Use the user’s installed target version when known. If unknown, ask or use the current pnpm 11 version already evidenced in the task/logs. Do not bump application semver solely because the package manager pin changes unless repo policy requires it.

### Update Runtime Pins

Search Dockerfiles, CI, devcontainers, setup scripts, and docs for old pnpm pins. Replace stale Corepack activation such as:

```dockerfile
RUN corepack enable && corepack prepare pnpm@9.12.3 --activate
```

with the target pnpm 11 version.

If a build command uses `--ignore-scripts`, keep it unless the repo has a reason to run scripts during image install. `allowBuilds` mainly affects installs where dependency scripts are allowed to run.

### Copy pnpm 11 Project Settings Into Docker Install Layers

When a Dockerfile runs `pnpm install` before copying the full app source, make sure that install layer copies `pnpm-workspace.yaml` along with `package.json` and `pnpm-lock.yaml`.

For example, this is incomplete after moving pnpm 11 settings out of `package.json`:

```dockerfile
COPY package.json pnpm-lock.yaml ./
COPY patches ./patches
RUN pnpm install --frozen-lockfile --ignore-scripts
```

Use:

```dockerfile
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY patches ./patches
RUN pnpm install --frozen-lockfile --ignore-scripts
```

This matters when `pnpm-workspace.yaml` contains settings such as `patchedDependencies`, `allowBuilds`, `packageManagerStrictVersion`, or `verifyDepsBeforeRun`. Without the workspace settings file present, container builds can fail during `pnpm install --frozen-lockfile`, especially when the lockfile references patched dependencies.

## Lockfile Handling

Do not edit lockfiles manually unless the user explicitly asks for a no-command metadata-only patch. Prefer having pnpm 11 regenerate lockfile metadata. Expected pnpm 11 lockfile changes may include:

- `patchedDependencies` changing from nested `{hash, path}` entries to direct hash values.
- `patch_hash=` suffixes changing from short hashes to longer hashes.
- additional platform metadata such as `libc`.
- new deprecation metadata from registry refresh.

If the user asks not to run pnpm commands, make only config/docs edits and tell them to run the install/dev command locally. If they already ran pnpm 11 and the lockfile changed, include the lockfile in the pnpm 11 commit after reviewing that the diff is package-manager metadata, not dependency drift.

## Verification

Keep verification proportional to the user’s constraints.

No-pnpm verification:

- Parse changed `package.json` files with Node: `node -e "JSON.parse(require('fs').readFileSync('path/package.json','utf8'))"`.
- Search for stale settings: `rg -n "package.json#pnpm|onlyBuiltDependencies|ignoredBuiltDependencies|neverBuiltDependencies|ignoreDepScripts|set this to true or false|pnpm@9|pnpm@10" .`.
- Inspect staged or working diff manually.

Full verification when allowed:

- Run the repo’s normal install or dev command with pnpm 11.
- Run the repo’s normal final checks, not a broad build, unless repo guidance asks for build verification.
- For Docker pin changes, build only if the user asks or repo policy requires it.

## Documentation Updates

Update only docs that future maintainers will actually read:

- root README or app README prerequisites: note pnpm 11 and the pinned version.
- agent/contributor guidance: say pnpm 11 settings live in `pnpm-workspace.yaml`, not `package.json#pnpm`.
- deployment docs when Docker/Corepack pins change.
- changelog only if repo policy says tooling/config changes must be logged.

Avoid touching historical docs, old run logs, or unrelated plans unless they are current setup instructions.

## Commit Hygiene

When asked to commit only pnpm 11 work:

1. Review `git status --short` and `git diff` first.
2. Stage exclusively pnpm-related files or hunks.
3. For mixed files, use index-only patch staging (`git add -p` or `git apply --cached`) so unrelated user changes remain unstaged.
4. Run `git diff --cached --check`.
5. Commit with a message like `Update pnpm 11 project settings`.
6. Report the commit hash and list any remaining unstaged files at a high level.

Never revert unrelated changes to make staging easier.

## Common Interpretation

- Browserslist/caniuse-lite warnings are unrelated to pnpm 11 migration unless the user specifically asks to refresh browser data.
- `ERR_PNPM_IGNORED_BUILDS` is usually fixed with `allowBuilds`, not by disabling strictness globally.
- `pnpm approve-builds` is an interactive helper that writes `allowBuilds`; for automation, editing `pnpm-workspace.yaml` directly is often clearer after reviewing the packages.
- `.npmrc` is no longer the home for most pnpm settings in pnpm 11; use `pnpm-workspace.yaml` or trusted global config for non-project secrets.
