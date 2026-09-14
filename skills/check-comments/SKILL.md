---
name: check-comments
description: Judge every comment by the facts it carries. Remove the ones that carry none, shorten the ones padded around a few, keep the rest at any length. Use when asked to check, clean up, remove, or shorten comments, when a comment restates the code, when a comment is bloated or too long, when reviewing the comments a branch or PR introduced, or on `/check-comments [<number>]`.
---

# Check Comments

Judge a comment by the facts it carries, never by its length. A **fact** is something the
comment states that the code cannot. `// increment the counter` above `count++` carries
zero. `env — one of qa, stg, prod` carries one.
`/check-comments` checks the 10 worst, `/check-comments <number>` that many. The number is
a ceiling, not a quota — report 3 when only 3 earn a verdict. A codebase that comments well
yields few. That is a good result, so report it as one.

## Scope

Resolve this before searching.

| Situation | Search |
|---|---|
| The current branch has an open PR | The PR diff — `gh pr diff` |
| The branch is ahead of the default branch | `git diff $(git merge-base HEAD <default>)...HEAD` |
| On the default branch, or no diff | The whole repository |

In diff scope a candidate is a comment the diff **added or modified**, not every comment in
a file the branch touched. Diff scope usually yields far fewer than the limit; that is the
expected result, not a reason to widen. A path or a phrase like "the whole repo" overrides
the table.

## Verdict

Count the facts. Compare to the line count.

| Facts | Verdict |
|---|---|
| None | **Remove** |
| Roughly one per line | **Keep** — at any length, 5 lines or 80 |
| Far fewer than lines | **Rewrite** to about one line per fact |

Length never decides: a 51-line header landing a fact per line is a Keep, a 10-line block
padded around 3 facts is a Rewrite. When the count is close, Keep — searching by length
surfaces dense headers more often than padded ones, so expect to reject most hits.

**Never Remove, and always carry across a Rewrite:** backports and version-specific
behavior; infrastructure, deployment, architecture; workarounds, gotchas, non-obvious
reasons; docs, specs, RFCs, ADRs; bugs, tickets, contextual TODOs and FIXMEs; intent,
trade-offs, constraints. When unsure, Keep.

**A rewrite carries every fact across and nothing else**, in the comment's original
language and voice. Cut restated parameter names, signatures and types, banner rules,
filler lines, hedging, and narration of the line below. Dropping a fact makes it a Remove
in disguise, so check the list above first. A claim you cannot verify never goes in.

## Workflow

1. Resolve the limit, then the scope.
2. Search it, skipping generated output, vendored dependencies, lockfiles, and docs.
3. Count facts, assign verdicts, rank by lines wasted.
4. Date each with `git blame -L <line>,<line> --date=relative -- <file>`; mark uncommitted
   lines `uncommitted`.
5. Draft every rewrite, then present, ask, and apply only what the user approves.
6. Harvest, then run the project's lint and typecheck. Fix what the changes broke.

Where a fast, low-reasoning subagent is available, delegate the read-only search: at most
the limit, each with exact path, line, full comment text, and adjacent code lines.

## Report

Name the scope you searched, then one row per candidate. Truncate a long comment with
`...`; its full text goes in the rewrite block.

| Comment | Age | Verdict | Why |
|---|---|---|---|
| `/** Sync a review response... */` | 3 weeks ago | **Rewrite** | 10 lines, 3 facts. 7 restate the signature. |
| `// cache-layer module header` | 1 year ago | **Keep** | 51 lines, ~30 facts. Dense. |

Then one block per Rewrite: `path:line`, lines before and after, a diff showing both
versions in full, and a `Facts carried:` line naming each fact — that last line is how the
user checks your work.

Then ask with the interactive selector your harness provides (Claude Code:
`AskUserQuestion`), never as prose the user has to answer by typing. Three options:
**Apply all**; **Removes only**, skipping the rewrites; **Review each one**, which goes one
at a time, naming each comment by its exact text rather than its location and taking
Remove, Rewrite, or Keep for each.

## Harvest

Runs only where the environment names a knowledge base — a vault, wiki, `docs/` tree, or
notes system in `CLAUDE.md`, `AGENTS.md`, or the project's instructions. Otherwise skip in
silence. That base owns its protocol — routing, quality bar, dedup, frontmatter — so read
it before writing. This skill adds no rules.

Copy a kept or rewritten fact there when it states a gotcha, a workaround, a decision with
a reason, or a non-obvious domain rule; stays true outside its file; and has no note yet.
Skip what only explains the line beside it, or what the base, the repo docs, the code, or
git already record. Search first, then update the existing note or create one. Write
without asking: the base's quality bar is the filter, not the user. The fact stays in the
code too, so the note is a copy. Report each note in one line: its path and its source
comment.

## Red Flags — Stop

Short of the number and hunting for more. Widening past the diff. Counting a fact twice.
Unable to name the facts a rewrite carries without rereading your draft. Rewriting facts
you guessed from the code. **Each one means: revert to Keep and move on.**

| Excuse | Reality |
|---|---|
| "Only found 4, the user asked for 10" | 4 is the answer. Padding it with weak verdicts costs the user real facts. |
| "The branch only touched 2 comments, so I looked wider" | 2 is the answer. The user asked about this branch's work, not the repo's backlog. |
| "This file is in the diff, so its old comments count" | Only comments the diff added or modified are in scope. |
| "This one is close enough to padded" | Close means Keep. The rule is there for the close calls. |
| "The rewrite says the same thing, better" | Prove it. Name every fact in both. If you cannot, it does not. |
| "It's long, so I'll shorten it" | Count the facts first. Dense stays, at any length. |
