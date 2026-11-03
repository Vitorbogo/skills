---
name: vault
description: Read and write the knowledge vault, a folder of linked markdown notes that serves as long-term memory. Use before a task in a domain the vault covers, when recording a decision, a concluded investigation, or a gotcha, or when the session start names a vault.
---

# Vault

The vault is curated memory: few notes, each one worth reading. Its path is in `$VAULT_PATH`, and the session start names it.

The vault's own `Meta/conventions.md` is the source of truth. Where it differs from this skill, it wins.

## Read

1. **Index.** Read `INDEX.md` at the vault root. It lists every note with its one-line description. The session start often injects it already.
2. **MOC.** Open the Map of Content for the task's domain. It is the domain's entry point.
3. **Notes.** Open the notes the index and the MOC point to. Follow their `[[wikilinks]]` one hop when the link bears on the task.

Grep the vault only for a term the index and MOCs do not surface.

Done when you have read every note whose description bears on the task, or you know none does.

## Write

Write proactively. The filter below curates the vault, so the human does not have to.

**Save:**

- A decision, with its reason and the alternatives discarded.
- An investigation with a conclusion: a root cause, an analysis that cost time.
- A domain pattern: how a part of the system behaves, and why.
- A gotcha: a trap that looks fine and is not.

**Leave to the environment:** intermediate steps, anything the code or git history already records, and facts that matter only to this session.

### Note shape

One fact per note: an **atomic** note. Before writing, check the index for a note that already covers the fact, and update it instead.

```markdown
---
type: decision | investigation | pattern | gotcha | reference
description: One line that says what the note holds.
tags: [domain, topic]
related: ["[[other-note]]"]
created: YYYY-MM-DD
---

# Title

The fact. Then **Why:** and, where useful, **How to apply:**.
```

The `description` is the note's pointer in the index. Write it so an agent can pick the note from the index without opening it: the claim itself, not the topic. "The loader skips tables without a manifest" beats "Notes about the loader".

### Route and link

- Save the note in the folder for its domain, following the routing in `Meta/conventions.md`.
- Link it from that domain's MOC, and link related notes both ways.
- A hook rebuilds `INDEX.md` after every write to a vault note, and lints that note. When it reports a problem, fix the note.

Done when the note has a description, sits in its domain folder, and its MOC links to it.
