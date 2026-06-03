---
name: report
description: Render the finding into a platform-specific report template (H1, Bugcrowd, Intigriti, Immunefi, client DOCX).
---

# /report

**Args:** `finding=<id> platform=<h1|bc|intigriti|immunefi|client>`

## What this command does

1. Loads the platform-specific reporting skill:
   - `h1` → `h1-reporting`
   - `bc` → `bugcrowd-reporting`
   - `intigriti` → `intigriti-reporting`
   - `immunefi` → `immunefi-reporting`
   - `client` → `redteam-report-template`
2. Renders the finding's markdown into the platform template.
3. Runs evidence hygiene (loads `evidence-hygiene`):
   - Verifies HARs have no `Authorization` / `Cookie` / `Set-Cookie`
   - Verifies screenshots black-bar PII / API keys
   - Sequences screenshots: unauthenticated state first, then
     escalation
4. Writes the rendered report to
   `engagements/<...>/findings/<id>.report.<platform>.md` (or `.docx`
   for `client`).

## Output contract

```
✅ Report rendered: findings/<id>.report.h1.md
   Title:         <generated>
   Severity:      Critical (8.1)
   Word count:    432
   Evidence:      3 screenshots + 1 HAR (all redacted ✅)
   Submit-ready: yes

Preview:
---
# <title>
## Summary
...
```

## Discipline

- Reports never include the operator's own session cookies or
  bearer tokens, even in collapsed code blocks.
- Steps to reproduce must be **deterministic** — variable parameters
  go in `${PLACEHOLDER}` form, not real values, unless the value is
  the proof (e.g., a leaked secret).
- For `client` (red-team) reports, the executive summary precedes
  technical detail and is written for a non-technical reader.
