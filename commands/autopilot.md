---
name: autopilot
description: Run surface→recon→intel→hunt non-stop. Pauses for operator confirmation on destructive payloads.
---

# /autopilot

**Args:** `target=<host> [mode=bugbounty|pentest|redteam] [stop-at=intel|hunt|chain]`

## What this command does

Sequentially invokes:

1. `/surface target=<host>` (if no engagement folder yet)
2. `/recon target=<host>` (passive + light)
3. `/intel target=<host>`
4. `/hunt target=<host>` (for each class suggested by intel)
5. Pauses before any destructive payload (`rce`, `cmdi`,
   `deserialization`, `path-traversal` writes) and asks for explicit
   "yes, authorized" confirmation.

In `mode=redteam`, also loads `redteam-mindset` and
`mid-engagement-ir-detection` (the latter spawns a parallel baseline
snapshot of probed endpoints; re-checks every 30 min for changes).

## Output contract

A scrolling status line:

```
[surface] ✅ engagement scaffolded
[recon ] ✅ 247 subs, 14 live, 3 secrets
[intel ] ✅ Spring Boot 2.6 + Okta — 4 CVEs, 6 misconfig classes
[hunt  ] ⏵ class=ssti — 3 phases queued
         ⏵ class=oauth — 5 phases queued
         ⏵ class=jwt   — 4 phases queued
[pause ] one of the queued payloads is destructive: confirm? (y/n)
```

## Discipline

- Autopilot **never** auto-reports. The final step before any submit
  is always an interactive `/validate` + `/report` invocation by the
  operator.
- `stop-at=intel` is the safe default for first-touch engagements.
- The `mid-engagement-ir-detection` background poll is the only thing
  in CBH that runs without per-call confirmation, and only in
  red-team mode.
