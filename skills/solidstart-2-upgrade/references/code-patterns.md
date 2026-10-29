# Code patterns: SolidStart 1 to 2

Before/after code from visual-notes, plus the shapes found in the `solid-start-panda-park-ui` template.

## WebSocket route (template `src/ws/jobs.ts`)

Before:

```ts
import { eventHandler } from "vinxi/http";

type Peer = Parameters<
  NonNullable<
    NonNullable<Parameters<typeof eventHandler>[0]["__websocket__"]>["open"]
  >
>[0];

export default eventHandler({
  handler() {},
  websocket: {
    open(peer) { /* ... */ },
    message(peer, payload) { /* ... */ },
    close(peer) { /* ... */ },
  },
});
```

After:

```ts
import { defineWebSocketHandler } from "nitro";
import type { WebSocketPeer as Peer } from "nitro/h3";

export default defineWebSocketHandler({
  upgrade(request) {
    // Middleware does not run for Nitro routes. Check auth here.
    if (!isAuthed(request)) throw new Response("Unauthorized", { status: 401 });
  },
  open(peer) { /* ... */ },
  message(peer, payload) { /* ... */ },
  close(peer, details) { /* ... */ },
  error(peer, error) { /* ... */ },
});
```

Register it in `vite.config.ts`: `nitro({ features: { websocket: true }, routes: { "/ws/jobs": "./src/ws/jobs.ts" } })`.

The Nitro route is a separate bundle from the app. Module-level state is not shared with app code. visual-notes shares events through `globalThis` plus a `BroadcastChannel`, which works across both bundles. Check how the socket gets its events before you move it.

## Middleware (template `src/middleware.ts`)

Before (vinxi, h3 v1, Node request objects):

```ts
import { defineMiddleware } from "vinxi/http";

export default defineMiddleware({
  onRequest: (event) => { event.context.startedAt = Date.now(); },
  onBeforeResponse: async (event, response) => {
    const url = new URL(event.node.req.url ?? "/", "http://localhost");
    const cookie = event.node.req.headers.cookie;
    const status = event.node.res.statusCode;
    // ...
  },
});
```

After (h3 v2, Web request objects). visual-notes uses this form in production:

```ts
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: [
    async (event) => {
      const url = new URL(event.request.url);
      const cookie = event.request.headers.get("cookie");
      if (!allowed(event.request)) {
        return new Response("Unauthorized", { status: 401 });
      }
    },
  ],
});
```

The template's `onBeforeResponse` analytics hook reads `event.node.res`. That hook is not yet ported in any repo. Port it with h3 v2 response hooks from the h3 and SolidStart 2 docs, and test that the analytics rows still record status and byte counts.

## `vinxi/http` helpers

```ts
// Before
import { setCookie, deleteCookie, setHeader } from "vinxi/http";
// After
import { setCookie, deleteCookie, setResponseHeader } from "@solidjs/start/http";
```

`setHeader` is `setResponseHeader` in h3 v2. `sendRedirect` is gone: return `Response.redirect(url, 302)` or a router `redirect()`.

## Public server functions by reference

Before (breaks in v2, because ids are hashes):

```ts
const publicServerFunctionIds = new Set([
  "src_services_auth_magic-auth_actions_ts--magicLogin_action",
]);
```

After (`src/server/public-server-fns.ts`):

```ts
import { loginWithMagicPassword } from "~/services/auth/magic-login";

// SolidStart gives each server function an opaque id; the server reference
// carries it in `.url` (`/_server?id=...`).
const publicServerFunctions: unknown[] = [loginWithMagicPassword];

export const publicServerFunctionIds = new Set(
  publicServerFunctions.flatMap((fn) => {
    const url = (fn as { url?: string }).url;
    const id = url && new URL(url, "http://local").searchParams.get("id");
    return id ? [id] : [];
  }),
);
```

The function must be a named `"use server"` export. Wrap it in `action()` or `query()` in the actions file: `export const magicLogin = action(loginWithMagicPassword, "magic-login");`. Log an error at startup when the set is smaller than the list, so a broken lookup does not lock everyone out.

## E2E: match a server function by name

v2 ids are `<module hash>-<name hash>`. The name half is xxHash32 (seed 0, UTF-8) of the function's own name, in hex. In dev it is the plain name. Copy `app/tests/e2e/helpers/server-fn-id.ts` from visual-notes (`isServerFn(serverId, "createDoc")`), and pin the hash with a unit test against an id read from a real build.

## Type re-exports in `"use server"` modules

```ts
// Before: build fails, the transform drops the inline type import
import { type CollectionProperty } from "~/lib/collections/types";
export type { CollectionProperty };

// After
export type { CollectionProperty } from "~/lib/collections/types";
```

## Namespace imports of server modules in action files

```ts
// Before: keeps the whole store (and Prisma) in the client bundle
import * as store from "~/server/time-blocks/time-block-store";
const { normalizeRange } = store;

// After
import { normalizeRange, updateTimeBlock as updateTimeBlockInStore } from "~/server/time-blocks/time-block-store";
```

## Route params

```ts
const params = useParams<{ id: string }>();
```
