---
name: create-macos-finder-quick-action
description: Create, install, repair, or explain macOS Finder Quick Actions and Services backed by shell scripts or command-line tools. Use when Codex needs to put an existing alias, shell function, ffmpeg command, formatter, converter, uploader, or other script into Finder's right-click Quick Actions or Services menu as an Automator `.workflow` bundle.
---

# Create macOS Finder Quick Action

Package a self-contained shell script as a Finder service, install it in `~/Library/Services`, refresh macOS registration, and verify the installed workflow with disposable input.

## Build the workflow

1. Inspect the source alias, function, or script before changing anything. Preserve its actual behavior and tell the user when comments or assumptions disagree with the command.
2. Resolve the menu name, accepted file UTI, single-versus-multiple selection behavior, output location, overwrite policy, and user feedback. Prefer a precise name such as `Convert Video to MP4 (1080p)` over a vague name.
3. Make the workflow script self-contained. Do not source `.zshrc` or another interactive startup file. Automator has a minimal environment, so discover command locations with `command -v` and use absolute paths such as `/opt/homebrew/bin/ffmpeg`.
4. Ensure the script accepts Finder paths through `"$@"`. Quote every path and iterate over all inputs unless the user explicitly wants one file only.
5. Stage the shell body in a temporary file, then run `scripts/generate_workflow.py`. Supply one or more accepted UTIs with repeated `--send-file-type` arguments.

```bash
python3 scripts/generate_workflow.py \
  --name "Convert Video to MP4 (1080p)" \
  --script-file /private/tmp/convert-video.zsh \
  --send-file-type com.apple.quicktime-movie \
  --output "/private/tmp/Convert Video to MP4 (1080p).workflow"
```

Find an existing file's UTI with `mdls -name kMDItemContentType /path/to/file`. Common choices include `public.item`, `public.folder`, `public.movie`, `com.apple.quicktime-movie`, `public.image`, and `public.text`. Use the narrowest type that matches the request.

## Validate and install

1. Validate both generated plists before installation.

```bash
plutil -lint "$workflow/Contents/Info.plist" "$workflow/Contents/Resources/document.wflow"
```

2. Resolve the exact destination first. Refuse to replace an existing workflow unless the user authorized that exact replacement.
3. Install with `ditto` into `~/Library/Services/<Name>.workflow`. Request filesystem approval when the sandbox cannot write there.
4. Refresh registration and inspect the service entry.

```bash
/System/Library/CoreServices/pbs -flush
/System/Library/CoreServices/pbs -update
/System/Library/CoreServices/pbs -read_bundle "$installed_workflow"
```

Use `pbs -dump_cache` and search for the bundle path if registration remains uncertain. Restart Finder only if cache refresh and bundle inspection are insufficient.

## Verify end to end

Test the installed bundle, not merely the staged bundle. A newly generated `.workflow` outside a recognized Services location can fail with OSStatus `-10813` even when its plists are valid.

Create a disposable fixture under `/private/tmp`, run `/usr/bin/automator -i "$fixture" "$installed_workflow"`, and inspect the result. Never test by overwriting or converting a user's real file when a synthetic fixture can prove the same behavior. Hardware encoders and GUI-adjacent Automator execution may require running outside a restricted sandbox.

After success, tell the user to right-click a matching file and choose **Quick Actions** or **Services** followed by the configured name. State material behavior such as output naming, overwrites, resolution changes, and multi-file support.

## Shell-script guardrails

- Use Automator's `/bin/zsh` action with `inputMethod = 1`, which passes selected Finder paths as arguments.
- Pass notification text as arguments to `/usr/bin/osascript -` instead of interpolating filenames into AppleScript source.
- Prefer start, success, and failure notifications for long-running actions.
- Return nonzero when any selected item fails, but continue processing independent selections when appropriate.
- Avoid relying on aliases, shell options, relative working directories, `PATH`, terminal UI, or interactive prompts.
- Remember that `-y` in ffmpeg overwrites outputs, scaling filters may upscale or downscale, and comments about frame rate or resolution do not change command behavior.

## Resource

Use `scripts/generate_workflow.py` to generate the Automator bundle deterministically. Read or patch it only when the workflow needs capabilities beyond a Finder file-selection shell action.
