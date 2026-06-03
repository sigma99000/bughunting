# Engagement Log Format

Every authorized engagement gets one folder under `engagements/`. CBH
does **not** ship pre-populated engagements; this file documents the
format so `/pickup` and `/memory-gc` know what to read.

## Folder name convention

```
engagements/<primary-host>-<YYYY-MM-DD>/
```

Examples:

- `engagements/app.example.com-2026-01-15/`
- `engagements/corp.acme.com-redteam-2026-02-01/`

## Required files

### `scope.md`

```markdown
# Scope — <program/engagement name>

## Authorization
- Type: bug-bounty | pentest | redteam | research-disclosure
- Authority: <H1 program slug | SOW reference | charter doc>
- Window: <start date> – <end date>
- Operator: <handle>

## In scope
- *.example.com (any HTTP/S subdomain)
- mobile app: com.example.app (iOS/Android)
- public API: api.example.com

## Out of scope
- corp.example.com (internal)
- *.example-staging.com
- third-party SaaS (Zendesk, Stripe, etc.)

## Accepted impact (program-stated)
- Critical: RCE, ATO without user interaction, data exfil > 10k records
- High: ATO with 1 click, SQLi to data, SSRF to cloud metadata
- Medium: stored XSS in authenticated context, IDOR with PII
- Low: reflected XSS, CSRF on state-changing actions

## Never submit (program-stated or universal)
- Logout CSRF
- Self-XSS
- Missing security headers without demonstrated impact
- Banner grabbing / version disclosure alone
- EXIF metadata disclosure
- Rate-limit-only findings
- Clickjacking on non-state-changing pages

## Known issues (program-disclosed or own past submissions)
- (none yet)
```

### `recon-notes.md`

Free-form running log of:

- Subdomain enumeration output (deduplicated)
- Tech stack fingerprints per host
- Endpoints harvested from gau/waybackurls/katana
- Secrets found in JS bundles
- Interesting third-party integrations

### `chains.md`

One section per multi-vuln chain in progress:

```markdown
## chain-001: oauth-ato-via-takeover
Status: WIP | VALIDATED | KILLED
Components:
  1. Subdomain takeover on legacy-promo.example.com (CNAME → unclaimed Heroku)
  2. OAuth redirect_uri allow-list includes *.example.com
  3. Phishing-free PoC: victim clicks any example.com link logged in
Impact: P1 ATO
Next: build PoC HTML, capture HAR
```

### `findings/<id>.md`

One file per validated finding. ID format: `<class>-<short-slug>`.

```markdown
---
id: oauth-redirect-bypass-001
class: oauth
severity: critical
cvss: AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N
status: shipped
ship_date: 2026-01-18
platform: h1
report_url: https://hackerone.com/reports/XXXXX
---

# Finding: <title>

## Summary
## Steps to reproduce
## Impact
## Remediation
## Evidence
- evidence/oauth-ato-unauth.png
- evidence/oauth-ato-postlogin.png
- evidence/oauth-ato.har (redacted)
```

### `evidence/`

- HARs with `Authorization`, `Cookie`, `Set-Cookie` headers replaced by `[REDACTED]`
- Screenshots in sequence: `01-unauth.png`, `02-bypass.png`, `03-impact.png`
- All PII / API keys black-barred (see `evidence-hygiene` skill)

## Git hygiene

`.gitignore` in repo root excludes `engagements/`. **Never commit an
engagement folder to a public repo.** Use a private mirror or
filesystem encryption.

## Archival

After ship + program closure (typically 90 days post-disclosure), move:

```
engagements/<name>/ → archive/<year>/<name>.tar.gz.gpg
```

`/memory-gc` will prompt for this automatically.
