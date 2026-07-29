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
