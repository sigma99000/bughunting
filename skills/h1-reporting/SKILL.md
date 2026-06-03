---
name: h1-reporting
description: HackerOne report template — title convention, CWE mapping, severity (CVSS 3.1), program-specific etiquette.
keywords: [hackerone, h1, hacktivity, cvss, cwe, report, triage]
---

# h1-reporting

## When this skill loads

`/report platform=h1`.

## H1 title convention

`<verb> <asset> via <vector> [<class>]`

Examples:

- `Account takeover on app.example.com via OAuth redirect_uri allow-list bypass`
- `Stored XSS in /profile/bio via CSP-bypass with JSONP endpoint`
- `SSRF on api.example.com import-from-URL → GCP metadata creds`

Avoid:
- "Critical vulnerability found" (no specifics)
- "RCE in <product>" (too vague)
- All caps, exclamation marks

## Field-by-field

### Asset
Pick the **exact** subdomain. H1 dedupes by asset; wrong asset =
triage delay.

### Weakness (CWE)
Map to the closest CWE. Common picks:

| Finding | CWE |
|---|---|
| Stored / reflected XSS | CWE-79 |
| SQL injection | CWE-89 |
| OS command injection | CWE-78 |
| SSRF | CWE-918 |
| XXE | CWE-611 |
| IDOR | CWE-639 |
| OAuth redirect_uri | CWE-601 (open redirect) or CWE-863 (broken authz) |
| Deserialization | CWE-502 |
| Path traversal | CWE-22 |
| Mass assignment | CWE-915 |
| Race condition | CWE-362 |
| HTTP request smuggling | CWE-444 |
| Cache poisoning | CWE-444 (poisoning), CWE-913 |
| Server-side template injection | CWE-94 |
| JWT alg=none / RS/HS confusion | CWE-345 / CWE-347 |

### Severity (CVSS 3.1)
Use FIRST's calculator. Pin specific vector components:

- `AV:N` (network) — always for external
- `AC:L` (low complexity) — unless requires race/MITM
- `PR:N` (no privs) for pre-auth; `PR:L` for single-account; `PR:H` for admin
- `UI:N` for no interaction; `UI:R` for OAuth/click required
- `S:C` (scope changed) when attacker reaches different security
  domain (e.g., XSS in tenant A reaches tenant B data) — bump score
- `C:H/I:H/A:N` (confidentiality+integrity high, availability not impacted)
  — typical ATO vector

Programs sometimes override severity downward to fit their bounty
tiers — don't argue; the **CVSS vector** is what stays in the report
for posterity.

## H1 template

```markdown
## Summary

A misconfiguration in the OAuth 2.0 `redirect_uri` allow-list on
app.example.com permits an attacker to redirect victims to an
attacker-controlled domain after authorization, capturing the
authorization code and exchanging it for a victim session.

## Steps to reproduce

(All steps numbered. Variable values in `${...}` form. No live tokens.)

1. As a registered user (test account: ${ATTACKER_HANDLE}), navigate to:
   `https://app.example.com/auth/oauth/init?provider=google`
2. In the resulting `redirect_uri` parameter, observe the value:
   `https://app.example.com/auth/callback`
3. Modify the URL to:
   `https://app.example.com/auth/oauth/init?provider=google&redirect_uri=https://app.example.com.attacker.com/`
4. Note that the OAuth flow proceeds and the authorization code is
   delivered to `attacker.com`.
5. Exchange the code for a session: ...

(Continue. Always end on a screenshot demonstrating the impact.)

## Supporting material / references

- `evidence/oauth-redirect-bypass.har` (redacted)
- `evidence/01-unauth.png` `evidence/02-redirect.png` `evidence/03-takeover.png`
- OWASP OAuth Security Cheat Sheet § "Redirect URI Validation"
- RFC 6749 § 3.1.2 redirect_uri validation

## Impact

An external attacker can take over any user account on
app.example.com by sending the victim a single link. No additional
interaction beyond clicking the link is required (the victim must
be logged in, which is the normal state). Account takeover exposes
all user data, payment methods, and the ability to act on the
victim's behalf.

## CVSS

CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N — 8.1 (High)
```

## Etiquette

- **Don't open a "fix verification" report**; use the "Re-test"
  button.
- **Respond within 7 days** to triager comments or risk closure.
- **Don't request bounty re-grade** before remediation is confirmed —
  it looks coercive.
- **Acknowledge fix**: confirm in 2 sentences that the fix patches
  the issue and the variants you tested. Variants worth testing
  separately become new reports.

## See also

- `triage-validation`
- `bugcrowd-reporting` — for cross-platform mental model
- `evidence-hygiene`
