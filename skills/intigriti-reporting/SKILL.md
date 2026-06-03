---
name: intigriti-reporting
description: Intigriti report template — ITG-VR mapping, severity, "fluff-free" submission style.
keywords: [intigriti, itg-vr, bug bounty europe, european bb platform]
---

# intigriti-reporting

## When this skill loads

`/report platform=intigriti`.

## ITG-VR (Intigriti Vulnerability Rating)

Similar in spirit to Bugcrowd VRT, mapped to 5 severities:

```
Exceptional   — RCE pre-auth, ATO without UI, mass data leak
Critical      — ATO with UI, SSRF to cloud admin, privilege escalation
High          — SQLi to data, stored XSS auth, IDOR with PII
Medium        — reflected XSS, CSRF on state change, info disclosure
Low           — open redirect chained, missing security headers with chain
```

## Etiquette

- Intigriti triagers are notably strict about "fluff" — avoid
  preamble.
- Title prefix the asset: `[app.example.com] Pre-auth RCE via ...`
- "Severity self-rating" field — be honest; over-rating triggers
  punitive triage.
- "Steps to Reproduce" must be machine-copy-pasteable for triagers
  with no context.

## Template

```markdown
**Asset:** https://app.example.com
**Endpoint:** POST /api/v1/user/profile
**Severity (self):** Critical

## Summary
<1-2 sentences>

## Steps to Reproduce
1. ...
2. ...

## Impact
<one paragraph; business terms>

## Remediation
<specific, cite RFC/OWASP>

## CVSS
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N — 7.5 (High)

## Supporting Material
- evidence/full.har
- evidence/01-unauth.png evidence/02-trigger.png evidence/03-impact.png
```

## See also

- `h1-reporting`, `bugcrowd-reporting`
- `report-writing`
