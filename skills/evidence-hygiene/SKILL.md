---
name: evidence-hygiene
description: Redact, sequence, and sanitize evidence (HAR, screenshots, video) before any report submission.
keywords: [evidence, redaction, har, screenshot, pii, cookie, token, sanitize, hygiene]
---

# evidence-hygiene

## When this skill loads

Auto-loads on `/report`. Also explicitly invoked during multi-stage
recon when secrets get captured (run `/token-scan` results through
hygiene before sharing).

## The hygiene checklist

### 1. HAR files

Replace these headers with `[REDACTED]`:

- `Authorization`
- `Cookie`, `Set-Cookie`
- `X-Auth-Token`, `X-API-Key`, `X-CSRF-Token`
- `Proxy-Authorization`
- Any header containing `bearer`, `token`, `secret`, `key`, `auth`
  case-insensitive

Replace these body fields:

- JSON keys matching `(?i)(password|secret|token|api_key|access_key|
  refresh_token|client_secret|private_key|ssn|sin|tax_id|credit_card|
  cvv|pan)` → `"[REDACTED]"`
- Form fields with the same names

Keep these intact (they're the evidence):

- The vulnerable parameter's value
- Status codes
- Response sizes
- Timings

### 2. Screenshots

| Element | Action |
|---|---|
| Operator's session cookies in DevTools panel | crop out or black-bar |
| Browser autofill (real email, phone) | black-bar |
| Other tabs (potential client leakage) | crop to single tab |
| URLs containing your own access token in fragment | black-bar fragment |
| Victim's PII (when proving cross-user IDOR with a *test* account, blank account fields are fine; if real PII appears, abort and re-do with a fresh test account) | abort + redo |

### 3. Sequence requirement

Every report with multi-step proof must include screenshots in this
**order**:

1. `01-unauthenticated.png` — baseline showing victim's normal state
2. `02-attack-trigger.png` — the moment the attack fires
3. `03-impact.png` — the resulting unauthorized state

This sequencing is the most common reason H1 reports are sent back
as "insufficient evidence". Bake it into the report rendering.

### 4. Video

Same rules as screenshots, plus:

- Strip audio if it was captured
- Watermark the operator's handle in a corner (proves authorship if
  the video leaks)
- Use `ffmpeg -vf "drawbox=color=black@1.0:t=fill"` for redaction
  overlays, not pixelation (pixelation can be reversed)

### 5. cURL commands

When pasting reproduction `curl` commands into the report:

- Replace your bearer with `${SESSION_TOKEN}` and add a note
  "obtained via login at /login"
- Replace any UUIDs that are your own with `${YOUR_USER_ID}` and
  victim's with `${VICTIM_USER_ID}` — instruct the triager how to
  obtain a second test account
- Keep the **exact** payload that demonstrates the bug

### 6. Secrets discovered via `/token-scan`

If you find a live Stripe key in a JS bundle:

- Do **not** include the full key in the report body.
- Last 4 chars + first 4 chars only: `sk_live_abcd...wxyz`
- Validation evidence: a single curl with redacted Authorization
  showing the key is valid (e.g., `200 OK` from
  `/v1/account` for Stripe)
- Move the full key to `evidence/secrets-<date>.txt` mode 0600 and
  reference the file by path

### 7. Server-side artifacts (red-team only)

If a red-team engagement produces server-side artifacts (web shell,
implant, log entries):

- Time-stamp every action so the client can correlate logs
- Catalog every file touched in `evidence/touched-paths.txt`
- Provide cleanup instructions in the final report

## Automation hooks

`/report` will refuse to render if:

- A HAR file in `evidence/` contains any of the redaction-target
  headers/keys (regex scan).
- A screenshot's OCR matches a credit-card or SSN pattern (where
  OCR is available).
- No "01-" / "02-" / "03-" sequence exists for multi-step findings.

## Discipline

- **Triage cost is real.** Sloppy evidence makes triagers downgrade
  or close as N/A.
- **Never share unredacted artifacts in chat with the program.**
  Triagers can lose API access for handling raw PII; help them.
- **Black-bar, never blur.** Blurred text has been reversed in
  research; opaque rectangles are safe.

## See also

- `triage-validation` — Q1 evidence needs to be hygienic
- `report-writing` — embeds the redacted artifacts
- `redteam-report-template` — adds artifact-handling appendix
