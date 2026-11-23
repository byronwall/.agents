# Inspection checklists

Use these to fill the boundary card. They are prompts, not a form: write down only the rows that apply to this change, and one line on why a whole family doesn't.

## Contents

- Boundary card template
- Actors people forget
- Input variation catalog
- Implicit-assumption families
- Fault seams and how to inject them
- Where failures show up

## Boundary card template

```markdown
# Boundary: <change> at <sha>

## How to run it
- Command, working directory, config files and environment it reads; how to run the same probe on base

## Entry points
- <route / message / CLI / job / config> — driven by <actor> — reaches <changed function> via <path:line>
- Selected by: <flag / config / deploy template that picks this path> (<path:line>)

## Inputs and variations considered
| Input | Variations that apply | Not applicable, and why |

## Outputs and where each is observed
| Output | Destination | What to look at (UI text, query, log event, span, status) |

## Implicit assumptions
- <assumption> — relied on at <path:line> — broken by <condition>

## Fault seams
| Seam | Inject by | Observed at |
```

## Actors people forget

- The same user in a **second tab** or window, or on a second device.
- A **second user** in the same workspace, model, account or file.
- A **retry**: the client, a proxy, a queue redelivery, the user double-clicking.
- An **old client** talking to a new server, or the reverse, during a rolling deploy.
- A **scheduled job**, background loop or webhook running while a person acts.
- An **agent or script** calling an API that was designed for a UI.
- An **operator** running a migration, a backfill, a restart or a config change.
- Someone **untrusted** who can reach the input: a web page in the user's browser, a LAN peer, a tenant in a shared service.

## Input variation catalog

Pick what fits the input's type. For each, ask what the code does, not just whether it errors.

- **Absence:** missing, null, empty string, empty list, zero, field present but blank.
- **Multiplicity:** duplicated item, duplicated header or key, the same request twice, one item vs many.
- **Size:** one more than a limit, a very long string, a huge list, a deep nesting.
- **Accumulation:** what grows when the same path runs again: history re-sent each turn, a transcript a tool loop extends, a retry or recovery that replays earlier input, pages fetched into one list, a batch that grows with the customer. Count it in the unit the limit names (per request, per message, per minute, per account), not the unit the code builds in, and probe the call where it first crosses.
- **Shape:** wrong type, an extra unknown field, an old schema version, a new enum value the code doesn't know.
- **Encoding and case:** Unicode, mixed case, trailing dot or slash, whitespace, percent-encoding, a different but equivalent spelling (`localhost` vs `127.0.0.1` vs `::1`).
- **Boundaries of meaning:** the value at the edge of a range, a time at midnight or across a DST change, a negative or a future date.
- **Reference validity:** an ID that doesn't exist, was deleted, belongs to someone else, or was renamed.
- **Order:** the same inputs in a different order; an update before its create; a reply before its request.
- **Source:** the same input from a different actor or network position (loopback vs LAN vs proxy).

## Implicit-assumption families

Each of these is something internals often rely on without checking. Name the code that relies on it.

- **Ordering:** event A arrives before B; a list is sorted; a migration ran.
- **Single writer:** only one request, process or tab changes this at a time; a read-modify-write is not interleaved.
- **Idempotence:** running it twice is the same as once (retries, redelivery, double-click).
- **Atomicity:** both writes land or neither does; a crash between them leaves a consistent state.
- **Timing:** a call returns within a timeout; a cache is fresh enough; a timer fires before the next request.
- **Presence:** a config value, a file, a connection, a parent record or a user session exists.
- **Lifetime:** the process stays up for the whole flow; a connection isn't dropped mid-stream; a page isn't reloaded.
- **Locality:** one process per host, one host per user, state in memory is the only copy.
- **Trust:** the caller is who it says; a header wasn't set by someone else; data from storage wasn't written by an older version.
- **Exhaustiveness:** every consumer handles every kind the producer can emit. List the kinds from the type definitions (each union member, enum value, spec type), then check each consumer: an unpack that expects exactly one result, a `match` with no default, a renderer with no case for the new kind.
- **Consistency:** two outputs that describe the same fact are built by different code and agree. A tint from the cell's role and a tooltip from the claim's verdict; a count from one query and the list from another; a status badge and the log line. Feed one input that the two derivations treat differently.
- **Resource:** there's a free slot in a pool or limiter; a disk or memory isn't full; a rate limit isn't hit.

## Fault seams and how to inject them

| Seam | Inject by |
| --- | --- |
| Process lifetime | `kill -TERM` or `kill -9` mid-flow; restart the server while a client is connected |
| Network | drop the connection (close the socket, stop the proxy), add delay, block a host |
| Dependency | make a downstream call fail, time out or return an unexpected shape (stub, env var pointing at a dead port, revoked credential in a scratch account) |
| Concurrency | two clients or tasks gated on the same event; two tabs clicking at once; a script firing N requests in parallel |
| Ordering | deliver messages out of order; run step 2 before step 1 by calling the API directly |
| State | start from an empty store, a store written by an older version, a half-finished migration, a stale cache |
| Config | unset a variable, set two conflicting ones, use each deploy target's real template |
| Clock | freeze or jump the clock in a test; shrink a timeout to force the slow path |

Inject faults only in a local or scratch environment you control. Never against shared or production systems without explicit permission.

## Where failures show up

A candidate is only useful if you know where to look. For each output, name the destination and the exact observation:

- **UI:** the text, state or element a user sees (screenshot it).
- **API:** status code and body (save the raw response).
- **Storage:** the row, file or object, with the query that reads it.
- **Logs:** the event name and fields; check the level.
- **Traces and metrics:** the span or metric name and the query in the observability tool.
- **Another service:** what it received, from its own log or a captured request.

A failure no output shows is a **silent** failure. Say so: it raises the harm, and it usually means a test gap too.
