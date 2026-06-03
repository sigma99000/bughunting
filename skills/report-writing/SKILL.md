---
name: report-writing
description: Generic report-writing skill — title, summary, steps, impact, remediation. Loaded when no platform-specific skill applies.
keywords: [report, writing, finding, template, markdown]
---

# report-writing

## When this skill loads

`/report platform=client` for non-redteam single-finding writeups,
or when the platform doesn't match a more-specific skill.

## Section-by-section guidance

### Title
- One line, 8–12 words.
- Verb + asset + vector.
- Avoid: "Critical RCE found in the application!"
- Prefer: "Pre-auth RCE on portal.example.com via deserialized session cookie"

### Summary
- 2–3 sentences max.
- What is broken; how is it exploited; what impact follows.
- No "could allow", "may permit" — use "an attacker can".

### Steps to reproduce
- Numbered.
- Every variable in `${PLACEHOLDER}` form.
- Show prerequisites (test account credentials, attacker
  infrastructure, headers).
- End with the observable signal (HTTP response code + key bit of
  body).

### Impact
- One paragraph.
- Frame in business terms: data exfil, account takeover, lateral
  movement, financial loss.
- Note attacker effort required (zero-click, one-click, N-click).

### Remediation
- Specific, not generic.
- Cite the root cause, not the symptom.
- Reference the relevant standard / framework section
  (OWASP, NIST 800-53, RFC).

### Severity
- CVSS 3.1 vector with score.
- Justification paragraph for borderline ratings.

### Evidence
- Listed in viewing order (`01-...`, `02-...`, `03-...`).
- HAR / Burp project file referenced by filename + SHA-256.
- All sensitive content redacted (see `evidence-hygiene`).

## Tone

- Active voice ("an attacker can read", not "files can be read").
- Past tense for what you did ("I captured the request"),
  present for what the bug allows ("the endpoint accepts").
- No bravado, no apologies. Just facts and impact.

## Avoid

- "Critical!!" / "Urgent!!" — let the CVSS do the speaking.
- Long preamble about your testing methodology.
- Speculation ("This could likely be combined with...").
- Self-citation ("As I demonstrated in my last report...").

## Markdown skeleton

```markdown
# <title>

## Summary

<2-3 sentences>

## Steps to reproduce

1. ...
2. ...

## Impact

<one paragraph>

## Remediation

<specific>

## Severity

CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N — 9.8 (Critical)

## Evidence

- evidence/01-unauth.png
- evidence/02-trigger.png
- evidence/03-impact.png
- evidence/full.har (SHA-256: ...)
```

## See also

- `h1-reporting`, `bugcrowd-reporting`, `intigriti-reporting`,
  `immunefi-reporting`, `redteam-report-template`
- `evidence-hygiene`
- `triage-validation`
