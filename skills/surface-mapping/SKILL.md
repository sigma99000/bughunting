---
name: surface-mapping
description: Convert raw recon output into a scope-pinned asset inventory with risk-prioritized hit list.
keywords: [surface, asset inventory, attack surface, prioritization, mapping]
---

# surface-mapping

## When this skill loads

Between `/recon` and `/hunt`. Consumes `recon-notes.md` and produces
a ranked, scope-filtered surface.

## What it produces

A `recon-notes.md` update with a new section:

```markdown
## attack surface (ranked)

| # | Asset | Stack | Reasons to look here | Suggested hunt |
|---|-------|-------|-----------------------|----------------|
| 1 | api.example.com | Spring Boot 2.6 + Okta SSO | Spring4Shell-vuln range; Okta IdP-init enabled | hunt-ssti, hunt-oauth |
| 2 | legacy.example.com | Apache 2.4.49 | CVE-2021-41773 vuln band | hunt-path-traversal |
| 3 | files.example.com | NGINX + nginx-ingress | nginx-ingress CVE-2025-1974 candidate | hunt-rce |
| 4 | admin.example.com | Citrix StoreFront | CVE-2023-4966 (Citrix Bleed) range | enterprise-vpn-attack |
| 5 | sso.example.com | Okta tenant | IdP-init review | okta-attack |
| ... | | | | |
```

## Ranking heuristic

Score each asset by:

1. **Pre-auth CVE candidates** (weight 5)
2. **Exposed admin / debug interfaces** (weight 4)
3. **Auth/SSO endpoints** (weight 4)
4. **Custom code (vs vendor product)** (weight 3) — more bugs per
   line in greenfield code
5. **JS bundle secret findings** (weight 3)
6. **Subdomain takeover candidates** (weight 5 — high-leverage)
7. **Cloud bucket exposure** (weight 4)

Rank by total score; sort descending.

## Out-of-scope filter

Cross-reference every discovered asset with `scope.md`. Drop
out-of-scope assets. **Never** rank them; never mention them in
the hit list — that's an audit-trail hazard.

## Subdomain takeover candidate list

Specifically scan recon output for these CNAME targets (orphaned
SaaS subdomains):

| Provider | Indicator |
|---|---|
| GitHub Pages | CNAME to `<user>.github.io` + 404 page |
| AWS S3 | CNAME to `<bucket>.s3.amazonaws.com` + NoSuchBucket |
| Azure Web Apps | CNAME to `<name>.azurewebsites.net` + 404 |
| Heroku | CNAME to `<app>.herokuapp.com` + "No such app" |
| Shopify | CNAME to `shops.myshopify.com` + "Sorry, this shop is currently unavailable" |
| Fastly | CNAME to Fastly + "Fastly error: unknown domain" |
| Netlify | CNAME to `<site>.netlify.app` + 404 |
| Tilda / Webflow / etc | Various |

Tools: `subjack`, `subzy`, `nuclei -t takeovers/`.

## Output to `/hunt`

When done, append to `recon-notes.md`:

```markdown
## suggested hunt invocations
/hunt target=api.example.com class=ssti
/hunt target=api.example.com class=oauth
/hunt target=legacy.example.com class=path-traversal
/hunt target=admin.example.com class=enterprise-vpn   (loads enterprise-vpn-attack)
```

## See also

- `recon-stack` — raw recon
- `offensive-osint` — strategy
- `intel` command — consumes this output
