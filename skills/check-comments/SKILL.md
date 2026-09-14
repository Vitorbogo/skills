---
name: check-comments
description: Judge every comment by the facts it carries. Remove the ones that carry none, shorten the ones padded around a few, keep the rest at any length. Use when asked to check, clean up, remove, or shorten comments, when a comment restates the code, when a comment is bloated or too long, when reviewing the comments a branch or PR introduced, or on `/check-comments [<number>]`.
---

# Check Comments

Judge a comment by the facts it carries, never by its length.

A **fact** is something the comment states that the code cannot state on its own.
`// increment the counter` above `count++` carries zero facts.
`env — one of qa, stg, prod` carries one.

The user picks which changes land.

## Invocation

| Command | Behavior |
|---|---|
| `/check-comments` | Check the 10 worst comments. |
| `/check-comments <number>` | Check that many. |

The number is a ceiling, not a quota. Report 3 when only 3 earn a verdict.
A codebase that comments well yields few. That is a good result, so report it as one.

## Scope

Where you search depends on where you are. Resolve this before searching.

| Situation | Search |
|---|---|
| The current branch has an open PR | The PR diff — `gh pr diff` |
| The branch has commits ahead of the default branch | The branch diff — `git diff $(git merge-base HEAD <default-branch>)...HEAD` |
| On the default branch, or no diff | The whole repository |

In branch or PR scope, a candidate is a comment the diff **added or modified**. A comment
that merely sits in a file the branch touched is out of scope.

The user's request overrides this table. A named path, a named file, or a phrase like
"the whole repo" sets the scope directly.

Branch scope usually yields far fewer than the limit. That is the expected result, not a
reason to widen. State the scope you searched in your report.

## Pick the Verdict

Count the facts. Compare that count to the line count.

| Facts | Verdict |
|---|---|
| None | **Remove** |
| Roughly one per line | **Keep** — at any length, 5 lines or 80 |
| Far fewer than lines | **Rewrite** to about one line per fact |

Length never decides. A 51-line header where every line lands a fact is a **Keep**.
A 10-line block padded around 3 facts is a **Rewrite**.

When the count is close, keep the comment as it stands.

Long comments are mostly Keeps. Searching by length surfaces dense headers far more
often than padded ones, so expect to reject most of what the search returns.

## The Rewrite Contract

A rewrite carries every fact across. Nothing else survives.

**Carry over:** every fact, in the comment's original language and voice.

**Cut:** restated parameter names, restated signatures, restated types, banner rules,
blank filler lines, hedging, and narration of the line below.

A shorter version that drops a fact is not a rewrite. It is a Remove. Remove needs the
fact to be worthless, so check it against Never Lose first.

Never invent a fact to fill the shorter version. If you cannot verify a claim from the
code, it does not go in.

## Never Lose

These facts survive every verdict. They rule out Remove, and a Rewrite must carry them:

- backports, compatibility, or version-specific behavior;
- infrastructure, deployment, or architecture;
- workarounds, gotchas, or non-obvious reasons;
- documentation, specifications, RFCs, or ADRs;
- bugs, issues, tickets, or contextual TODOs and FIXMEs;
- intent, trade-offs, or constraints.

When unsure, keep it.

## Workflow

1. Resolve the limit from the invocation (default 10).
2. Resolve the scope from the Scope table.
3. Search within that scope. Skip generated output, vendored dependencies, lockfiles,
   and docs.
4. Count the facts in each candidate and assign a verdict.
5. Rank by lines wasted, most to least.
6. Get each candidate's age with `git blame -L <line>,<line> --date=relative -- <file>`.
   Mark uncommitted lines `uncommitted`.
7. Draft the replacement text for every Rewrite before you present anything.
8. Present the table, then the rewrite blocks, then ask (see Feedback).
9. Apply only what the user approves.
10. Harvest knowledge-base-worthy facts (see Harvest to the Knowledge Base).
11. Run the project's lint and typecheck. Fix anything the changes broke.

Delegate the read-only search to a fast, low-reasoning subagent when one is available.
Ask it for at most the limit, each with exact path, line, full comment text, and one to
three adjacent code lines. Otherwise search directly.

## Required Output

Open with one line naming the scope you searched: the PR, the branch and its base, or the
whole repository.

Then the table, one row per candidate:

