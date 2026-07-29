# Personal Skills Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn this directory into a public, installable Claude Code plugin marketplace (`Vitorbogo/skills`) that packages Vitor's 16 currently-installed skills as individually installable plugins, then retire the old manual `~/.agents/skills` + symlink setup.

**Architecture:** A root `.claude-plugin/marketplace.json` lists one plugin entry per skill. Each skill lives at `skills/<name>/` with its original files plus a new `.claude-plugin/plugin.json`. Content is generated from the existing `~/.agents/skills/<name>` folders by a small Python script, checked by a validation script, then pushed to GitHub and installed locally to confirm parity before the old setup is deleted.

**Tech Stack:** Plain Python 3 (stdlib only — `json`, `shutil`, `os`) for generation/validation scripts, git, GitHub CLI (`gh`), Claude Code's `/plugin` and `/reload-skills` commands.

## Global Constraints

- Repo: `Vitorbogo/skills`, public, built at `/Users/vitorbogo/Documents/dev/skills`.
- Marketplace name: `vitorbogo-skills`.
- One plugin per skill — no thematic bundling (confirmed design decision).
- No upstream tracking with `mattpocock/skills` — this is a one-time content copy.
- Root `LICENSE` stays MIT and must retain Matt Pocock's copyright notice.
- Do not delete `~/.agents/skills` or the `~/.claude/skills/*` symlinks until Task 4 (local install verification) has passed.
- Source of truth for skill content during migration: `~/.agents/skills/<name>` (copy full folder contents, not just `SKILL.md`).

---

### Task 1: Root repo files (README, LICENSE, .gitignore)

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `.gitignore`

**Interfaces:**
- Produces: repo-level identity/legal files. No code interfaces — later tasks don't depend on any symbol from this task, only on the files existing.

- [ ] **Step 1: Write `LICENSE`**

```text
MIT License

Copyright (c) 2026 Matt Pocock
Copyright (c) 2026 Vitor Bogo

The skills in this repository originate from https://github.com/mattpocock/skills
(MIT licensed) and are maintained here as a personal derivative by Vitor Bogo.
This notice must be retained per the original license's terms.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Write `.gitignore`**

```text
.DS_Store
```

- [ ] **Step 3: Write `README.md`**

```markdown
# skills

Vitor Bogo's personal Claude Code skills, packaged as an installable plugin
marketplace. Each skill is its own plugin, so you can install exactly the
ones you want.

The initial skill set originates from
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT licensed) and
is maintained here as an independent copy — edits happen directly in this
repo and are not synced back upstream.

## Install

Add the marketplace once per machine:

```
/plugin marketplace add Vitorbogo/skills
```

Then install whichever skills you want, one at a time:

```
/plugin install diagnose@vitorbogo-skills
/plugin install tdd@vitorbogo-skills
```

Run `/reload-skills` after installing to pick them up in the current
session.

## Update a skill

Edit the skill's files in this repo, commit, push, then on any machine that
has it installed:

```
/plugin marketplace update vitorbogo-skills
```

## Add a new skill

1. Create `skills/<name>/` with a `SKILL.md` (and any supporting files).
2. Add `skills/<name>/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "<name>",
     "version": "1.0.0",
     "description": "<same description as the SKILL.md frontmatter>",
     "author": { "name": "Vitor Bogo" },
     "license": "MIT"
   }
   ```
3. Add one entry to `.claude-plugin/marketplace.json`'s `plugins` array:
   ```json
   { "name": "<name>", "source": "./skills/<name>", "description": "<same description>" }
   ```
