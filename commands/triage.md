---
name: triage
description: Decide reportable-or-not. Dedupes against known issues and prior submissions.
---

# /triage

**Args:** `finding=<id>`

## What this command does

`/triage` is the pre-report gate that runs **after** `/validate`:

1. Re-reads `scope.md` `## Known issues` section.
2. Checks `engagements/*/findings/` for prior submissions of the same
   class on the same asset (own-dupe detection).
3. Optionally consults H1 hacktivity (operator pastes the program's
   public-disclosure URL list) for external duplicates.
4. Categorizes against the program's taxonomy:
   - **Bugcrowd:** maps to a VRT category (loaded from
     `bugcrowd-reporting`).
   - **HackerOne:** maps to the program's CWE allow-list.
   - **Intigriti:** maps to ITG-VR.

## Output contract

```
Finding: <id>
Class taxonomy match: <CWE-79 / VRT P1 / ITG-001>
Duplicate check:
  Internal (this engagement): 0 hits
  Internal (other engagements, same target): 0 hits
  External (program hacktivity): operator to confirm
Severity adjustment: Critical → High (program caps OAuth ATO at High)
Bounty estimate (per program table): $4,000–$6,000

VERDICT: REPORTABLE
Next: /report finding=<id> platform=<...>
```

## Discipline

- Never assume a dupe — surface candidates and ask the operator.
- Bounty estimates are advisory, never definitive.
- For red-team engagements, `/triage` instead produces a
  client-narrative paragraph (loaded from `redteam-report-template`).
