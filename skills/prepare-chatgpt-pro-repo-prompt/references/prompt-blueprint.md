# Pro Prompt Blueprint

Assemble the prompt from these sections. Use the ones the task needs, in this order. Write short, direct sentences; every line should change what Pro does.

## 1. Repository and mission

- Canonical repository URL on its own line, and the ref or commit.
- The mode (Design, Methods, Strategy, Review, Evaluation loop).
- One primary mission as a decision question. Good: "What should explorEDA's selection-bound narrative findings look like, and how should we build them?" Weak: "Research narrative findings."
- Why it matters now and what will be built or decided from the answer.

## 2. Role

Name a concrete expert role (for example "senior data-visualization tool designer who has shipped linked-view systems", or "applied statistician focused on numerically stable regression"). Ask for candid judgment: strengths, weaknesses, tradeoffs, rejected options, uncertainty.

## 3. Access check

Before the work, Pro confirms it can read the repository at the named ref, or the supplied source packet. If decisive source is missing from both, it stops and names the smallest missing input. It does not claim a full review from partial access. One short paragraph is enough.

## 4. Reading route

A short ranked list of real files: rules (`AGENTS.md`), product and architecture docs, public entry points, the core implementation for the topic, representative examples, tests, and prior research or plans on the topic. Say "at minimum" when broader discovery helps.

## 5. Ranked questions

Three to six questions, most important first. For each, say what a useful answer must decide.

By mode:

- **Design:** What do the best tools, libraries, and papers do (name them and cite primary sources)? What are the real design options for this product? Which one and why? What does the user see and do? What changes in the data model, API, and state? What is the milestone plan? What would make the design fail?
- **Methods:** What is the correct method and its assumptions? Where does the current code differ? What are the numerical and edge-case failure modes? What test cases with exact expected values prove it? What is the implementation plan?
- **Strategy:** Who is this for and what job does it do better than named alternatives? What are the three to five highest-leverage capability bets, ranked, with reasoning? What should be stopped or not built?
- **Review:** What is wrong, ranked by user impact, with evidence and a fix for each?

## 6. Evidence rules

- Cite repository paths and symbols for claims about the code.
- Cite current primary sources (docs, papers, source code) for decisive external claims, with URLs.
- Label facts, inferences, and proposals when it isn't obvious.
- Say when evidence is missing or conflicting.

Don't ask Pro to prove demand, run a usability study, or produce integrity receipts. Those don't improve the design.

## 7. Scope and non-goals

List what is out of scope for this mission, and any hard constraints (stack, package manager, public API stability, licensing). Keep it short and specific; don't list generic cautions.

## 8. Deliverable

Design and Methods missions end in a plan someone can build. Ask for:

1. **Report** (Markdown): the answer to each ranked question, with sources.
2. **Decision** at the top: what to build, in one paragraph.
3. **Implementation plan** (Markdown): milestones in order, each one shippable on its own, naming the files or modules it changes, the tests that prove it (with exact expected values where they apply), the docs page and runnable example it needs, and its main risk.
4. **Recommendations** with stable IDs, each classified **Build**, **Explore** (needs a prototype first), **Defer**, or **Avoid**, with a one-line reason.

Strategy missions end in ranked bets, each with a suggested Design-mode follow-up question. Review missions end in a ranked fix list.

Ask Pro to attach the files as downloads and link each one in its final message. If it can't create files, it gives the full content inline. One ZIP is fine but optional; don't ask for manifests or hash files.

Tell Pro that Codex or Claude will review the result against the code and do all repository changes.

## 9. Evaluation-loop additions

Only for iterative optimization: an immutable baseline, objective metrics and invariants, `better` / `not-better` / `invalid` results, cheap rejection checks before full checks, a bounded trial count, and a ledger of trials. Static checks can reject a candidate but not accept one when a full evaluation is required.

## 10. Final status

Pro ends with: access status, files read, what it checked versus what it proposes, deliverable links, and open questions.