4. Run `python3 scripts/validate_marketplace.py` to confirm it's wired up correctly.
5. Commit and push.
```

- [ ] **Step 4: Verify the files were written correctly**

Run: `grep -l "Matt Pocock" LICENSE && grep -l "mattpocock/skills" README.md && cat .gitignore`
Expected: both `grep` calls print the filename (match found), and `.gitignore` prints `.DS_Store`.

- [ ] **Step 5: Commit**

```bash
git add README.md LICENSE .gitignore
git commit -m "Add repo README, LICENSE, and gitignore"
```

---

### Task 2: Generate per-skill plugin manifests and marketplace.json

**Files:**
- Create: `scripts/validate_marketplace.py`
- Create: `scripts/generate_manifests.py`
- Create: `skills/<name>/` for all 16 skills (copied from `~/.agents/skills/<name>`, plus a new `skills/<name>/.claude-plugin/plugin.json` each)
- Create: `.claude-plugin/marketplace.json`

**Interfaces:**
- Produces: `.claude-plugin/marketplace.json` with a top-level `plugins` array of 16 `{name, source, description}` objects; `skills/<name>/.claude-plugin/plugin.json` per skill with `{name, version, description, author, license}`. Task 3 and Task 4 rely on these exact file locations and the marketplace name `vitorbogo-skills` (set inside `generate_manifests.py`, not passed in from elsewhere).

- [ ] **Step 1: Write the validation script**

```python
#!/usr/bin/env python3
"""Validate that .claude-plugin/marketplace.json and per-skill plugin.json
files are consistent. Exits 0 and prints PASS, or exits 1 and prints FAIL
plus every problem found."""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    errors = []
    marketplace_path = os.path.join(REPO_ROOT, ".claude-plugin", "marketplace.json")

    if not os.path.isfile(marketplace_path):
        print(f"FAIL: {marketplace_path} does not exist")
        sys.exit(1)

    with open(marketplace_path) as f:
        marketplace = json.load(f)

    plugins = marketplace.get("plugins", [])
    if not plugins:
        errors.append("marketplace.json has no plugins listed")

    seen_names = set()
    for entry in plugins:
        name = entry.get("name")
        source = entry.get("source")
        if not name or not source:
            errors.append(f"plugin entry missing name/source: {entry}")
            continue
        if name in seen_names:
            errors.append(f"duplicate plugin name in marketplace.json: {name}")
        seen_names.add(name)

        rel = source[2:] if source.startswith("./") else source
        skill_dir = os.path.join(REPO_ROOT, rel)
        skill_md = os.path.join(skill_dir, "SKILL.md")
        plugin_json_path = os.path.join(skill_dir, ".claude-plugin", "plugin.json")

        if not os.path.isfile(skill_md):
            errors.append(f"{name}: missing {skill_md}")

        if not os.path.isfile(plugin_json_path):
            errors.append(f"{name}: missing {plugin_json_path}")
        else:
            with open(plugin_json_path) as f:
                pj = json.load(f)
            if pj.get("name") != name:
                errors.append(
                    f"{name}: plugin.json name '{pj.get('name')}' "
                    f"!= marketplace entry '{name}'"
                )

    if errors:
        print(f"FAIL: {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"PASS: {len(plugins)} plugins validated")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it to verify it fails (nothing generated yet)**

Run: `python3 scripts/validate_marketplace.py`
Expected: `FAIL: /Users/vitorbogo/Documents/dev/skills/.claude-plugin/marketplace.json does not exist` and exit code 1.

- [ ] **Step 3: Write the generation script**

```python
#!/usr/bin/env python3
"""Copy each skill from ~/.agents/skills into skills/<name> in this repo,
add a .claude-plugin/plugin.json to each, and write the root
.claude-plugin/marketplace.json listing all of them as separate plugins."""
import json
import os
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_ROOT = os.path.expanduser("~/.agents/skills")
MARKETPLACE_NAME = "vitorbogo-skills"
AUTHOR = {"name": "Vitor Bogo"}

SKILLS = {
    "caveman": (
        "Ultra-compressed communication mode. Cuts token usage ~75% by dropping "
        "filler, articles, and pleasantries while keeping full technical accuracy. "
        "Use when user says \"caveman mode\", \"talk like caveman\", \"use caveman\", "
        "\"less tokens\", \"be brief\", or invokes /caveman."
    ),
    "diagnose": (
        "Disciplined diagnosis loop for hard bugs and performance regressions. "
        "Reproduce → minimise → hypothesise → instrument → fix → regression-test. "
        "Use when user says \"diagnose this\" / \"debug this\", reports a bug, says "
        "something is broken/throwing/failing, or describes a performance regression."
    ),
    "find-skills": (
        "Helps users discover and install agent skills when they ask questions like "
        "\"how do I do X\", \"find a skill for X\", \"is there a skill that can...\", or "
        "express interest in extending capabilities. This skill should be used when "
        "the user is looking for functionality that might exist as an installable skill."
    ),
    "grill-me": (
        "Interview the user relentlessly about a plan or design until reaching shared "
        "understanding, resolving each branch of the decision tree. Use when user wants "
        "to stress-test a plan, get grilled on their design, or mentions \"grill me\"."
    ),
    "grill-with-docs": (
        "Grilling session that challenges your plan against the existing domain model, "
        "sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as "
        "decisions crystallise. Use when user wants to stress-test a plan against their "
        "project's language and documented decisions."
    ),
    "handoff": (
        "Compact the current conversation into a handoff document for another agent to "
        "pick up."
    ),
    "improve-codebase-architecture": (
        "Find deepening opportunities in a codebase, informed by the domain language in "
        "CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve "
        "architecture, find refactoring opportunities, consolidate tightly-coupled "
        "modules, or make a codebase more testable and AI-navigable."
    ),
    "prototype": (
        "Build a throwaway prototype to flesh out a design before committing to it. "
        "Routes between two branches — a runnable terminal app for state/business-logic "
        "questions, or several radically different UI variations toggleable from one "
        "route. Use when the user wants to prototype, sanity-check a data model or state "
        "machine, mock up a UI, explore design options, or says \"prototype this\", "
        "\"let me play with it\", \"try a few designs\"."
    ),
    "setup-matt-pocock-skills": (
        "Sets up an `## Agent skills` block in AGENTS.md/CLAUDE.md and `docs/agents/` so "
        "the engineering skills know this repo's issue tracker (GitHub or local "
        "markdown), triage label vocabulary, and domain doc layout. Run before first use "
        "of `to-issues`, `to-prd`, `triage`, `diagnose`, `tdd`, "
        "`improve-codebase-architecture`, or `zoom-out` — or if those skills appear to "
        "be missing context about the issue tracker, triage labels, or domain docs."
    ),
    "tdd": (
        "Test-driven development with red-green-refactor loop. Use when user wants to "
        "build features or fix bugs using TDD, mentions \"red-green-refactor\", wants "
        "integration tests, or asks for test-first development."
    ),
    "teach": (
        "Teach the user a new skill or concept, within this workspace."
    ),
    "to-issues": (
        "Break a plan, spec, or PRD into independently-grabbable issues on the project "
        "issue tracker using tracer-bullet vertical slices. Use when user wants to "
        "convert a plan into issues, create implementation tickets, or break down work "
        "into issues."
    ),
    "to-prd": (
        "Turn the current conversation context into a PRD and publish it to the project "
        "issue tracker. Use when user wants to create a PRD from the current context."
    ),
    "triage": (
        "Triage issues through a state machine driven by triage roles. Use when user "
        "wants to create an issue, triage issues, review incoming bugs or feature "
        "requests, prepare issues for an AFK agent, or manage issue workflow."
    ),
    "write-a-skill": (
        "Create new agent skills with proper structure, progressive disclosure, and "
        "bundled resources. Use when user wants to create, write, or build a new skill."
    ),
    "zoom-out": (
        "Tell the agent to zoom out and give broader context or a higher-level "
        "perspective. Use when you're unfamiliar with a section of code or need to "
        "understand how it fits into the bigger picture."
    ),
}


