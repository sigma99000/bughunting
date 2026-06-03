# SSRF — Disclosed Pattern Survey

Patterns from 56 disclosed reports.

## Entry vectors (frequency)

1. Image-fetch by URL (avatar, OG-preview) — 31%
2. Webhook destination URLs — 24%
3. "Import from URL" (RSS, document, project) — 18%
4. Server-side PDF / screenshot rendering — 11%
5. Markdown image fetching — 9%
6. XML/SOAP integration endpoints — 4%
7. Other — 3%

## Bypass techniques (frequency)

1. DNS rebinding (TTL=0 → resolves attacker, then internal) — 22%
2. Userinfo `@` injection — 18%
3. Decimal / hex / IPv6 encoding of internal IP — 14%
4. Open redirect chain (302 from allowlisted host) — 12%
5. Hostname allow-list bypass via subdomain prefix/suffix — 10%
6. `gopher://`, `dict://` protocol switching — 9%
7. CRLF injection in URL hostname — 7%
8. Other — 8%

## Top H1 reports

| H1 ID | Pattern |
|---|---|
| 341876 | Shopify — Image upload URL → GCP metadata → bucket takeover |
| 807310 | Atlassian Jira — Webhook URL → internal admin endpoints |
| 1062088 | HackerOne — Markdown OG-image preview SSRF |
| 1108591 | GitLab — Project import URL → SSRF → Redis cron RCE |
| 1037436 | HackerOne — IdP discovery → SSRF |
| 397376 | Internal AWS metadata via PDF render |
| 615888 | Mail.ru — DNS rebinding bypass of IP allow-list |
| 778231 | Drupal — Markdown converter SSRF |

## Cloud-metadata pivots (disclosed)

| Cloud | Endpoint used | Disclosed in |
|---|---|---|
| AWS IMDSv1 | `/latest/meta-data/iam/security-credentials/<role>` | CapitalOne 2019, multiple H1 |
| AWS IMDSv2 | requires PUT to token endpoint — found in SSRFs allowing method control | Rare but observed |
| GCP | `/computeMetadata/v1/instance/service-accounts/default/token` + Metadata-Flavor header | Shopify, others |
| Azure | `/metadata/identity/oauth2/token` + Metadata: true | Multiple Azure tenant disclosures |
| DigitalOcean | `/metadata/v1/user-data` | Common |
| Kubernetes svc | `/api/v1/namespaces/.../secrets/` from compromised pod | Multiple |

## Impact-escalation matrix (disclosed)

- Redis on 127.0.0.1 + SSRF + gopher → cron RCE (most common
  SSRF→RCE chain in disclosed corpus)
- IMDS → IAM creds → S3 dump (CapitalOne archetype)
- Internal Jenkins/GitLab SSRF → leaked build secrets → supply
  chain
- Internal admin UI without auth → state-change

## Blind/semi-blind impact

| Channel | Reports |
|---|---|
| DNS exfil (`{data}.collab.attacker.com`) | Common in latest reports |
| Port-scan via response timing | Older but still effective |
| HTTP status disambiguation (200 vs 403) | Common |
| Response-length disambiguation | Some |

## Patches commonly missed

The corpus shows three categories of incomplete-fix patterns:

1. **Resolve-then-fetch race**: SSRF defender resolves URL, validates
   IP, then re-fetches → between (1) and (3), DNS rebinds. Pattern
   present in 8 of the 56 reports.
2. **Allowlist by domain suffix without anchoring**: `endswith(".example.com")`
   matches `attacker.com.example.com.attacker.com` if the parser
   strips trailing dots.
3. **Redirect-follow without re-validation**: defender validates the
   initial URL, but `requests`-style libraries follow 302s without
   re-checking. Disclosed in multiple Python apps.

## See also

- `skills/hunt-ssrf/SKILL.md`
- `skills/hunt-xxe/SKILL.md` — SSRF via XXE entity
- `skills/hunt-redirect/SKILL.md` — redirect-chain bypass
- `skills/m365-entra-attack/SKILL.md` — Azure metadata specifics
