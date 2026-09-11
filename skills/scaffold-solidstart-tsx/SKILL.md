---
name: scaffold-solidstart-tsx
description: Scaffold a new small SolidStart SPA with TypeScript, TSX, pnpm, and a server-served JSON endpoint. Use for an empty or minimal repository root, or when converting a simple HTML prototype into a SolidStart project. Do not use for an established application that already has a framework structure.
---

# Scaffold SolidStart TSX

Create a working SolidStart SPA with a small typed structure. Prefer the bundled template over writing boilerplate from memory.

## Default workflow

1. Read the repository `AGENTS.md` and inspect the root before writing.
2. Preserve user files. The scaffold script stops when a template path already exists.
3. Run the script from the repository root:

   ```sh
   node <skill-directory>/scripts/scaffold.mjs --dir . --name <package-name> --title "<App title>"
   ```

4. Do not pass `--force` unless overwriting every reported path is clearly authorized.
5. Install with `pnpm install`. Use no other package manager unless the user requests it.
6. Run `pnpm typecheck` and `pnpm build`.
7. Start `pnpm dev` only when browser verification is useful.

Use `--install` to let the script run `pnpm install`. Use `--verify` to run typecheck and build after copying. Both options can be combined.

## Template contract

- The target is the repository root unless `--dir` says otherwise.
- All application source uses `.ts` or `.tsx`.
- SolidStart runs as an SPA with `ssr: false`.
- `GET /api/app-data` serves JSON from the server bundle.
- The page loads that endpoint through a typed Solid resource.
- The template uses SolidStart 1 on Node 20–22. This avoids SolidStart 2's Node 24 requirement.
- pnpm 11 build approvals live in `pnpm-workspace.yaml`.
- The script never deletes unrelated files.

## Adaptation

For file ownership and safe extension points, read [references/template-map.md](references/template-map.md).

When converting an existing single-file prototype, read [references/adapting-a-prototype.md](references/adapting-a-prototype.md). Preserve the original before splitting it.

Keep the scaffold small. Add libraries only when the requested application needs them.
