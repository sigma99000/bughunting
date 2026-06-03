---
name: triage-validation
description: 7-question validation gate. Routes findings to SHIP, CHAIN-REQUIRED, DOWNGRADE, or KILL.
keywords: [triage, validation, gate, ship, kill, downgrade, dedupe, scope check, severity]
---

# triage-validation

## When this skill loads

This is the **mandatory** pre-report gate. It auto-loads whenever
`/validate` is invoked, and is referenced from every `hunt-*` skill's
"Never-submit fallbacks" section.

## The 7 questions

Each must be answered with **evidence**, not assertion. Evidence is
a file path + line range or a screenshot filename.

### Q1 — Is there a real HTTP request demonstrating the impact?

PASS if:
- A captured HAR shows the exact request/response that triggers impact
- A curl one-liner reproduces it from a clean shell
- A multi-step PoC is captured in screenshots with timestamps

FAIL → **KILL**. Theory is not a bug.

### Q2 — Is the impact on the program's accepted-impact list?

Read `scope.md` `## Accepted impact`. Map the finding's impact to the
program's taxonomy:

| Finding | Maps to | Verdict |
|---|---|---|
| ATO without UI | "Critical: ATO without user interaction" | PASS |
| Stored XSS (authenticated) | "Medium: stored XSS in auth context" | PASS |
| Self-XSS | (not present in any program's accepted list) | KILL |
| Missing security header | (excluded for most programs) | KILL or DOWNGRADE |

FAIL → **KILL or DOWNGRADE** depending on whether a lower-severity
mapping exists.

### Q3 — Is the asset in scope per domain/subdomain rules?

Read `scope.md` `## In scope` and `## Out of scope`.

- Apex match (`example.com`) ≠ subdomain match unless wildcard is
  declared.
- "Mobile app" scope ≠ "API" scope unless explicitly listed.
- Third-party SaaS hosted at `*.example.com` is usually out of scope.

FAIL → **KILL**. Out-of-scope reports damage researcher reputation.

### Q4 — Is the finding free of admin-only / same-user / self-only
assumptions?

- Admin can do bad thing → not a bug; admins are trusted.
  - **Exception**: bypassing admin scoping (e.g., low-admin reads
    super-admin secrets).
- Self-XSS, self-IDOR (your own data) → not a bug.
- Requires the victim to paste something into their browser → DOWNGRADE.

FAIL → **DOWNGRADE** or **KILL**.

### Q5 — Has it been publicly disclosed, or is it on the program's
known-issues list?

Check:
1. The program's hacktivity (HackerOne) / public reports.
2. `scope.md` `## Known issues`.
3. Your own past submissions (`engagements/*/findings/`).
4. Public CVE databases — if the target is running a known-vulnerable
   version, the CVE-itself isn't novel; you must add the
   *exploitation chain* in their environment.

FAIL → **KILL**.

### Q6 — Is the impact concretely demonstrated, not "technically
possible"?

- "An attacker could pivot to internal" → CHAIN REQUIRED until you
  actually pivot.
- "If the secret is valid, attacker has access" → run the validator
  curl one-liner and prove the secret is live.
- "The endpoint accepts arbitrary URLs" → fetch a metadata endpoint
  and dump credentials.

FAIL → **CHAIN REQUIRED**. Go back to `/chain`.

### Q7 — Is the finding **not** on the universal never-submit list?

Universal never-submit (independent of program):

- Logout CSRF
- Self-XSS (paste-in-console)
- Banner grabbing / version disclosure alone
- Missing security headers without an attack chain
- EXIF metadata in user-uploaded images
- Rate-limit-only findings (no auth-bypass, no monetary impact)
- Clickjacking on non-state-changing pages
- Cookie missing `Secure` / `HttpOnly` when there's no
  exploitable XSS to read it
- TLS version downgrade without MITM proof
- HSTS missing without proof of stripping attack
- Reflected file download
- Open redirect alone (only valuable as a chain primitive — see
  `hunt-redirect`)

FAIL → **KILL**.

## Verdicts

| Verdict | Meaning | Next step |
|---|---|---|
| **SHIP** | All 7 pass → reportable | `/report` |
| **CHAIN REQUIRED** | Q6 fail | `/chain` — add concrete impact |
| **DOWNGRADE** | Q2 or Q4 fail (lower-severity mapping exists) | adjust severity, restart Q-loop |
| **KILL** | Any KILL-trigger fail | mark `findings/<id>.killed.md` with reason |

## Output template

```
Finding: <id>
Q1 real request?      ✅ <evidence>
Q2 accepted impact?   ✅ <mapping>
Q3 in scope?          ✅ <asset matches rule>
Q4 admin-only?        ✅ <user role>
Q5 disclosed?         ✅ <search results>
Q6 concrete impact?   ✅ <evidence>
Q7 never-submit?      ✅ <not on list>

VERDICT: SHIP
Severity: <CVSS>
```

## Discipline

- **No skipping**: every Q must have a recorded answer, even if
  trivially "yes". The audit trail matters when triagers push back.
- **No re-running until evidence changes**: don't keep asking the
  same question; gather data, then re-validate.
- Pair with `evidence-hygiene` before `/report`.

## See also

- `evidence-hygiene` — Q1's evidence must be redacted
- `bugcrowd-reporting`, `h1-reporting`, etc. — Q2's mapping uses the
  platform's taxonomy
- `scope-discipline` — Q3 enforcement
