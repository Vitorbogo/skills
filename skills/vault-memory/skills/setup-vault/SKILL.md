---
name: setup-vault
description: Create a new knowledge vault, or adopt an existing folder of notes, and wire it to the agent.
disable-model-invocation: true
argument-hint: "[path to the vault]"
---

# Setup vault

Sets up a vault the `vault` skill can read and write. The path comes from the argument; ask for it when there is none.

## 1. Pick the branch

- The folder is missing or empty → **Create** (step 2).
- The folder already holds markdown notes → **Adopt** (step 3).

## 2. Create

1. Ask which domains the vault covers. Offer this default: `Projects/`, `Infra/`, `Clients/`, `Internal/`.
2. Create one folder per domain, plus `Meta/`.
3. Write `Meta/conventions.md` from [conventions-template.md](conventions-template.md). Fill every `{{placeholder}}`; `{{domains}}` becomes one line per domain folder.
4. In each domain folder, write a MOC named `<Domain> MOC.md`, from [moc-template.md](moc-template.md), placeholders filled.
5. Write `Home.md` at the root, linking every MOC.

Go to step 4.

## 3. Adopt

1. Read the vault's existing conventions file, if it has one. Add the `description` rule from [conventions-template.md](conventions-template.md) to it, in the vault's own voice. Leave its other rules as they are.
2. Run `python3 "${CLAUDE_SKILL_DIR}/../../scripts/build_index.py" <path>`. The `## Missing description` section of `INDEX.md` lists the work.
3. For each note in that list, read it and add a one-line `description` to its frontmatter. Add the frontmatter block when the note has none. Change nothing else in the note.
4. Rerun the script.

Done when the script reports 0 notes without a description.

## 4. Wire

1. Ask where the vault applies:
   - every project → `~/.claude/settings.json`;
   - one project → `.claude/settings.local.json` in that project.
2. In that file, set `"env": { "VAULT_PATH": "<absolute path>" }`. Merge it with any `env` already there.
3. Run the script once more, and show the user the summary line.

Tell the user the vault loads at the next session start.