```markdown
| Comment | Age | Verdict | Why |
|---|---|---|---|
| `// increment the counter` | 8 months ago | **Remove** | Restates `count++`. No facts. |
| `/** Sync a review response... */` | 3 weeks ago | **Rewrite** | 10 lines, 3 facts. 7 restate the signature. |
| `// cache-layer module header` | 1 year ago | **Keep** | 51 lines, ~30 facts. Dense. |
```

Truncate a long comment in the cell with `...`. The full text goes in its rewrite block.

Then one block per Rewrite, showing both versions in full:

````markdown
**`src/sync/reviews.ts:142`** — 10 lines to 4

```diff
- * Sync a review response update to the database
- *
- * @param {string} reviewId - The review ID to update
- * @param {string} responseText - The owner's response text
- * @param {number|null} responseTimeHours - Hours between review and response
- * @param {string} env - Target environment (qa, stg, prod)
- * @param {string} jobId - Job ID for logging
+ * Write one review response to the database.
+ * `responseTimeHours` is the gap between the review and the response.
+ * `env` is one of qa, stg, prod.
```

Facts carried: response-time definition, env values, target is the database.
````

State the facts carried under every rewrite. That line is how the user checks your work.

## Feedback

After the table and the rewrite blocks, ask:

> **Apply all recommended?**
> - Yes, apply all
> - Removes only, skip the rewrites
> - No, I want to review each one

On the third answer, go one at a time. Name each comment by its exact text, not its
location. Take `Remove`, `Rewrite`, or `Keep` for each.

## Harvest to the Knowledge Base

A kept or rewritten fact lives in one file. Some of those facts are team knowledge.

This step runs **only when the environment defines a knowledge base** — a vault, a wiki, a
`docs/` tree, or a notes system named in `CLAUDE.md`, `AGENTS.md`, or the project's own
instructions. No knowledge base named, no harvest. Skip the step in silence.

Harvest a fact when **all** of these hold:

- it states a gotcha, a workaround, a decision with a reason, or a non-obvious domain rule;
- it stays true outside the file it sits in;
- the knowledge base has no note on it yet.

Do not harvest a fact that only explains the line beside it, that repeats the knowledge
base or the repo docs, or that the code and git already record.

The knowledge base owns its own protocol — routing, quality bar, deduplication,
frontmatter. Read that protocol before you write. This skill adds no rules of its own.

Search first. Then update the existing note, or create one and link it where that protocol
says new notes get linked.

Write without asking. The knowledge base quality bar is the filter, not the user. The fact
stays in the code too. The note is a copy, not a move.

Report each note in one line: the note path and the comment it came from.

## Red Flags - Stop

- You are short of the number and looking for more candidates.
- You are widening past the branch or PR diff because it did not yield enough candidates.
- You are counting a fact twice to justify keeping a comment.
- You cannot name the facts a rewrite carries without rereading your draft.
- A rewrite reads better than the original but you cannot map every fact across.
- You are rewriting a comment whose facts you had to guess from the code.

Each one means: revert to Keep and move on.

| Excuse | Reality |
|---|---|
| "Only found 4, the user asked for 10" | 4 is the answer. Padding it with weak verdicts costs the user real facts. |
| "The branch only touched 2 comments, so I looked wider" | 2 is the answer. The user asked about this branch's work, not the repo's backlog. |
| "This file is in the branch diff, so its old comments count" | Only comments the diff added or modified are in scope. |
| "This one is close enough to padded" | Close means Keep. The rule is there for the close calls. |
| "The rewrite says the same thing, better" | Prove it. Name every fact in both. If you cannot, it does not say the same thing. |
| "The comment is verbose, even if each line is a fact" | Verbose and dense are different. Facts decide, not style. |
| "I can infer the missing fact from the code" | Then the code says it and the comment need not. Do not write an inferred claim as a stated one. |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Searching the whole repo while on a feature branch | Resolve the scope first. The branch diff is the default there. |
| Shortening a comment because it is long | Count the facts first. Dense stays, at any length. |
| A rewrite that drops a fact | That is a Remove in disguise. Carry every fact or keep the comment. |
| Rewriting into your own voice | Match the file's language and tone. |
| Applying a rewrite the user never saw | Show both versions in full before you touch the file. |
| Adding a claim the code does not support | Only carry facts you verified. Never fill space. |
