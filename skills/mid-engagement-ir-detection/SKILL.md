---
name: mid-engagement-ir-detection
description: Detect blue-team / IR response mid-engagement by comparing baseline endpoint snapshots to live state.
keywords: [ir, incident response, blue team, detection, baseline, drift, patch, mitigation, monitoring]
---

# mid-engagement-ir-detection

## When this skill loads

Loaded by `redteam-mindset` and by `/autopilot mode=redteam`. Runs
as a background poll (operator-confirmed cadence; default 30 minutes).

## What it does

Maintains a snapshot index in `engagement/evidence/baseline/` for
every endpoint that's been probed:

```
baseline/
├── 2026-01-15T10:00/
│   ├── https__app.example.com_login.json
│   ├── https__app.example.com_oauth_authorize_redirect_uri.json
│   └── ...
├── 2026-01-15T10:30/
│   └── ...
```

Each snapshot file contains:

```json
{
  "url": "https://app.example.com/oauth/authorize?redirect_uri=...",
  "captured_at": "2026-01-15T10:00:00Z",
  "method": "GET",
  "headers_sent": { ... redacted ... },
  "status": 302,
  "headers_received": { "location": "...", "set-cookie": "[REDACTED]" },
  "body_hash_sha256": "abc...",
  "body_size": 4096,
  "response_time_ms": 142
}
```

## Diff signals — what's blue-team activity vs noise

| Signal | Interpretation |
|---|---|
| `status` flip from 302 to 403 | likely block rule deployed |
| `body_hash` change + size unchanged | template patch (e.g., XSS payload now sanitized) |
| `set-cookie` includes new `cf-mitigated` or `__cfduid` value | CDN rule update |
| Time-to-first-byte regression >2x | rate-limit rule or analyze-first proxy added |
| New header `X-Detected-By` / `X-WAF` | new WAF in path |
| 404 where 200 was → endpoint pulled | hotfix removal |
| Inserted `Content-Security-Policy: ...` previously absent | hardening |
| Subdomain DNS now resolves differently | re-pointed to honeypot or DLP-routing |
| New TLS cert with `staging.<vendor>` SAN | mitigations rolled in via vendor |
| OAuth `redirect_uri` allow-list narrower than baseline | targeted fix |

Noise (don't flag):

- Cookie value rotation (per-request `csrf` token)
- `Date` header
- ETag drift on static assets
- Vary-by-host load balancer producing different upstream

## Confirmation workflow

When a candidate IR signal fires:

1. Re-probe with the same exact request (within 10s).
2. Re-probe from a different egress IP if available.
3. If signal persists → mark "PROBABLE IR ACTIVITY" in
   `timeline.md`.
4. **Do not retry the exact exploit chain** — assume the blue team
   is watching. Switch to passive observation.

## What to do with detected IR

- Add to client deliverable: "Mitigation deployed at T+45 minutes
  after initial probe. Mean time to mitigation: 22 minutes from
  first hit. Blue team responded to specific endpoint, not to broader
  class."
- This is valuable measurement data, not a setback. Many clients
  hire red teams specifically to time their blue team.

## Adversary-simulation alignment

If the engagement is aligned to a TTP framework (ATT&CK), the IR
detection skill maps signals to ATT&CK:

| Signal | ATT&CK ID (defender-side) |
|---|---|
| WAF rule deployment | M1037 (Filter Network Traffic) |
| Endpoint takedown | M1056 (Pre-compromise: Disable or Modify Cloud Logs reverse) |
| Cred rotation | M1027 (Password Policies) |

## Discipline

- Never adapt the *exploit* to bypass the *new* mitigation if the
  goal is to measure IR. The mitigation working *is* the deliverable.
- If the engagement objective requires beating the mitigation,
  log the IR event, ask the client whether to proceed, then proceed
  with their go-ahead in `timeline.md`.

## See also

- `redteam-mindset`
- `redteam-report-template` — IR section template
- `scope-discipline` — re-probing must stay in scope
