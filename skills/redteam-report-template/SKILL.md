---
name: redteam-report-template
description: Client-facing red-team report — executive summary, technical narrative, remediation priority, evidence appendix.
keywords: [redteam, red team, client report, deliverable, exec summary, narrative, kill chain, attack path, docx]
---

# redteam-report-template

## When this skill loads

`/report platform=client`. Loaded after a red-team engagement closes.

## Report structure

```
1. Executive Summary             (2 pages — non-technical)
2. Engagement Overview           (scope, dates, rules of engagement)
3. Methodology                   (TTP frame: ATT&CK or kill-chain)
4. Attack Narrative              (chronological with timestamps)
5. Findings                      (one per primitive, with severity)
6. Remediation Priority Matrix   (effort × impact)
7. Detection Recommendations     (per finding, what would have caught it)
8. Engagement Hygiene Notes      (IR observations, cleanup, artifacts)
9. Appendix A — Evidence Index
   Appendix B — Indicator List (IPs, hashes, paths touched)
   Appendix C — Cleanup Log
```

## Section templates

### 1. Executive Summary

Audience: CISO, executive sponsor, board sub-committee. No jargon.

Required elements:

- **Headline result**: "The objective (compromise the domain) was
  achieved in 6 hours via an unpatched perimeter VPN appliance
  (CVE-XXXX-XXXX)."
- **Business impact**: "An adversary with the same access could
  have exfiltrated <data class>, modified <process>, and impersonated
  <persona>."
- **Mean time to detect (MTTD)**: "The blue team mitigated the
  initial beachhead 22 minutes after first probe."
- **Mean time to respond (MTTR)**: "Full containment took 4 hours."
- **Top 3 recommendations**, each in one sentence.

### 2. Engagement Overview

- Scope (in / out)
- Dates and operator hours
- Rules of engagement (authorized actions, blackout windows,
  destructive-action ban)
- Authorization chain (SOW reference, named approvers)

### 3. Methodology

If using ATT&CK, table each phase used to ATT&CK tactic + technique
IDs. Example:

| Phase | Tactic | Technique | TID | Observed in this engagement? |
|---|---|---|---|---|
| Recon | Reconnaissance | Gather Victim Network Info | T1590 | ✅ subdomain enum |
| Initial Access | Initial Access | Exploit Public-Facing Application | T1190 | ✅ Citrix Bleed |
| Privilege Escalation | PrivEsc | Valid Accounts: Domain Accounts | T1078.002 | ✅ session theft |
| Discovery | Discovery | Domain Trust Discovery | T1482 | ✅ via captured session |
| Collection | Collection | Data from Information Repositories | T1213 | ✅ Confluence dump |

### 4. Attack Narrative

Chronological, RFC3339 timestamps, one paragraph per step.

```
2026-01-15T09:14:22Z — Initial discovery of NetScaler at
gateway.example.com via CT log enumeration. Version banner from
/vpn/js/rdx/core/lang/en.js indicated NetScaler 13.1-49.15, vulnerable
to CVE-2023-4966 ("Citrix Bleed").

2026-01-15T09:33:08Z — Sent crafted HTTP request to /oauth/idp/login,
received memory disclosure including an active session cookie for
user `mfields@example.com` (Marketing Analyst, member of GG_Marketing).

2026-01-15T10:02:41Z — Mounted the session cookie in a browser,
landed in the corporate Citrix Storefront, launched the published
"Confluence" ICA application.

...
```

### 5. Findings

One sub-section per finding. Structure:

```
Finding RT-2026-01 — Citrix Bleed (CVE-2023-4966) on gateway.example.com

Severity: Critical
Likelihood of exploitation: High (active CVE, public exploit, weaponized in the wild)
Business impact: Foothold for AD-domain compromise

What we did:
  <2-3 sentence narrative>

Why it matters:
  <plain-language consequence>

Evidence:
  - artifacts/01-version-fingerprint.txt
  - artifacts/02-poc-request.har (redacted)
  - artifacts/03-session-recovered.png (token redacted)

Remediation:
  Citrix advisory CTX579459 — apply firmware 13.1-49.15 or later;
  rotate all NetScaler-issued session cookies post-upgrade.
```

### 6. Remediation Priority Matrix

| ID | Finding | Effort | Impact | Priority |
|---|---|---|---|---|
| RT-01 | Citrix Bleed unpatched | Low | Critical | P0 |
| RT-02 | Help-desk MFA reset SOP weak | Med | Critical | P0 |
| RT-03 | Excessive group memberships (GG_Marketing → finance share) | High | High | P1 |
| RT-04 | No alerting on Confluence bulk export | Med | Med | P1 |
| ... | ... | ... | ... | ... |

P0 = ship within 7 days; P1 = within 30; P2 = next quarter; P3 = backlog.

### 7. Detection Recommendations

For each finding, what telemetry would have caught it:

```
Finding RT-2026-01 (Citrix Bleed):
  - Sigma rule for unusual `/oauth/idp/login` POSTs with long
    response bodies (memory dump indicator)
  - Citrix ADM out-of-band session-cookie usage from non-matching
    egress IP
  - Splunk / Sentinel: correlate Citrix StoreFront login with
    unexpected User-Agent
```

### 8. Engagement Hygiene Notes

- IR signal observed at T+22 min — log, IP block deployed
- Files created on target: `evidence/cleanup.md` lists 4 paths to
  revert
- Implants deployed: NONE (per RoE)
- Persistence laid: NONE
- Operator C2 IPs (for hunt deconfliction): `198.51.100.7`,
  `198.51.100.8`

### 9. Appendix C — Cleanup Log

Every action that touched the target with a "revert?" column.
Example:

| Time | Host | Action | Reverted? |
|---|---|---|---|
| 09:14 | gateway.example.com | Sent HTTP probe (read-only) | n/a (read-only) |
| 10:33 | conf.example.com | Created Confluence page `pentest-marker-2026-01` | Yes (deleted 18:14) |
| 11:02 | fs01.example.com | Read \\fs01\finance\Q4-budget.xlsx | n/a (read-only) |

## DOCX rendering

The skill produces markdown by default. To render to DOCX:

```bash
pandoc engagement/findings/redteam-report.md \
  --reference-doc=assets/redteam-template.docx \
  -o engagement/redteam-deliverable.docx
```

(`assets/redteam-template.docx` is operator/firm-specific —
not shipped with CBH.)

## See also

- `redteam-mindset`
- `mid-engagement-ir-detection` — populates §8
- `evidence-hygiene` — appendix sanitization
