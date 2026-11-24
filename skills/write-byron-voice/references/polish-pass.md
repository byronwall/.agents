# Polish pass

Run this pass last, on a finished draft or on text Byron hands over for cleanup. It removes the patterns that make prose read as machine-written. It does not rewrite.

The rules come from a blind eval in 2026-11 (planning TASK-0037). Four anti-slop skills edited 21 of Byron's posts and drafts. The winner, `no-ai-slop` by Peter Yang (MIT), changed about 4% of the words and cut surface tells by about 40%. A judge preferred it to every other skill and to this voice skill alone. Skills that rewrote more (`stop-slop`, `plain-writing`) cut more tells but lost on voice and added claims. Credit: rule wording below adapts `no-ai-slop` (github.com/petergyang/no-ai-slop, MIT, copyright 2026 Peter Yang).

## The edit budget

- Make the minimum effective edit. Leave a strong sentence alone, even if you would phrase it differently.
- Add nothing: no claims, examples, numbers, hedges or framing lines. Do not pull more material in from the transcript during this pass.
- Do not make the text longer. A polish pass that grows the text has rewritten it.
- Keep Byron's rough edges when they carry meaning: blunt words ("crappy"), real uncertainty ("I think", "maybe"), an open ending, an uneven section. A tidy verdict line is not a rough edge (see "Moral closers").
- Byron edits harder than a cautious reviewer. In his own review he changed about half the sentences in a post that had these patterns. When a sentence matches a pattern below, change it.
- Cut whole clauses, not single words. Find the sentence that does no work and delete it.

## What to cut

Ordered by how often each one fired on Byron's text.

1. **Announcements.** A sentence that says a point is coming instead of making it. Delete it and let the next sentence stand.
   - Before: "The useful moment came near the end. Codex had submitted the sitemaps…"
   - After: "Near the end, Codex submitted the sitemaps…"
   - Other examples: "This matters for what comes next.", "Here it gets interesting.", "The simplest claim is this.", "One problem is obvious, though.", "Two things matter here:", "The interesting part is…".
2. **Colon reveals.** A noun phrase, a colon, then the point. Write a plain sentence.
   - Before: "The profile was clear: about 97% of `layout()` was edge routing."
   - After: "The profile showed that about 97% of `layout()` was edge routing."
   - Keep colons for lists, labels and code.
3. **Moral closers.** A short, quotable sentence at the end of a paragraph or post that restates the fact before it as a lesson. Delete it. Do not rewrite it into a better line.
   - Before: "…gave a new identity access to my data. The agent did all the preparation. I did the one step that cannot be undone."
   - After: "…gave a new identity access to my data."
   - A short verdict that restates the paragraph is a moral closer too, even when it sounds like Byron: "That is worth a whole round.", "…and that is a fine result.", "That is the limit of this kind of loop." Byron cut each of these in his own review (wall-portfolio PR #11). Keep a verdict only when it adds a fact or a decision.
4. **Count setups.** "For two reasons. First… Second…" or "Three things did the work:". Merge into one sentence, or a list when there are really four or more items.
5. **Labels for importance.** "useful", "key", "matters", "interesting", "the real X" used to tell the reader what to think. State the fact, or cut the label.
   - Before: "This gave the implementation a useful division of work."
   - After: "That result split the implementation into clear jobs."
6. **"Not X, it's Y" contrasts.** State Y. Keep a contrast only when the reader would really assume X.
7. **Empty adverbs.** "just", "simply", "really", "actually", "honestly" when they add nothing. Keep them when they carry Byron's spoken rhythm or a real contrast.
8. **Clever headings.** Make a heading say what the section holds. Byron replaced "Six runs, six answers" with "Results on six example diagrams" and "The measuring stick came first" with "Benchmark and digest".
   - Before: "A Table Is Never Just a Table". After: "The Choices Inside a Table".
9. **Formatting slop.** Bold in the middle of a sentence for emphasis, bullets for two items, headers over two-sentence sections, emoji. Em dashes: none in short text, one or two at most in a long post.
10. **Puffery words.** delve, leverage, robust, seamless, pivotal, tapestry, unlock, supercharge, transformative, testament, game changer.
11. **Invented feelings.** A line about Byron's feelings, expectations or surprise that he never stated: "it held up better than I expected", "I was pleasantly surprised", "I'm glad", "I love this". Cut it and state the result. This bites hardest in agent-written PR reviews and comments, where it reads as too much personality. Keep one only when Byron said it himself.
   - Before: "I tried to break this on purpose, and it held up better than I expected."
   - After: "I tried to break this on purpose. It held across PyRel 2.0 to 2.3."

## What not to do

These rules lost in the eval or conflict with Byron's house style:

- Do not remove every adverb or every passive verb. Passive is fine when the actor is unknown or does not matter.
- Do not force every sentence to have a human subject.
- Do not rebalance sentence lengths for rhythm. Fix only a run of short, punchy fragments.
- Do not replace Byron's word with a plainer synonym when his word is already clear.

## Check

Before you return the text, compare it with the input:

1. Is every fact, number, name, link and qualifier still there?
2. Did the text get longer? If so, find what you added and remove it.
3. Does any paragraph now end on a tidy one-liner that the input did not have?
