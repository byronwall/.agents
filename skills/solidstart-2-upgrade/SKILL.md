---
name: solidstart-2-upgrade
description: Upgrade a SolidStart 1 app (vinxi, app.config.ts) to SolidStart 2 on Vite 8 and Nitro v3, mainly to cut build time (visual-notes went from 292s to 49s on 2 CPUs). Use when Byron asks to upgrade, port, or migrate a repo to SolidStart 2, "drop vinxi", "move to the new SolidStart", speed up a slow `vinxi build`, or roll the upgrade across his repos. Covers config mapping, vinxi/http replacements, WebSocket routes, server-function id changes, the known build and runtime breakages, Node 24, Docker, and Coolify deploy settings.
---

# SolidStart 2 Upgrade

## Goal

Move one repo from SolidStart 1 (`@solidjs/start@1`, `vinxi`, `app.config.ts`) to SolidStart 2 (`@solidjs/start@2`, Vite 8 with Rolldown, Nitro v3). Keep the app's behavior the same. Measure the build time before and after.

Proven once, on visual-notes (PRs byronwall/visual-notes#243, #244, #246):

| | vinxi | SolidStart 2 |
|---|---|---|
| `pnpm build`, 2 CPUs / 3.8 GB container | 292s | 49s |
| Coolify build step | 457s | 166s cold |
| Coolify full deploy | 10-13 min | about 5 min |

Most of Byron's SolidStart repos come from the `solid-start-panda-park-ui` template. They share one `app/` layout, one `app.config.ts` shape, a `/ws/jobs` WebSocket router, and a `vinxi/http` middleware. Port that template once, then reuse the diff.

## Versions that worked (October 2026)

- `@solidjs/start@^2.1.0`, `@solidjs/router@^1.0.0`, `solid-js@^1.9.17`
- `vite@^8.3.5`, `vite-plugin-solid@^2.11.14` (add it as a dev dependency)
- `nitro@3.0.260903-beta`. Nitro v3 is still published as a beta. Pin the exact version.
- Node 24 or later. SolidStart 2 requires it.

Check `pnpm view @solidjs/start version` and `pnpm view nitro dist-tags` first. Use newer versions when they exist.

## Step 1: Survey the repo

Run these from the package root (usually `app/`):

```bash
rg -n "vinxi|app\.config|@solidjs/start|nitropack|h3" --glob '!node_modules' --glob '!pnpm-lock.yaml'
rg -n "from \"vinxi/http\"" src
rg -n "event\.node|eventHandler|defineMiddleware|addRouter|__websocket__" src app.config.ts
rg -n "useParams\(\)" src/routes
rg -n "^export type \{" src --glob '*.ts' --glob '*.tsx'
rg -n "import \* as .* from \"~/server" src
rg -n "node:?2[0-2]|node-version|\"node\":" Dockerfile* .github package.json README.md .nvmrc
```

Record a baseline before you change anything. See "Measure the build" below.

## Step 2: Packages and scripts

1. Remove `vinxi`, any `vinxi` patch (`patches/vinxi@*.patch` and its `patchedDependencies` entry), `nitropack`, and `@solidjs/vite-plugin-nitro-2`.
2. Remove libraries that import `vinxi` and that the app does not use. On visual-notes, Auth.js (`@solid-mediakit/auth`, `@auth/core`, `@auth/prisma-adapter`) was dead code. Nothing read its session. Check usage before you port a library.
3. Add the versions above. Set `"engines": { "node": ">=24" }`.
4. Scripts:
   - `"dev": "vite dev"` (keep any `panda codegen &&` prefix)
   - `"build": "vite build"`
   - `"start": "node .output/server/index.mjs"`
5. Delete `app.config.ts` and every `app.config.timestamp_*.js` file. Remove `app.config.timestamp_*` from `.dockerignore` and `.gitignore` if you want; it is harmless.
6. In `tsconfig.json`, remove `"vinxi/types/client"` from `types`. Keep `"vite/client"` and `"@solidjs/start/env"`.
7. Replace `vinxi` with `vite` in every script, harness, CI step, and doc (`vinxi build`, `vinxi dev`, `vinxi start`). `rg -n vinxi` must return nothing outside the lockfile.
8. Update knip or other tool entry lists from `app.config.ts` to `vite.config.ts`.

## Step 3: `vite.config.ts`

Map `app.config.ts` like this:

| SolidStart 1 (`app.config.ts`) | SolidStart 2 (`vite.config.ts`) |
|---|---|
| `defineConfig` from `@solidjs/start/config` | `defineConfig` from `vite`; `solidStart()` from `@solidjs/start/config` |
| `vite: { plugins, optimizeDeps, ... }` | top-level Vite options and `plugins` |
| `vite-tsconfig-paths` plugin | `resolve: { tsconfigPaths: true }` (built into Vite 8) |
| `middleware: "./src/middleware.ts"` | `solidStart({ middleware: "./src/middleware.ts" })` |
| `server: { preset, prerender, baseURL, ... }` | `nitro({ preset, prerender, baseURL, ... })` from `nitro/vite` |
| `server: { experimental: { websocket: true } }` | `nitro({ features: { websocket: true } })` |
| `.addRouter({ base: "/ws/jobs", handler: "./src/ws/jobs.ts" })` | `nitro({ routes: { "/ws/jobs": "./src/ws/jobs.ts" } })` |
| `build.rollupOptions` | `build.rolldownOptions` |

The visual-notes config, which works in dev and production:

```ts
import { solidStart } from "@solidjs/start/config";
import { nitro } from "nitro/vite";
import { defineConfig } from "vite";

export default defineConfig({
  resolve: { tsconfigPaths: true },
  // vinxi read PORT and HOST; CI, Playwright, and harnesses still set them.
  server: {
    port: Number(process.env.PORT) || 3000,
    host: process.env.HOST,
    strictPort: Boolean(process.env.PORT),
  },
  plugins: [
    solidStart({ middleware: "./src/middleware.ts" }),
    nitro({
      preset: "node-server",
      features: { websocket: true },
      routes: { "/ws/jobs": "./src/ws/jobs.ts" },
    }),
  ],
});
```

- The `server` block matters. Vite does not read `PORT` or `HOST`, and its default port is 5173. Without the block, CI dev smokes, Playwright, and dev scripts that set `PORT` connect to nothing.
- Put other Vite plugins (lucide preprocess, solid-devtools, custom `define` plugins) before `solidStart()`.
- The official guide shows Nitro options as a top-level `nitro` property. Passing them to `nitro({...})` also works, and visual-notes uses that form.
- `baseURL` and `prerender` are not yet proven in one of Byron's repos. Build, then check the prerendered files and the asset URLs under the base path.

## Step 4: Server code

Read [references/code-patterns.md](references/code-patterns.md) for before/after code. Summary:

- **`vinxi/http` imports** move to `@solidjs/start/http` (`getCookie`, `setCookie`, `deleteCookie`, `useSession`, `getRequestHeader`, `setResponseHeader`, `readBody`, `getQuery`). Nitro v3 uses h3 v2, which uses Web `Request`, `Response`, and `Headers`. `event.node.req` and `event.node.res` are gone; use `event.request` / `event.req` and return a `Response`.
- **Middleware** uses `createMiddleware` from `@solidjs/start/middleware`. Replace `defineMiddleware` from `vinxi/http`. Prefer the array form: `onRequest: [async (event) => { ... }]`.
- **WebSocket routes** use `defineWebSocketHandler` from `nitro`. The hooks (`upgrade`, `open`, `message`, `close`, `error`) do not change. Type a peer with `import type { WebSocketPeer } from "nitro/h3"`. Remove the old `Parameters<typeof eventHandler>[0]["__websocket__"]` type gymnastics.
- **Nitro handlers** use `defineHandler` from `nitro`, not `eventHandler` or `defineEventHandler`. Return bodies directly; the `send*` helpers are gone.

## Step 5: Known breakages

Each one below broke visual-notes. Search for each one in every repo.

1. **Server-function ids are opaque hashes.** v1 ids were readable (`src_services_auth_magic-auth_actions_ts--magicLogin_action`). v2 ids are `<module hash>-<name hash>`; the name half is xxHash32 of the function name, and dev uses the plain name. Any hard-coded id list (an auth allowlist for public functions, e2e helpers that match `X-Server-Id`) silently stops matching. On visual-notes, sign-in returned 401. Fix: read the id from the server reference (`fn.url` holds `/_server?id=...`). Never hard-code ids. For e2e matching by name, use the xxHash32 helper in the reference.
2. **Type re-exports in `"use server"` modules.** `import { type X } from "..."` then `export type { X }` fails the build. The new server-function transform drops the import. Re-export from the source: `export type { X } from "~/lib/x/types";`.
3. **Server code in the browser bundle.** A namespace import of a server module, used at module top level in an actions file (`import * as store from "~/server/store"; const { fn } = store;`), keeps the whole module in the client. Prisma's runtime then ships to the browser, and the page crashes with `promisify is not a function` only when it runs. Fix: use named imports, and reference server modules only inside `"use server"` bodies. Add a CI guard after the build:

   ```bash
   ! grep -rlE 'prisma:get-platform|PrismaClient' .output/public/_build
   ```

   Change the pattern for the repo's server-only libraries (database drivers, `node:` modules).
4. **Router 1.0 types params as optional.** `useParams()` now gives `string | undefined`. Type the route: `useParams<{ id: string }>()`.
5. **Vitest and `server-only`.** The SolidStart Vite plugin provides a virtual `server-only` module. Vitest does not load that plugin. Add an alias to an empty stub, and inline `@solidjs/start` so the alias reaches it:

   ```ts
   test: { server: { deps: { inline: [/@solidjs\/start/] } } },
   resolve: { alias: { "server-only": resolve(__dirname, "src/test/server-only.ts") } },
   ```

   The stub file contains only `export {};`.
6. **Serialization defaults to JSON.** Server-function payloads use JSON, not v1's JS format. Dates, Maps, and class instances that crossed the wire before may arrive as strings or plain objects. Test a few server functions that return those types. Use `solidStart({ serialization: { mode: "js" } })` only if a real payload breaks.
7. **Vite dev first run.** A cold `vite dev` can answer 504 "Outdated Optimize Dep" once and reload while it pre-bundles. This is expected. Wait for the reload before you judge the dev server.

## Step 6: Node 24 everywhere

Change every pin in one commit: `Dockerfile` (`node:24-bookworm-slim`), CI `setup-node` (`node-version: 24`), `.nvmrc`, `engines`, and README setup steps. CI must use the same major version as Docker.

## Step 7: Docker and Coolify

Most of Byron's repos deploy with Docker on Coolify. Read [references/docker-coolify.md](references/docker-coolify.md). The deploy-time gains came from these changes as much as from the faster build:

- A multi-stage Dockerfile. The runtime stage copies only `.output` (Nitro bundles its server dependencies), not the full dev `node_modules`. That cut visual-notes from 1.68 GB to 877 MB.
- BuildKit cache mounts for the pnpm store, and a dependency layer keyed only on `package.json` and `pnpm-lock.yaml`.
- `.dockerignore` must exclude `docker-compose*.yml`. Coolify rewrites it on every deploy.
- Coolify settings: Docker Cleanup on the disk-threshold trigger, not forced hourly. Buildtime off on env vars the build does not read.
- Do not reference `${SOURCE_COMMIT}` in `docker-compose.yml`.

## Step 8: Verify

Run the repo's checks one at a time (lint, type-check, tests). Then check these by hand or with Playwright, on both `vite build && pnpm start` and `vite dev`:

- Every route renders and hydrates with no console errors.
- Sign-in works. Signed-out requests get 401 or a redirect, and public server functions still run without a session.
- Each server action that writes data works through the UI.
- Each WebSocket route accepts a connection and sends its first message. An unauthenticated upgrade is refused.
- The client bundle has no server-only library (the CI guard above).
- The Docker image starts, runs migrations, and passes its healthcheck.

## Measure the build

Measure in a container sized like the deploy server, not on the Mac. A Mac build is several times faster and hides the difference:

```bash
docker build --target build --no-cache --progress=plain -t build-bench . 2>&1 | tee tmp/build-bench.log
```

To cap the build resources, run the build inside a capped container instead, for example `docker run --rm --cpus=2 --memory=3.8g -v "$PWD":/src -w /src node:24-bookworm-slim sh -c 'corepack enable && pnpm install --frozen-lockfile && time pnpm build'`. Copy the source to a temporary folder first if the mounted `node_modules` belongs to macOS. Report the old and new numbers in the PR.

## PR shape

Split the work into a stack (see the `gh-stack` skill):

1. Docker image and cache fixes. They do not depend on the upgrade.
2. The SolidStart 2 port: config, Node 24, vinxi removal, and the breakages above.
3. Follow-ups found in CI or on the first deploy.

In the PR body, give the build-time table, the list of breakages fixed, and what was not run (for example, e2e tests left to CI). Name Nitro's beta status as a risk.
