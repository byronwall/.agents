# Adversarial patterns

Pick the two or three that fit the target. Describe each to Pro as a pattern and a ground truth it can check; do not tell Pro the expected UI result. Pro builds the controls in fixture copies.

## Wrong answers (correctness)

| Pattern | Control to ask for | Oracle |
|---|---|---|
| **Same output, different cause** | Two variants show the same visible result; the cause differs (field A versus field B, cache versus fresh fetch) | Source assignment; a runtime script |
| **Same name, different root** | The same relative path or symbol in two roots or workspaces with different contents | File hashes; the API response's root |
| **Completeness claim with a hole** | A dependency with no body: a declaration, a stub, a generated file, a third-party call, a dynamic import | The product must say "unknown", not "none" |
| **Alias or mutation** | A copy versus an alias of the same input; a function that mutates its argument | Run the code and compare object identity |
| **Revision identity** | Open a deleted, moved, or reverted line; a commit that touches only data files | `git show <rev>:<path>`, `git diff --numstat` |
| **Touched versus net** | A change made and reverted inside the range | `git log --name-only` versus `git diff --name-only` |
| **Dirty worktree** | An uncommitted value that conflicts with the committed text | `git status`, `git diff` |
| **Missing versus zero** | An item with no metric beside one with a real zero | The data source |
| **Coverage drift between views** | A tracked file that matches an ignore rule; a file type one view skips | `git ls-files` against each view's set |
| **Mixed configurations** | Two settings for the same thing that must combine (a monthly and a yearly budget on one category; two rules on one path), created in both orders | Recompute by hand; order must not matter |
| **Instance confusion** | One component used twice with different inputs | Which caller each witness names |

## Wrong state (navigation and identity)

| Pattern | Control to ask for |
|---|---|
| **Race** | Slow the first request (label it a controlled stress test) and finish the second first; the final view must match the last selection |
| **Back / Forward / refresh / shared link** | Record separately what survives for each piece of state: scope, path, filter, overlay, selection, line |
| **Stale selection** | Delete or rename the selected item, switch roots, change the ref |
| **Mode handoff** | Start the same task from a different view than the happy path; no manual mode switch or retry |

## Honest limits (what good failure looks like)

| Pattern | Control to ask for |
|---|---|
| **Opaque handoff** | An upstream step the product cannot model. Good result: names the last proven step, opens its source, does not claim the producer |
| **Scale** | The same question on a larger real checkout. Good result: an explicit timeout or partial result, not a blank panel or a crash |
| **Unsupported construct** | A pattern the docs say is not supported. Good result: a stated limit, not silence |

## Phrases that worked

- "Try to make the build give a convincing wrong answer."
- "A plausible wrong answer matters more than a noisy layout."
- "A precise, clickable 'I can't prove past here' can be acceptable."
- "A missing metric is not a zero metric."
- "Don't award a pass just because the feature exists or CI is green."
- "If you artificially delay a request, label it a controlled stress test."
- "If you find a consequential failure whose history is ambiguous, replay that one case on the before-build. Otherwise label it newly observed, not introduced."
