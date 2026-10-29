# Docker and Coolify

What made visual-notes deploys fast on Coolify (2 CPUs, 3.8 GB). Apply these with the upgrade, or before it as their own PR.

## Dockerfile shape

```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:24-bookworm-slim AS os
RUN apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app

FROM os AS base
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable && corepack prepare pnpm@<pinned> --activate

FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
  pnpm install --frozen-lockfile

FROM deps AS build
COPY . .
RUN pnpm build

FROM os AS runtime
ENV NODE_ENV=production
COPY --from=build /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

- The runtime stage copies only `.output`. Nitro bundles the server dependencies there. Do not copy `node_modules`.
- Prisma: `.output` carries the generated client and engine. `prisma migrate deploy` at start needs only the CLI. Install it alone in a small stage at the same version (`pnpm add prisma@<version>` with `--config.node-linker=hoisted`) and copy that folder into runtime.
- Put slow, rarely changed installs (Python venvs, apt packages) before `COPY . .` and before the app files in runtime, so a commit does not reinstall them.
- Add a healthcheck with a long `start_period` when migrations run before the server listens.

## `.dockerignore`

Exclude at least: `node_modules`, `.output`, `.vinxi`, `.git`, `.env`, `.env.*`, `Dockerfile`, `docker-compose*.yml`, `tmp`, test output, and generated folders the build recreates.

Coolify rewrites `docker-compose.yml` in the build folder on every deploy. If the compose file is in the build context, `COPY . .` misses the cache even on a redeploy of the same commit.

## Coolify settings

Check these through the Coolify API (`/api/v1`, token in `~/.config/coolify/coolify.env`) or the UI. Get Byron's approval before you change one.

- **Docker Cleanup:** use the disk-threshold trigger (visual-notes uses 85%) with Force off. A forced hourly cleanup runs `docker builder prune -af`, which deletes the build cache, so no deploy reuses a layer. The API rejects these fields (422); change them in the UI.
- **Env vars:** turn Buildtime off for every var the build does not read. Coolify adds each Buildtime var as an `ARG` after every `FROM`, so a changed value misses the cache for every later `RUN`. The API update needs each var's value, so use the UI unless the token can read values. Coolify-managed vars (`SERVICE_URL_*`, `SERVICE_FQDN_*`, database vars made from the compose file) cannot be changed; that is fine.
- **"Include Source Commit in Build":** leave it off. It adds the commit as an `ARG` to every stage and breaks the cache on every commit.
- The deploy endpoint is `POST` in Coolify 4.5.

## Deployed commit (`SOURCE_COMMIT`)

Coolify writes `SOURCE_COMMIT=<sha>` to the runtime `.env` and adds `env_file: .env` to every compose service. Read `process.env.SOURCE_COMMIT` at runtime.

- Do not write `SOURCE_COMMIT: ${SOURCE_COMMIT:-}` in `docker-compose.yml`. Coolify creates an app env var for each `${VAR}` in the compose file. When an app env var named `SOURCE_COMMIT` exists, Coolify does not write the real one, so the value is empty.
- If such a var already exists, remove the compose reference, deploy, delete the stored `SOURCE_COMMIT` entries (production and preview), and deploy again.
- Do not read `.git` in the image. Coolify runs `rm -fr <basedir>/.git` before a compose build.

## Measured on visual-notes

| | Before | After |
|---|---|---|
| Image | 1.68 GB | 877 MB |
| Build step on Coolify | 457s | 166s cold, 216s warm with a new app build |
| Build args injected | 92 | 18 |
| Full deploy | 10-13 min | about 5 min |
| Same-commit redeploy | everything rebuilt | 64s total, after the `.dockerignore` rule |