def main():
    skills_dir = os.path.join(REPO_ROOT, "skills")
    os.makedirs(skills_dir, exist_ok=True)

    marketplace_plugins = []

    for name, description in SKILLS.items():
        src = os.path.join(SOURCE_ROOT, name)
        dst = os.path.join(skills_dir, name)

        if not os.path.isdir(src):
            print(f"ERROR: source skill folder missing: {src}", file=sys.stderr)
            sys.exit(1)

        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        plugin_dir = os.path.join(dst, ".claude-plugin")
        os.makedirs(plugin_dir, exist_ok=True)
        plugin_manifest = {
            "name": name,
            "version": "1.0.0",
            "description": description,
            "author": AUTHOR,
            "license": "MIT",
        }
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(plugin_manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")

        marketplace_plugins.append(
            {
                "name": name,
                "source": f"./skills/{name}",
                "description": description,
            }
        )

    marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": AUTHOR,
        "plugins": marketplace_plugins,
    }

    marketplace_dir = os.path.join(REPO_ROOT, ".claude-plugin")
    os.makedirs(marketplace_dir, exist_ok=True)
    with open(os.path.join(marketplace_dir, "marketplace.json"), "w") as f:
        json.dump(marketplace, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Generated {len(marketplace_plugins)} plugin manifests + marketplace.json")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the generation script**

Run: `python3 scripts/generate_manifests.py`
Expected: `Generated 16 plugin manifests + marketplace.json`

- [ ] **Step 5: Run the validation script to verify it now passes**

Run: `python3 scripts/validate_marketplace.py`
Expected: `PASS: 16 plugins validated` and exit code 0.

- [ ] **Step 6: Spot-check that original file content survived the copy**

Run: `diff ~/.agents/skills/tdd/SKILL.md skills/tdd/SKILL.md && diff ~/.agents/skills/diagnose/scripts/hitl-loop.template.sh skills/diagnose/scripts/hitl-loop.template.sh`
Expected: no output from either `diff` (files are identical) and exit code 0.

- [ ] **Step 7: Commit**

```bash
git add scripts/validate_marketplace.py scripts/generate_manifests.py skills .claude-plugin/marketplace.json
git commit -m "Generate per-skill plugin manifests and marketplace.json"
```

---

### Task 3: Create the GitHub repo and push

**Files:** none (no file changes — this task creates the remote and pushes existing commits)

**Interfaces:**
- Consumes: the two commits from Task 1 and Task 2 already sitting on the local `main` branch.
- Produces: `Vitorbogo/skills` on GitHub, with `origin` pointing at it and `main` pushed.

- [ ] **Step 1: Confirm gh is authenticated with the right account**

Run: `gh api user --jq '.login'`
Expected: `Vitorbogo`

- [ ] **Step 2: Confirm the local repo has no uncommitted changes**

Run: `git status --short`
Expected: no output (clean working tree) — Tasks 1 and 2 should already be committed.

- [ ] **Step 3: Create the GitHub repo, add it as `origin`, and push**

This is a visible, external action (creates a public repo under Vitorbogo's account and pushes code to it) — confirm with Vitor before running if this plan is being executed unattended.

Run: `gh repo create Vitorbogo/skills --public --source=. --remote=origin --description "Vitor Bogo's personal Claude Code skills marketplace" --push`
Expected: output confirming repo creation, e.g. `✓ Created repository Vitorbogo/skills on GitHub` followed by a successful push.

- [ ] **Step 4: Verify the push landed**

Run: `gh repo view Vitorbogo/skills --json url,defaultBranchRef --jq '.url, .defaultBranchRef.name'`
Expected: prints `https://github.com/Vitorbogo/skills` then `main`.

---

### Task 4: Verify installation works from the marketplace

**Files:** none (this task exercises the plugin system; no repo files change)

**Interfaces:**
- Consumes: `Vitorbogo/skills` published on GitHub from Task 3.

- [ ] **Step 1: Add the marketplace**

In a Claude Code session, run:
```
/plugin marketplace add Vitorbogo/skills
```
Expected: confirmation that the `vitorbogo-skills` marketplace was added.

- [ ] **Step 2: Install two skills as a sample**

```
/plugin install diagnose@vitorbogo-skills
/plugin install tdd@vitorbogo-skills
```
Expected: both report successful installation.

- [ ] **Step 3: Reload skills and confirm they're active**

Run the `/reload-skills` command.
Expected: skill count includes `diagnose` and `tdd` with no errors reported.

- [ ] **Step 4: Diff installed content against the original source**

Run:
```bash
INSTALLED=$(find ~/.claude/plugins/cache/vitorbogo-skills -maxdepth 1 -type d -name 'diagnose*' | head -1)
diff -r ~/.agents/skills/diagnose "$INSTALLED"
```
Expected: no output (content matches byte-for-byte) aside from the added `.claude-plugin/plugin.json`, which `diff -r` will report as "Only in $INSTALLED/.claude-plugin: plugin.json" — that single line is expected; anything else is a mismatch to investigate before proceeding to Task 5.

---

### Task 5: Retire the old manual setup

**Files:**
- Delete: `~/.claude/skills/*` (all 16 symlinks)
- Delete: `~/.agents/skills/` (entire directory)

**Interfaces:** none — this is cleanup of files outside this repo, with no interfaces other tasks depend on.

**Do not run this task until Task 4's diff check has passed.** This step is destructive and hard to reverse (no upstream copy remains once `~/.agents/skills` is deleted) — confirm with Vitor immediately before running if executing unattended.

- [ ] **Step 1: List what will be removed, for a final look before deleting**

Run: `ls -la ~/.claude/skills && echo --- && ls -la ~/.agents/skills`
Expected: the 16 symlinks and the 16 source folders, matching what Task 2 copied from.

- [ ] **Step 2: Remove the symlinks**

Run: `rm ~/.claude/skills/caveman ~/.claude/skills/diagnose ~/.claude/skills/find-skills ~/.claude/skills/grill-me ~/.claude/skills/grill-with-docs ~/.claude/skills/handoff ~/.claude/skills/improve-codebase-architecture ~/.claude/skills/prototype ~/.claude/skills/setup-matt-pocock-skills ~/.claude/skills/tdd ~/.claude/skills/teach ~/.claude/skills/to-issues ~/.claude/skills/to-prd ~/.claude/skills/triage ~/.claude/skills/write-a-skill ~/.claude/skills/zoom-out`

- [ ] **Step 3: Remove the old source directory**

Run: `rm -rf ~/.agents/skills`

- [ ] **Step 4: Verify no duplicate/dangling skills remain**

Run: `ls ~/.claude/skills`
Expected: empty (or only entries unrelated to this migration, if any exist).

- [ ] **Step 5: Run `/reload-skills` once more**

Expected: the same skills as Task 4 Step 3 are still reported active (now served purely from the installed plugin, not the old symlinks).
