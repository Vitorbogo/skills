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
