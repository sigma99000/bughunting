---
name: bugcrowd-reporting
description: Bugcrowd VRT mapping + Bugcrowd-style submission template with severity justification.
keywords: [bugcrowd, vrt, bugcrowd taxonomy, p1, p2, p3, p4, p5, severity, report]
---

# bugcrowd-reporting

## When this skill loads

`/report platform=bc`.

## Bugcrowd VRT primer

Bugcrowd's Vulnerability Rating Taxonomy is hierarchical:

```
P1 Critical (RCE, full ATO, exec admin)
P2 Severe (auth bypass, IDOR with PII, SSRF to internal)
P3 Moderate (stored XSS auth, CSRF state-changing, info disclosure with PII)
P4 Low (reflected XSS, IDOR without PII, open redirect chained)
P5 Informational (banner, lacking headers, version disclosure)
```

Always cite the **VRT category** in the submission. Examples:

- `Server Security Misconfiguration > OAuth Misconfiguration > Account Takeover`
- `Broken Access Control > Insecure Direct Object Reference > Read`
- `Server-Side Injection > Cross-Site Scripting (XSS) > Stored`

## VRT fallback rules

When the finding doesn't match a leaf node:

1. Climb to the nearest parent that fits.
2. Note in submission: "Closest VRT: X.Y (no leaf for this variant)".
3. Don't invent categories — Bugcrowd triagers will renumber.

## Severity justification paragraph

Every Bugcrowd submission must include a "Why this is P<N>" paragraph
that maps the demonstrated impact to the VRT severity definition.
Example for a P2 IDOR:

> This finding meets P2 severity per Bugcrowd VRT 1.13 §
> "Insecure Direct Object Reference > Read". The PoC demonstrates
> unauthenticated read of arbitrary user PII (full name, email,
> phone, order history) by incrementing a numeric `orderId` URL
> parameter. The dataset accessed contains 200,000+ records based
> on `Content-Length` regression analysis. Bugcrowd VRT places PII
> exfiltration at P2 when not requiring authentication; this PoC
> demonstrates exactly that condition.

## Submission template

```markdown
# <Concise title — what + where>

**Asset:** <https://app.example.com>
**VRT:** Server Security Misconfiguration > OAuth Misconfiguration > Account Takeover
**Severity:** P1 (Critical)
**CVSS:** 9.6 — AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N
**Bounty range (per program tiers):** $5,000–$15,000

## Summary

(1–2 sentences. What is the bug; what's the impact.)

## Why this is <P-rating>

(Paragraph mapping demonstrated impact to VRT severity definition.)

## Steps to reproduce

1. As a freshly-registered user A on https://app.example.com, capture
   the OAuth flow. Note `redirect_uri` value `${APP_REDIRECT}`.
2. Construct the malicious URL: ...
3. ...
4. Observe that user B's session cookie is sent to attacker-controlled
   domain (evidence: 03-impact.png; HAR: evidence/oauth-poc.har).

## Impact

(Concrete language: "An attacker can take over any user account by
sending the victim a single link.")

## Remediation

(Specific to root cause; cite OWASP / NIST / vendor docs.)

## Evidence

- evidence/01-unauth.png
- evidence/02-attack-trigger.png
- evidence/03-impact.png
- evidence/oauth-poc.har (redacted; Authorization + Cookie scrubbed)

## Additional notes

(Disclosure restrictions, retest expectations, known caveats.)
```

## Bugcrowd-specific etiquette

- Use `@bcsec` mentions only when triager engages
- Do not paste raw HARs in chat — attach as files
- Retests: respond to the triager's "verify fix" within 7 days or
  the report archives
- Bugcrowd's "Submit for retest" workflow is the right channel for
  regressions — don't open new reports for variants

## See also

- `triage-validation` — pass before submission
- `evidence-hygiene` — Bugcrowd triagers reject reports with PII
- `report-writing` — generic platform-agnostic template
