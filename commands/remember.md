---
name: remember
description: Append a durable note to the current engagement's memory log.
---

# /remember

**Args:** `note=<free text> [tag=<label>]`

## What this command does

Appends a timestamped line to the current engagement's
`recon-notes.md` under a `## remembered notes` section. Optional
`tag=` lets the operator group notes for later grep
(`tag=primitive`, `tag=blocker`, `tag=question`).

## Example

```
/remember note="legacy-api uses RS256 with a JWK URL — try kid=../../etc/passwd injection" tag=primitive
```

Appends:

```
- 2026-01-18T14:22Z [primitive] legacy-api uses RS256 with a JWK URL —
  try kid=../../etc/passwd injection
```

## Discipline

- Notes are append-only — never edit or delete. To retract, append a
  retraction note referencing the original timestamp.
- For sensitive notes (credentials, tokens), use `tag=secret` — those
  are mirrored to `evidence/secret-notes.txt` (mode 0600) instead of
  the markdown.
