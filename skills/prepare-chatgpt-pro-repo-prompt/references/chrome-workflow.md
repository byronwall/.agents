# Use the signed-in Chrome session

Use this reference for Pro submission, follow-up, and collection on Byron's Mac.
Use Google Chrome's existing signed-in profile unless Byron requests another browser.
The profile observed on 2026-10-12 was **Byron (byroni.us)**. Verify the current profile; do not hard-code a profile directory.

The steps are the same for both agents. Only the tools differ:

- **Codex:** `cua_repl` with `@Chrome`, or native controls as a fallback. See [Codex tools](#codex-tools).
- **Claude Code:** the Claude in Chrome extension (`mcp__claude-in-chrome__*`). See [Claude Code tools](#claude-code-tools).

## Rules for both agents

- An agent's built-in browser (Codex in-app browser, Claude's browser pane) has its own signed-out session. That does not show that Chrome is signed out. Use Chrome.
- Do not ask Byron to log in again until the intended Chrome profile has been checked.
- Do not extract browser cookies or copy browser profile files to work around access.
- Read the URL and ChatGPT account state before you send anything.
- Inspect the live model selector. Verify **Pro** and record its effort setting when shown. Do not substitute another model.
- Read fresh UI state after each action. If an action appears unchanged, inspect the current view before you retry.
- Verify every attachment name and wait for uploads to finish before you send.
- Verify the submitted message, the conversation URL, and the processing state (Thinking text or a Stop control). A click is not proof of submission.
- ChatGPT can rename an uploaded file, for example `pro-prompt(20261028…).md`. Record the shown name.

## Claude Code tools

Load the tools in one `ToolSearch` call: `tabs_context_mcp`, `navigate`, `computer`, `find`, `file_upload`, `javascript_tool`, `get_page_text`, `read_page`, `list_connected_browsers`, `browser_batch`.

### Submit

1. `list_connected_browsers`. Confirm a local Chrome is connected and in use. If none, ask Byron to open Chrome with the extension.
2. `tabs_context_mcp` with `createIfEmpty: true`, then `navigate` the tab to `https://chatgpt.com/`.
3. Take a screenshot. A sidebar with chat history shows the account is signed in.
4. Click the model button in the composer (it shows `Pro` or `Thinking effort`). The menu shows the model and an effort slider. Press Escape to close it.
5. `find` "Attach files" input. It returns a hidden `input type=file` ref. Call `file_upload` with that ref and the absolute paths. Do not click the + button: a native file picker opens that the extension cannot drive. One call accepts up to 10 MB in total.
6. Click the message box, `type` the short execution instruction, and `zoom` on the composer to check the text and both attachment chips.
7. Click the send arrow. Wait about 8 seconds. Take a screenshot and read `location.href` with `javascript_tool` to get the `/c/<id>` URL.

Use `browser_batch` for each predictable run of steps (click, type, zoom).

### Check and collect

- The tab group from submission is usually gone by the next check. Call `navigate` with the URL and no `tabId`: it makes a new tab group. Close the tab with `tabs_close_mcp` when done.
- Wait about 4 seconds, then take a screenshot. A square Stop button in the composer or progress lines ("Edited a file", "Read files") mean it is still running. Don't rely on DOM selectors such as `data-testid` or `data-message-author-role`; on 2026-10-28 they matched nothing.
- When it is done, the answer ends with a table of files with **Download** links, an optional **Download ZIP**, and file cards. `find` "Download ZIP" returns a button ref; `left_click` on that ref saves the file to `~/Downloads` with no prompt. Wait for the file with a short bounded loop on `ls -t ~/Downloads`, then move it into `tmp/pro/<topic>/`.
- Check ZIP entries for absolute or `..` paths before you extract. Commit the extracted reports as intent assets; never commit the ZIP.
- When a file link fails, read the same content inline with `get_page_text`, or ask Pro in the same conversation to give that file inline. Do not resubmit the research.

### Schedule the later check

- `CronCreate` with an hourly off-minute cron (for example `41 * * * *`). The prompt names the conversation URL, checkout, branch, run record, and what to do in each state. Record the job ID in the run record.
- These jobs are session-only. They stop when the Claude session closes, and they fire only when the session is idle. Say so in the run record.
- Remote routines (`/schedule`) run in the cloud and cannot reach the local Chrome. Do not use them for collection.
- Delete the job with `CronDelete` when the run is done or blocked on Byron.

## Codex tools

- Use `cua_repl` for browser or native UI actions and read its returned documentation.
- At each resumed collection, check connected browsers once. Chrome may now be connected even if submission used native controls.
- When a Chrome tab is available through browser controls, bind that tab with Chrome explicitly selected.
- If Chrome is absent from the browser inventory, it may still be available as a native app.
- On macOS, use `let chrome = await cua.getApp("com.google.Chrome");` for that native fallback.
- Read the window title and Chrome profile button, and match the intended profile.
- If native access reports a locked Mac, check the Chrome browser connection before you request an unlock. The extension connection can stay usable while native controls are unavailable.
- For the native fallback upload, use ChatGPT's **Add files and more** → **Add photos & files** control. In the macOS file picker, **Go to Folder** accepts the absolute paths.
- Re-derive element IDs after menus, navigation, or picker changes. Do not reuse stale IDs or guess coordinates.
- Schedule the later check with a heartbeat automation, per the autonomous workflow.

## Resume and collect

Return to the recorded conversation in the same verified Chrome profile.
Inspect it before any resend. Preserve a running response and collect its observed artifact links when complete.
Follow the autonomous workflow for artifact checks, bounded follow-ups, integration, and PR completion.

For downloads, verify the actual local file before you retry. If a download fails, inspect the same conversation first.
A normal download click can recover the existing file without resubmitting research. Use bounded waits; do not leave an unresolved download wait running.
Record any failed independent download.
