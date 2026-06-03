---
name: redteam-mindset
description: Operator discipline for red-team engagements — chain to objective, credential reuse, evidence trails, never stop at first vuln.
keywords: [redteam, red team, operator, mindset, opsec, persistence, lateral, objective, kill chain]
---

# redteam-mindset

## When this skill loads

Auto-loads when `mode=redteam` is passed to `/surface`, `/autopilot`,
or `/hunt`. Also loads on `/pickup` if engagement type is redteam.

## Core posture

Red-team is goal-driven, not vuln-driven. The bug-bounty mindset
("ship one impactful finding then move on") is wrong here. The
engagement scope typically defines an **objective**:

- "Compromise the corporate domain"
- "Exfiltrate a specific tagged file from finance"
- "Demonstrate access to the production database"
- "Achieve domain admin on the AD forest"

CBH's job: keep advancing toward the objective without scope-jumping.

## The 10 operator rules

1. **Never stop at first vuln** if the engagement objective is not
   yet reached. A reflected XSS is a step, not a destination.

2. **Always check credential reuse**. A leaked dev credential should
   be tested against every discovered service (VPN, M365, GitHub,
   Jira, Confluence, Okta, internal SSO) and against the public
   bounty-platform-style "have I been pwned" + commercial breach
   data.

3. **Document every HTTP request**. Client deliverables need
   reproducible evidence. Save all Burp project files in
   `engagement/evidence/burp/` and HARs in `evidence/har/`.

4. **Map blast radius before exploiting.** A confirmed primitive is
   more valuable than a one-shot RCE. Identify all places the
   primitive could be exercised.

5. **Don't trip prevention controls.** Test small first. If an EDR
   alert fires, the engagement's stealth model is broken — note it
   and adjust.

6. **Watch for IR re-touching your finding.** Load
   `mid-engagement-ir-detection`. If the blue team patches your
   beachhead mid-engagement, that's a positive signal — measure
   their dwell time and add to the deliverable.

7. **Persistence is a deliverable, not a side effect.** When the
   SOW allows persistence, lay it deliberately and document
   exhaustively. When the SOW forbids it, never plant any.

8. **Pivot only into scope.** A misconfigured VPN that leads to an
   internal IP outside the SOW boundary is **out**. Stop, document,
   ask client for expansion.

9. **Avoid destructive actions even when you "could".** Demonstrate
   write access by setting a benign file (`README-pentest-${date}`)
   in a sandbox path, not by replacing production files.

10. **Preserve attribution.** The client report should be
    publishable internally. Don't leak your own infrastructure
    (don't use shared C2 IPs that other ops have burned).

## Engagement-specific mode flags

| Flag in `scope.md` | Effect on CBH |
|---|---|
| `objective: domain-compromise` | Prioritize AD/Entra/Okta over web bugs |
| `objective: data-exfil` | Prioritize file-share, S3, DB endpoints |
| `objective: vpn-perimeter` | Auto-load `enterprise-vpn-attack` first |
| `stealth: high` | Disable nuclei in `/recon`; passive sources only |
| `stealth: low` | Allow full active scanning |
| `persistence: allowed` | Surface persistence options post-RCE |
| `persistence: forbidden` | Refuse to suggest persistence patterns |

## Credential reuse playbook

Whenever a credential leaks (recon, /token-scan, social engineering):

```
for service in [
  "Okta tenant SSO",
  "M365 / OWA (autodiscover.example.com)",
  "Citrix Gateway / NetScaler",
  "GlobalProtect / SonicWall / Fortinet VPN",
  "Cisco AnyConnect",
  "GitHub / GitLab / Bitbucket (corporate)",
  "Jira / Confluence (Atlassian Cloud + self-hosted)",
  "Jenkins / TeamCity / Bamboo",
  "Internal Wiki (DokuWiki, MediaWiki, Notion)",
  "AWS Console (via SSO)",
  "GCP Console (via SSO)",
  "Slack (corp workspace)",
  "Zoom (corp tenant)",
  "Dropbox / OneDrive corporate",
  "Salesforce",
  "ServiceNow",
  "SAP Fiori",
  "Cisco DUO admin (lol)",
]:
    test_credential(cred, service, rate=slow, log=true)
```

Always rate-limit: 1 attempt per service per 30s avoids triggering
generic auth-rate-limit alerts.

## Evidence trail format

```
engagements/<client>-redteam-<date>/
├── timeline.md         # one line per action, RFC3339 timestamps
├── chains.md           # each chain's diagram + IP + command + result
├── compromised/        # one file per compromised asset
├── evidence/
│   ├── burp/           # Burp project files
│   ├── har/            # exported HARs
│   ├── screenshots/    # numbered + captioned
│   ├── shells/         # any tunneled session captures (mode 0600)
│   └── cleanup.md      # what to undo at end of engagement
└── client-deliverable.docx  # final report (loaded from redteam-report-template)
```

## See also

- `mid-engagement-ir-detection`
- `enterprise-vpn-attack`, `m365-entra-attack`, `okta-attack`
- `redteam-report-template`
- `scope-discipline` — still hard, even in red-team
