---
name: validate
description: Run a finding through the 7-question validation gate. Returns SHIP, CHAIN-REQUIRED, DOWNGRADE, or KILL.
---

# /validate

**Args:** `finding=<id>`

## What this command does

Loads `triage-validation`. Walks the 7-question gate:

| # | Question | Fail verdict |
|---|----------|--------------|
| Q1 | Real HTTP request demonstrating the impact? | KILL |
| Q2 | Impact on the program's accepted-impact list? | KILL or DOWNGRADE |
| Q3 | In scope per domain/subdomain rules? | KILL |
| Q4 | Free of admin-only / same-user / self-only assumptions? | DOWNGRADE |
| Q5 | Not publicly disclosed / not in program known-issues? | KILL |
| Q6 | Concrete demonstrated impact (not "technically possible")? | CHAIN REQUIRED |
| Q7 | Not on the never-submit list? | KILL |

For each Q, Claude must cite the evidence (file path, line, screenshot
name) that supports the answer. Bare "yes" is not acceptable.

## Output contract

```
Finding: <id>
Q1 real request?       ✅ evidence/oauth-poc.har § request 12
Q2 accepted impact?    ✅ ATO listed P1 in scope.md
Q3 in scope?           ✅ app.example.com ∈ *.example.com
Q4 admin assumption?   ✅ standard user role (evidence/02-victim-role.png)
Q5 publicly disclosed? ✅ H1 hacktivity search 2026-01-15 — 0 dupes
Q6 concrete impact?    ✅ evidence/03-victim-takeover.png
Q7 never-submit list?  ✅ ATO is explicitly accepted

VERDICT: SHIP
Severity: Critical (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N → 8.1)
Next: /report finding=<id> platform=<h1|bc|...>
```

## Discipline

- Any "skip" or "n/a" on a question forces verdict = NEEDS-CLARIFICATION,
  not SHIP.
- `KILL` verdicts go to `findings/<id>.killed.md` with reason — useful
  for portfolio review.
- `DOWNGRADE` does not auto-rewrite severity; it triggers a
  re-classification step where Claude proposes the new severity and
  the operator confirms.
