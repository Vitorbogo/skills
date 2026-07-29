# Personal Skills Marketplace — Design

## Goal

Vitor currently has Matt Pocock's skill set (`mattpocock/skills`) installed
globally as plain files: real content lives in `~/.agents/skills/<name>/`,
with symlinks from `~/.claude/skills/<name>` pointing at them. Neither
location is a git repo, so there is no way to edit a skill, version the
change, or reinstall the same set on another machine.

This design creates a new repo, `vitorbogo/skills`, that becomes the single
source of truth for Vitor's skills going forward: an installable Claude Code
**plugin marketplace**, seeded from the skills he already has, editable
directly, and extensible with skills from other sources over time.

## Non-goals

- No upstream tracking / git-fork relationship with `mattpocock/skills`. This
  is a one-time copy; Vitor's copy is free to diverge.
- No new skills from other sources are added in this pass — only structure +
  migration of the existing 16 skills. Adding more sources is a later,
  separate, incremental step (drop in a folder, add a manifest, add one
  marketplace entry).
- No thematic bundling — every skill is deliberately its own installable
  plugin (see Decisions).

## Repository

- Name: `vitorbogo/skills`, public, on GitHub.
- Built at `/Users/vitorbogo/Documents/dev/skills` (already the working
  directory for this project; currently empty aside from `.claude/`).

## Structure

```
skills/
├── .claude-plugin/
│   └── marketplace.json          # one entry per skill (~16 total)
├── skills/
│   ├── caveman/
│   │   ├── .claude-plugin/plugin.json
│   │   └── SKILL.md
│   ├── diagnose/
│   │   ├── .claude-plugin/plugin.json
│   │   └── SKILL.md
│   ├── find-skills/...
│   ├── grill-me/...
│   ├── grill-with-docs/...
│   ├── handoff/...
│   ├── improve-codebase-architecture/...
│   ├── prototype/...
│   ├── setup-matt-pocock-skills/...   # keeps its extra template files
│   ├── tdd/...
│   ├── teach/...
│   ├── to-issues/...
│   ├── to-prd/...
│   ├── triage/...
│   ├── write-a-skill/...
│   └── zoom-out/...
├── README.md
└── LICENSE                        # MIT, Matt Pocock's copyright retained
```

Every skill folder keeps whatever supporting files it already has beyond
`SKILL.md` (e.g. `setup-matt-pocock-skills` ships extra template docs) — the
migration is a full-folder copy, not just the `SKILL.md`.

## Manifests

`.claude-plugin/marketplace.json` (root) — one entry per skill:

```json
{
  "name": "vitorbogo-skills",
  "owner": { "name": "Vitor Bogo" },
  "plugins": [
    { "name": "caveman", "source": "./skills/caveman", "description": "..." },
    { "name": "diagnose", "source": "./skills/diagnose", "description": "..." }
  ]
}
```

Each skill's `.claude-plugin/plugin.json`:

```json
{
  "name": "diagnose",
  "version": "1.0.0",
  "description": "...",
  "author": { "name": "Vitor Bogo" },
  "license": "MIT"
}
```

Descriptions are pulled from each skill's existing `SKILL.md` frontmatter
`description:` field rather than written from scratch.

## Decisions and reasoning

- **One plugin per skill, not thematic bundles.** Confirmed with Vitor after
  verifying the actual Claude Code UX: there is no multi-select checkbox
  screen — `/plugin install` installs one plugin at a time regardless of
  grouping. Vitor explicitly kept max granularity anyway, valuing the ability
  to cherry-pick individual skills over fewer install commands.
- **No upstream tracking.** Vitor wants to be able to edit any skill freely
  and have that be authoritative — a plain copy avoids fork/merge friction
  with `mattpocock/skills`.
- **Plugin marketplace format over plain symlinked folder.** Vitor wants easy
  install on new machines/repos without re-doing manual symlinks each time;
  the plugin system (same one already used for `superpowers` and
  `frontend-design` in his global config) gives him `/plugin marketplace add`
  + `/plugin install` instead.

## Install / update workflow (after this ships)

- One-time per machine: `/plugin marketplace add vitorbogo/skills`
- Per skill wanted: `/plugin install <skill-name>@vitorbogo-skills`
- To change a skill: edit the file in the repo, commit + push, then
  `/plugin marketplace update vitorbogo-skills` (or reinstall) to pick up the
  change wherever it's installed.
- To add a new skill later (own or from another source): create
  `skills/<name>/` with `SKILL.md` + `.claude-plugin/plugin.json`, add one
  entry to `marketplace.json`, commit.

## Migration and cleanup

1. Copy each skill's full folder contents from `~/.agents/skills/<name>` into
   `skills/<name>/` in the new repo; add each skill's `plugin.json`; build
   `marketplace.json` from the 16 entries.
2. `git init`, initial commit, create the GitHub repo `vitorbogo/skills`
   (public), push.
3. Verify: `/plugin marketplace add vitorbogo/skills`, install 2-3 skills,
   `/reload-skills`, confirm they load and behave the same as the originals.
4. Only once verified: remove the symlinks under `~/.claude/skills/*` and
   delete `~/.agents/skills/`, so the plugin is the single remaining source.
   (Do not delete before verification passes — this is the point of no easy
   return for the old setup.)

## Licensing / attribution

`mattpocock/skills` is MIT-licensed, which requires the copyright notice be
retained in copies of the software. The new repo's root `LICENSE` stays MIT
and keeps Matt Pocock's original copyright line, with an added line noting
Vitor's repo is a maintained derivative. `README.md` credits and links
`mattpocock/skills` as the origin of the initial skill set.
