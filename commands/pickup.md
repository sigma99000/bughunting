---
name: pickup
description: Resume an engagement. Re-reads scope, chains, last verdict, suggests next step.
---

# /pickup

**Args:** `engagement=<folder-path>`

## What this command does

1. Reads `engagement/scope.md` end-to-end. If it's > 30 days old,
   warn that bounty scope may have drifted.
2. Reads `chains.md`. Surfaces any chain with status `WIP`.
3. Reads the most recent file in `findings/`. Reports its verdict.
4. Reads the tail of `recon-notes.md` to see what was last enumerated.
5. Asks the operator: "Where do you want to continue?" with
   suggested resume points.

## Output contract

```
Engagement: app.example.com-2026-01-15 (3 days old)
Scope: in-scope=4 hosts, out-of-scope=2, accepted=P1-P3
Last finding: oauth-redirect-bypass-001 — verdict SHIP — H1 #XXXXX
WIP chains: 1
  • chain-002: subdomain-takeover-to-ATO (blocker: need exposed
    cookie-domain endpoint on *.example.com)
Last recon action: nuclei -t cves/ — 2 high finds, 7 info

Resume options:
  1. Unblock chain-002 — hunt for cookie-domain leakage
  2. Investigate nuclei high finds (CVE-2024-XXXXX on legacy-api)
  3. Run /token-scan on newly-discovered JS bundles
```

## Discipline

- Don't silently re-run things — list what's already done.
- If the operator says "continue from where I left off", pick option
  1 by default.
