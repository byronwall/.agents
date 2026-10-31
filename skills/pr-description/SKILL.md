---
name: pr-description
description: "Write or fix a pull request description the way Byron reviews them: a plain statement of what changed and what the user sees, proof that it works, and a template for each PR type (feature, fix, dev, docs) plus stack layers. Use before every `gh pr create` and `gh pr edit` that changes a body, after `gh stack submit` writes placeholder bodies, before `gh pr ready`, and whenever Byron asks to write, update, or improve a PR description. Applies to all PRs in all repositories."
---

# PR descriptions

Byron reviews PRs on GitHub, often without opening the app. A PR body must let him decide to merge from the page alone. He wants two things:

1. A simple statement of what changed and what the user sees differently.
2. Proof that it works, or is better or faster.

## Steps

1. Choose one type from the table. If a PR does two things, use the type of the larger part. If the parts are separable, split the PR.
2. Collect the proof before you write the body. Capture it on this branch.
3. Write the body from the template, into `tmp/pr-<slug>.md`. Remove the template notes and any optional section with no content.
4. If the PR is in a stack, add the stack block.
5. Create or edit the PR with `--body-file` and `--attach`. The global GitHub rules give the upload steps.
6. Read the saved body with `gh pr view <n> --json body --jq .body`. Confirm that each image has a GitHub URL and that nothing from a template is left.

Keep repository rules on top of this skill. If a repository requires a line, such as `Survey moves:` in srcly or a changeset note, keep that line.

| Type | Use for |
| --- | --- |
| Feature | New behavior that a user can see or use. |
| Fix | Something was wrong and now is right. Includes user-visible performance fixes. |
| Dev | Refactors, tooling, CI, dependencies, tests, cleanup, and internal speed work. |
| Docs | Plans, intent and shaping docs, research, and reference docs. |

## Rules for all types

- Start with one to three plain sentences. Say what a user can do now, or what is different. Do not start with a file name, a function name, or the word "This PR".
- Write for a person who has not read the diff. Explain internals only when the reviewer needs them to judge the change.
- Do not list files or walk through the diff. GitHub shows the diff.
- Use the words the user sees in the product, such as button labels and page names.
- Keep it short. If a section does not help the merge decision, remove it.
- Tell the bad news. State limits, skipped checks, and known defects in `Limits`.
- Follow the prose rules in the global instructions.

## Proof

Each PR has a `## Proof` section. An empty one is never correct. Put the evidence in the page: a link to a local file, or a statement such as "works on my machine", is not proof.

Use the strongest proof that fits. Show more than one kind when it helps.

| The change is | Show |
| --- | --- |
| Visible UI | Screenshots of each changed state. Screenshots are the default. Add more, not fewer. |
| Fixed visual bug | Before and after screenshots at the same size and of the same state, labeled. |
| Faster or smaller | A table with before, after, and change, plus the command, the input, the machine, and the run count. |
| Performance detail | A trace, a flame chart, or a timing breakdown. Name the part that changed. |
| CLI or tool | The real command and its output in a fenced block. Trim the output to the lines that matter. |
| API or data | A real request and response, or a query result, from before and after if the value changed. |
| Bug with no visual | The reproduction and its result before and after, and the name of the test that now protects it. |
| Refactor, config, CI | Command output, such as tests, types, or the build. Add one line that says why no stronger proof exists. |

Rules for proof:

- Capture the proof from a real run on this branch. Never invent or estimate a number. Never reuse a number from an earlier commit.
- Do not write "faster" or "smaller" without a measured number.
- Give each image or block one line that says what it proves.
- Show the result that counts, also when it is not good. Report a regression next to the gain.
- "Tests pass" alone is weak proof. Use it only for the Refactor, config, CI row, with the reason line.
- If you did not view your own screenshots, start the body with this line: `> **Visuals unverified:** I couldn't view these screenshots. Please check them.`
- If you cannot capture proof that the change needs, say what is missing and why at the top of `## Proof`. Do not leave this out.

## Templates

Replace each `<...>` note. Keep the section names, so that all of Byron's PRs read the same.

### Feature

```markdown
<One to three sentences: what a user can do now.>

## What you'll see

- <Behavior, in product words.>
- <Where to find it.>

## Proof

![<state>](tmp/<shot>.png)
<What this shows.>

## Limits

- <Optional. What this does not do yet.>
```

### Fix

```markdown
<One to three sentences: what was wrong for the user, and what happens now.>

**Before:** <What the user saw.>
**After:** <What the user sees now.>

## Cause

<One or two sentences.>

## Proof

| Before | After |
| --- | --- |
| ![before](tmp/<before>.png) | ![after](tmp/<after>.png) |

<What this shows. Name the regression test if there is one.>

## Limits

- <Optional. Related cases that this does not fix.>
```

### Dev

```markdown
<One to three sentences: what changed for the people who work on this code.>

**User impact:** <None, or the small visible change.>

## Why

<The problem this removes, or what it makes possible.>

## Proof

<Benchmark table, or the command and output. Add the reason line if no stronger proof exists.>

## Limits

- <Optional. Risks, follow-up, or migration steps.>
```

### Docs

Docs PRs do not need screenshots. The proof is where the content came from.

```markdown
<One to three sentences: what this doc proposes, decides, or records.>

## What to do with it

<The decision or action needed from Byron, or "Reference only".>

## Proof

<How this is grounded: the code, runs, or sources that it uses, and what is verified or speculative.>
```

## Stacks

A slice is one layer of a stack. Each layer uses its own type template and gets a stack block. Put the block at the end of the body, before the attribution line.

The bottom PR holds the full story. Update the bottom PR when the layers change.

```markdown
## Stack: <name>

**What splits:** <The whole change, and the parts it divides into.>
**Why it splits:** <What a reviewer gains. For example, each part can merge alone, or the risky part is separate.>
**Why this split:** <Why these seams are the best choice. Name at least one other split that you rejected, and why.>

1. <PR link>: <What this layer adds.>
2. <PR link>: <What this layer adds.>
```

Each layer above the bottom gets a short block:

```markdown
## Stack: <name>, layer <n> of <total>

**This slice:** <What this layer adds.>
**Why it is its own layer:** <The reason that it cannot join the layer below or above.>
**Full story:** <link to the bottom PR>
```

`gh stack submit --auto` writes placeholder titles and bodies. Replace them with `gh pr edit` directly after the submit, while the PRs are new. A layer that depends on a later layer for its proof says so, and links to the layer that shows it.

A layer needs its own proof. Do not point all layers at one screenshot in the top PR.

## Reference

Byron's requests that this skill comes from:

- "Add screenshots so I can review without opening the app."
- "Ensure each PR has an image for verification."
- "Get screenshots and CLI output into the PRs."
- "Measure tsc memory before/after, and open a PR if it holds up."
- "Create a PR as soon as possible so I can track progress in GitHub."
