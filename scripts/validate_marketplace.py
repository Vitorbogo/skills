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
