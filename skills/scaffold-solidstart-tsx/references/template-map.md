# Template map

Read this reference when the generated structure needs customization.

## Root files

- `app.config.ts`: SolidStart SPA configuration.
- `package.json`: pnpm scripts and Node 20–22 dependencies.
- `pnpm-workspace.yaml`: pnpm 11 dependency build approvals.
- `tsconfig.json`: strict TypeScript and TSX settings.
- `.gitignore`: generated dependency and build directories.
- `README.md`: short local setup instructions.

## Application files

- `src/app.tsx`: router and global stylesheet entry.
- `src/entry-client.tsx`: client mount.
- `src/entry-server.tsx`: HTML document and server handler.
- `src/routes/index.tsx`: typed client request and page state.
- `src/routes/api/app-data.ts`: JSON server endpoint.
- `src/components/AppShell.tsx`: first reusable TSX component.
- `src/types/app-data.ts`: shared client and server contract.
- `src/data/app-data.json`: server-owned starter content.
- `src/styles.css`: minimal responsive styles.

## Safe extension points

- Add API routes under `src/routes/api/`.
- Add page routes under `src/routes/`.
- Add domain types under `src/types/`.
- Keep server-owned starter data under `src/data/`.
- Split large surfaces into `src/components/`.

Do not add a root `index.html`. SolidStart owns the HTML document through `src/entry-server.tsx`.
