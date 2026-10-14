# Use the signed-in Chrome session

Use this reference for Pro submission, follow-up, and collection on Byron's Mac.
Prefer Google Chrome's existing signed-in profile unless Byron requests another browser.
The profile observed on 2026-10-12 was **Byron (byroni.us)**. Verify the current profile; do not hard-code a profile directory.

## Select the browser and session

- Use `cua_repl` for browser or native UI actions and read its returned documentation.
- At each resumed collection, check connected browsers once. Chrome may now be connected even if submission used native controls.
- When a Chrome tab is available through browser controls, bind that tab with Chrome explicitly selected.
- If Chrome is absent from the browser inventory, it may still be available as a native app.
- On macOS, use `let chrome = await cua.getApp("com.google.Chrome");` for that native fallback.
- Read the window title, Chrome profile button, URL, and ChatGPT account state. Match the intended profile before sending anything.
- Select the existing ChatGPT tab when it is the requested handoff surface. Otherwise open a new tab in that profile.
- Inspect the live model selector. Verify **Pro** and record its power or effort when shown.

Codex's in-app browser can have a separate signed-out session. That does not establish that Chrome is signed out.
Do not ask Byron to log in again until the intended Chrome profile has been checked.
If native access reports a locked Mac, check the Chrome browser connection before requesting an unlock.
The extension connection can remain usable while native controls are unavailable.
Request an unlock only when neither route can reach the intended session. Report a native-access limit, not an account-login failure.
Do not extract browser cookies or copy browser profile files to work around access.

## Upload and submit

Use connected tools or documented browser controls within the verified session when available.
For the native fallback, use ChatGPT's **Add files and more** → **Add photos & files** control.
Use the macOS file picker to select the actual prompt and source packet. **Go to Folder** accepts their absolute paths.
Read fresh UI state after each action. Re-derive element IDs after menus, navigation, or picker changes.
If an action appears unchanged, inspect the current view before retrying; do not reuse stale IDs or guess coordinates.

Verify every attachment name and wait for uploads to finish before sending the execution instruction.
Verify the submitted message, conversation URL, and processing state. An attempted click is not proof of submission.
Record those observations in the run record and arrange the later check through the autonomous workflow.

## Resume and collect

Return to the recorded conversation in the same verified Chrome profile.
Inspect it before any resend. Preserve a running response and collect its observed artifact links when complete.
Follow the autonomous workflow for artifact checks, bounded follow-ups, integration, and PR completion.

For downloads, verify the actual local file before retrying. If an intercepted download fails, inspect the same conversation first.
A normal download click can recover the existing file without resubmitting research. Use bounded waits; do not leave an unresolved download wait running.
Record any failed independent download. Companions extracted from a verified archive remain original artifacts; compare their manifest hashes.
