---
type: reference
description: The vault protocol, how to read, write, route, and shape a note. Read before touching the vault.
tags: [meta, conventions]
created: {{date}}
---

# Vault conventions

This file is the single source of the vault protocol. Every agent that reads or writes here follows it.

## What this vault is

The working knowledge of {{owner}}: decisions, architecture, and lessons, curated so each note is worth reading. It is not a log. The code and git history are the log.

## Structure

Each top-level folder is a domain. Each domain has a MOC (Map of Content) as its entry point. Inside a domain, knowledge grows as atomic notes linked by `[[wikilinks]]`, not as nested folders.

{{domains}}
- `Meta/`: vault rules and templates.

`INDEX.md` at the root is generated. It lists every note with its description. Never edit it by hand.

## Read

`INDEX.md` → the domain MOC → the notes. Grep only for what those do not surface.

## Write

Save a decision (with its reason and the discarded alternatives), an investigation with a conclusion, a domain pattern, or a gotcha. Leave intermediate steps and anything the code or git already records to the environment.

One fact per note. Update an existing note before you add a new one. Link every new note from its domain MOC.

## Note shape

```markdown
---
type: decision | investigation | pattern | gotcha | reference
description: One line that says what the note holds.
tags: [domain, topic]
related: ["[[other-note]]"]
created: YYYY-MM-DD
---
```

Every note has a `description`. It is the note's line in `INDEX.md`, so it states the claim itself, specific enough to pick the note without opening it.
