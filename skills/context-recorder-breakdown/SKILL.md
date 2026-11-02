---
name: context-recorder-breakdown
description: Break down a Context Recorder session (a folder under ~/Movies/ContextRecorder/ with recording.mp4, marks, transcript, browser events and saved pages) into actionable output — an exhaustive categorized feedback list, fix-now changes plus a future-ideas doc, intent documents, or one Jira/Linear issue with annotated images. Covers every file the recorder writes, the three clocks and how to convert between them, and how to join a Modeler / Rel app walkthrough with the deployed revision, the source code and Observe telemetry. Use when Byron gives a ContextRecorder path ("Path = …/ContextRecorder/2026-…", "I recorded a session", "process my voiceover", "usability run", "walkthrough feedback") or a context-recorder-cloud link.
---

# Context Recorder breakdown

Byron records walkthroughs with his Context Recorder app (`/Users/byronwall/repos/context-recorder`, README is the format spec). He narrates while using an app and presses a hotkey to mark moments. Your job is to turn the session into the artifact he asked for without losing a single comment.

## 1. Inputs

- **Session folder:** `~/Movies/ContextRecorder/<YYYY-MM-DD_HH-MM-SS>/`. The folder name is **local time** (US Eastern), not UTC.
- **Cloud copy (optional):** `exports/cloud.json` holds `url` (`https://context-recorder-cloud.byron-711.workers.dev/s/<session>/`). Agents can read pushed sessions through its MCP (`claude mcp add --transport http sessions <cloud-url>/mcp`); the local folder is the source of truth.
- **Byron's ask:** decides the output shape (section 6). Re-read his pasted request for categories, recipients and companions ("combine with Ilian's PR feedback", "check Observe").

## 2. What's in the folder

| File | Use it for | Trust |
| --- | --- | --- |
| `session.md` | Start here. One `##` per mark: number, offset, title (the sentence the mark landed in), image, narration window (20 s before, 10 s after, `⚑` = mark), app/window/URL, element under mouse, saved page, recent clicks. | Good summary; the title is just the nearest sentence. |
| `transcript.json` | `{text, sentences:[{start,end,text}]}` in session time. **Read every sentence**; Byron often comments without marking. | Parakeet ASR: names and jargon get mangled ("Alien" = Ilian, "Sourcely" = Srcly). |
| `marks.jsonl` | Raw marks: `index`, `kind` (`mark` = full frame, `screenshot` = region), `offsetSeconds`, `wallTime` (UTC), `context`, `browser` (`hovered`, `focused`, `region.elements`, `recent` last 40 events, `url`, `title`, `pageFile`). `"source":"review"` marks were added afterwards. | `browser.*` is reliable; see `context` caveat below. |
| `frames/NNN.jpg` | Full-screen frame for every mark (from the video). | |
| `screenshots/NNN.png` | Region shot for `screenshot` marks — usually the clearest image. | |
| `annotations/*.png` | Byron's own markup, already flattened. Prefer these. | |
| `browser.jsonl` | Chrome extension events, `{event:{kind,t(epoch ms),url,tabId,…}, offsetSeconds}`. Kinds: `click` (selector, text, attrs), `nav`, `console` (`level`, `message`), `error` (uncaught/rejection with `stack`), `request` (only failed or slow ones: `status`, `ms`, `requestUrl`, first 800 chars of an error body). | Covers **every tab**: filter by the tested `tabId`/host. |
| `activity.jsonl` | Front app/window/Chrome-tab changes. | `context.browserURL` comes from AppleScript and can name a **different tab** than the one on screen. |
| `pages/m<N>-<s>.mhtml` | Saved DOM for marks made in Chrome. Open in Chrome or grep it for text, `data-*`, component names. | |
| `recording.mp4` | 15 fps video with audio. Pull extra frames for unmarked moments. | |
| `session.json` | Everything above merged, in edited time, plus `segments` and `hiddenMarks`. | |
| `edits.json`, `session-info.json` | Cuts/joins and a custom name. A joined session has only these plus `session.*`/`marks/`; its media lives in the `source` folders. | |
| `viewer.html` | Portable viewer; give Byron this link for review. | |
| `process.log` | Processing errors (e.g. transcription failed). | |
| `canvas.json`, `canvas/` | Stitched scroll columns, if built. | |

