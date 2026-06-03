---
name: memory-gc
description: Compact engagement notes; archive verdicts older than 30 days; rebuild summary indices.
---

# /memory-gc

**Args:** `[engagement=<folder>] [archive-after-days=30]`

## What this command does

1. For each engagement folder (or the single one if `engagement=` is
   supplied):
   - Compact `recon-notes.md` — dedupe subdomain / endpoint lists,
     move retired sections to `recon-notes.archived.md`.
   - Index findings into a single `findings/_index.md` table
     (`id | class | severity | status | ship_date | platform`).
   - If a finding's `status: shipped` and `ship_date >
     archive-after-days` ago, prompt to archive the whole engagement.
2. Refuses to touch files whose mtime is < 24h old (avoids
   stomping on active work).
3. Writes a per-engagement health report to
   `engagement/_gc-<date>.md`.

## Output contract

```
Scanned: 6 engagements
Compacted: 4 recon-notes.md (saved 12.4 KB / removed 412 dup lines)
Indexed:   18 findings across 6 engagements
Archive candidates:
  • engagements/example.com-2025-12-01/ — 3 shipped findings, 45 days old
  • engagements/acme-redteam-2025-11-22/ — 2 client-deliverables, 67 days old

Confirm archive? (y/N)
```

## Discipline

- Archive process: `tar + gpg --symmetric` with a passphrase the
  operator chooses; CBH never persists the passphrase.
- `/memory-gc` is **idempotent** — running it twice with no new
  data should be a no-op.
