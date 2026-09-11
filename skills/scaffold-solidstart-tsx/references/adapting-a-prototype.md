# Adapt a single-file prototype

Read this reference only when an existing HTML prototype is the source.

## Preserve first

Copy or move the original file to a clear archive path before migration. A useful default is `docs/prototype/index.html`.

## Split by responsibility

- Move global CSS into `src/styles.css`.
- Move static sample data into `src/data/`.
- Move data contracts into `src/types/`.
- Move stable page regions into TSX components.
- Move direct manipulation, routing, or canvas logic into focused files under `src/lib/`.
- Replace remote script tags with package dependencies when practical.

## Keep proven behavior

Do not rewrite interaction logic only to make it look reactive. A small controller mounted from `onMount` is acceptable for a first migration.

Preserve fallback behavior before replacing a remote dependency. Test pointer interaction after moving canvas code.

## Server JSON

Put the starter JSON in `src/data/`. Import it only from the server route. Let the page request the API endpoint.

Local browser edits can remain in `localStorage` when persistence is not yet part of the product scope.