Ignore `*.sb-*` sidecar files and `audio.wav`.

## 3. Clocks

- **Session offset** (`offsetSeconds`, transcript `start`): seconds into the (edited) session. Use `m:ss` offsets when citing.
- **UTC:** `recording start = mark.wallTime − mark.offsetSeconds`. `browser.jsonl` `t` is epoch ms. Observe needs UTC.
- **Joined/edited sessions:** `session.json.segments` = `[{source, start, end, editedStart}]`. Video time in a source = `offset − editedStart + start`. Each mark keeps `sourceSession` and `sourceOffsetSeconds`. Write the segment table into the output so offsets can be found in the right `recording.mp4`.

Quick orientation:

```bash
S=~/Movies/ContextRecorder/<session>
python3 - "$S" <<'EOF'
import json, sys, collections, datetime as dt
S = sys.argv[1]
s = json.load(open(f"{S}/session.json"))
m = s["marks"]
t0 = dt.datetime.fromisoformat(m[0]["wallTime"].replace("Z", "+00:00")) - dt.timedelta(seconds=m[0]["offsetSeconds"]) if m else None
print("duration", round(s["duration"]), "s; marks", len(m), "; sentences", len(s["transcript"]), "; start UTC", t0)
print("segments", s["segments"])
hosts = collections.Counter((e["event"].get("url") or "").split("#")[0] for e in s["browser"])
print("hosts", hosts.most_common(5))
kinds = collections.Counter(e["event"]["kind"] for e in s["browser"]); print("events", kinds)
for e in s["browser"]:
    ev = e["event"]
    if ev["kind"] == "error" or (ev["kind"] == "request" and (ev.get("status") or 0) >= 400) or (ev["kind"] == "console" and ev.get("level") == "error"):
        print(round(e["offsetSeconds"]), ev["kind"], ev.get("status"), (ev.get("message") or ev.get("requestUrl") or "")[:140])
EOF
```

## 4. Workflow

