# DNS Recon

## Passive sources

| Source | Method |
|---|---|
| crt.sh | Certificate Transparency logs — `https://crt.sh/?q=%25.<domain>&output=json` |
| censys.io | Certs + service banners — paid API |
| shodan.io | Service banners with hostname pivot |
| dnsdumpster | passive DNS history (free) |
| securitytrails.com | passive DNS — paid |
| bevigil.com | mobile-app-extracted subdomains |
| chaos.projectdiscovery.io | rolling passive index — entitled |
| github.com/oxnr/awesome-bug-bounty | pivot for additional sources |

## Zone transfer

```bash
dig axfr <domain> @<ns>
```

Almost always denied externally. If accepted → instant full DNS dump.

## DNS misconfigs to look for

- Dangling CNAMEs → see `surface-mapping` subdomain-takeover table
- Public-facing internal-style names (`prod-db.example.com`)
- Wildcards that cover unexpected subdomains
- SPF includes pointing to deprecated services
- DMARC `p=none` (not a finding alone, but indicates posture)
- DNSSEC missing (rarely actionable but worth noting)

## Tooling

```bash
dnsx -l subs.txt -a -aaaa -cname -ns -resp -silent
puredns resolve subs.txt -r resolvers.txt
massdns -r resolvers.txt -t A subs.txt
```

Resolvers list: `https://github.com/janmasarik/resolvers`.
