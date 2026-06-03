---
name: token-scan
description: Scan a directory, Git repo, or remote JS bundle for hardcoded secrets using 80+ patterns.
---

# /token-scan

**Args:** `path=<dir-or-url-or-git-repo> [validate=true|false]`

## What this command does

1. Loads `offensive-osint/references/secret-patterns.md` (80+ regex
   patterns) and `offensive-osint/references/secret-validators.md`.
2. Invokes `scripts/secret_scan.py path=<...>`:
   - If path is a URL, downloads the file.
   - If path is `git@...` or `https://...git`, clones to `/tmp` and
     scans full history.
   - If path is a directory, walks files matching
     `*.js,*.ts,*.tsx,*.jsx,*.map,*.json,*.env,*.yml,*.yaml,*.config`.
3. For each candidate match, computes entropy and applies the
   pattern's threshold (e.g., AWS access keys require entropy ≥ 3.5).
4. If `validate=true`, runs the curl validator one-liner from
   `secret-validators.md` for each unique key.

## Output contract

```
Scanned: 247 files (3.2 MB)
Hits: 4 candidates

[STRIPE_SECRET_KEY] in dist/app.bundle.js:12378
  Value: sk_live_••••••••••••••••••••2x9q   (entropy 4.8)
  Validator: curl -u <key>: https://api.stripe.com/v1/charges?limit=1
  Validated: ✅ HTTP 200 — LIVE KEY

[AWS_ACCESS_KEY_ID] in dist/app.bundle.js:12380
  Value: AKIA••••••••••••J3PR
  Validator: aws sts get-caller-identity --no-sign-request → use creds
  Validated: ⚠️ requires AWS_SECRET_ACCESS_KEY also present

...
```

## Discipline

- **Live key handling:** if validation succeeds, do NOT print the
  full key. Print the masked form and write the full key to
  `evidence/secrets-<date>.txt` with mode 0600.
- Always note in the finding which Git commit / asset bundle URL
  the key came from — bounty triagers will ask.
- Stripe / Twilio / SendGrid keys: if validated, the report must
  state "validated read-only via single endpoint; no resources
  enumerated" to avoid abuse.