1. **Establish what was tested.** Host from `browser.jsonl`/`mark.browser.url` (not `activity`), the model from the URL hash (`#model=FLIGHTS_REASONERS&layout=map&modelVizSelection=<id>`), and the deployed revision (section 5). If the image and metadata disagree, say so; don't guess.
2. **Read the whole transcript, then every mark.** Build one row per distinct comment: offset range, what Byron said (his words, cleaned), what he expected, mark numbers and images, and evidence from the page (selector, `aria-label`, failed request, console error). Unmarked comments are items too; mark them "(seen in video, not marked)" when you pull a frame for them. Visible problems Byron didn't mention are "(seen, not narrated)".
3. **Look at the images.** Read each frame/screenshot rather than trusting the title. For moments without a mark, or motion bugs (flashing, jumps), pull frames: `ffmpeg -loglevel error -ss <sec> -i recording.mp4 -frames:v 1 -q:v 3 out.jpg` (a pair or a short burst `-vf fps=5 -t 2` shows the change).
4. **Answer questions from sources, not speculation.** Code (section 5), the running app, and Observe. What telemetry can't answer becomes a **telemetry gap** item.
5. **Fold in other feedback** when asked (teammates' PR reviews, Slack, Jira): dedupe against Byron's items and credit the source.
6. **Write the output** (section 6) and a coverage line: "all N sentences and M marks reviewed".

Fan out with subagents when the session is long: one maps items to source, one reads Observe for the session window, one gathers teammates' feedback. Give each the session path, the UTC window, the environment and the item list.

## 5. Modeler / Rel app joins

**Environment from host**

| Host | Where | Telemetry |
| --- | --- | --- |
| `relationalai.up.railway.app` | Railway project `modeler`, environment `staging` | Observe `environment = "staging"` |
| `<name>.up.railway.app` (`rel-app-*`, `modeler-*`) | Railway environment of that instance; `tasks/TASK-0059-assets/instance-inventory.md` in daily-planning maps hosts to environments | Observe `environment = "<env>"` |
| `localhost:<port>` | Byron's local server/worktree | `server/logs/redwood2_*.jsonl` (newest by mtime, see modeler `server-log-troubleshooting` skill) |
| ECS / AWS | `service_name` `relapp-server`, `relapp-browser`, `customer.id` | browser spans carry `rum.sessionId` |

**Deployed revision:** Observe logs/spans carry `resource_attributes."vcs.revision"`; Railway shows the release. Check out or diff that commit when mapping to code, not `main`.

**Map UI to code** in `/Users/byronwall/repos/modeler` (read its `AGENTS.md`/skills first): grep the `aria-label`, visible text and component names from `hovered`/`region.elements` (e.g. `canvas[aria-label="Concept map"]` → `client/apps/modeler/src/components/model-viz/concept-map-2d.tsx`). Request URLs name the API route and ids (`/api/.../task/<uuid>/body`, `/api/connection-snapshot`). Give `file:line` for each item you map, and mark root causes as verified or suspected.

**Observe** (`observe` CLI; OPAL help in the `observability` skill):

```bash
observe query -i 41766875 -s <startZ> -e <endZ> --csv -q 'filter environment = "staging" | statsby n:count(), group_by(service_name, span_name) | topk 20, max(n)'   # spans
observe query -i 43252774 -s <startZ> -e <endZ> --csv -q 'filter environment = "staging" and severity_text != "INFO"'                                          # logs
```

- Spans `41766875` (`service_name = "model-server"` on Railway), logs `43252774` (`body`, `severity_text`, `attributes."event.type"`, `trace_id`). Pad the window by a minute each side.
- Line up each item's UTC time with spans: slow loads (`sync.*`, `model.load`, `SF::query`, `WS::Subscribe`), task runs, queueing (`limiter::pyrel_execution::acquire`), event-loop stalls (`LoopStallEvent`), errors.
- Cite trace IDs bare (32-hex) so the plan viewer links them.
- Spans have no user identity: other users on the same environment show up too. Narrow by time, route and ids from the browser events.

## 6. Output shapes

Match Byron's ask; ask only if genuinely ambiguous.

- **Exhaustive feedback list** (usability run): numbered items grouped by category — broken, polish/general UI, unfinished feature, stop doing, start doing, found in telemetry, telemetry gaps, what worked (keep these working). Each item: bold one-line problem, one or two sentences of detail and cause, offsets, image links, source credit, existing PR/issue that already covers it.
- **Fix now + future ideas** (feedback on work in progress): implement the immediately actionable items in the target repo, and collect the forward-looking ones in one future-ideas doc. Cite marks as `R<day>-NNN` with offsets.
- **Intent documents:** hand the extracted points to `software-design-sleuth-full` with the session as a raw source.
- **One issue** (Jira via `jira` skill, Linear via modeler `create-linear-issues`): standalone body (no local paths or task IDs), the most useful images only, each **annotated** — a caption bar naming the item plus numbered boxes (Pillow; `tasks/TASK-0084-assets/staging-walkthrough-2026-11-02/annotated/annotate.py` in daily-planning is a working template). Embed images inline under the item they show, with the timestamp above. For motion bugs, show a before/after frame pair rather than a video attachment. Jira image upload: memory note "Jira image embedding". File only when Byron says so.

**Where it goes:** the owning task's `tasks/TASK-NNNN-assets/` in daily-planning (create the task first), with images copied as `mark-NNN.<ext>` into a dated subfolder. Never into the recorder folder or a repo checkout. Link the source folder, `session.md` and `viewer.html` by absolute path, and record the session path in the task.

## 7. Pitfalls

- `activity.jsonl`/`mark.context.browserURL` and page title can name another tab (seen twice: a local brief and a localhost tab while staging was on screen). Trust `browser.*` and the image.
- `browser.jsonl` mixes tabs and third-party noise (`xp.atlassian.com`, other localhost apps). Filter by `tabId` and host.
- Only failed/slow requests are logged, so no request ids: join to Observe by time and route.
- Transcript mis-hearings: confirm names against `reference/people/` and the repo before writing them.
- A joined session's media and per-mark notes live in its sources; don't move or rename them.
- Don't drop low-signal comments to make the list tidy: Byron asks for exhaustive.
- Copy images out; never edit the recorder's files.
