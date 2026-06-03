---
name: offensive-osint
description: Recon + OSINT hub. 14 reference files cover dorks, secret patterns, validators, identity fabric, breach data, recon stack.
keywords: [osint, recon, reconnaissance, dorks, github dorks, google dorks, shodan, secrets, api keys, breach data, hibp, identity, enumeration]
---

# offensive-osint

## When this skill loads

Loaded by `/surface`, `/recon`, `/intel`, `/token-scan`. Always
loaded during the first phase of any external engagement.

## Reference index

This skill maintains 14 reference files under `references/`. Claude
loads them selectively based on the recon phase.

| File | What it contains |
|---|---|
| `dork-corpus.md` | 200+ Google / GitHub / Shodan dorks categorized by intent |
| `secret-patterns.md` | 80+ regex patterns for API keys with entropy thresholds |
| `secret-validators.md` | One-liner curl validators per key class |
| `identity-fabric.md` | Email → username → SaaS account enumeration across 30 platforms |
| `breach-and-credentials.md` | HIBP, dehashed.com, commercial sources, credential-stuffing hygiene |
| `recon-stack.md` | 40+ tools: subfinder, httpx, nuclei, gau, katana, etc. — install + usage |
| `dns-recon.md` | Passive DNS, certificate transparency, zone-transfer probing |
| `cloud-recon.md` | S3, GCS, Azure Blob enumeration; bucket name patterns |
| `mobile-app-recon.md` | APK / IPA decompilation, manifest secrets, deeplinks |
| `js-bundle-analysis.md` | sourcemap recovery, secret hunting, endpoint mining |
| `wayback-strategy.md` | gau / waybackurls / katana — diffing across time |
| `metadata-osint.md` | EXIF, document metadata, public author leakage |
| `physical-osint.md` | (advisory only — not actionable; reminds operators what's out of scope for external red-team) |
| `social-enumeration.md` | Public profile correlation, but with hard guardrails against harassment |

## Phase 1 — passive subdomain enumeration

See `references/recon-stack.md`. In order of yield:

1. `subfinder -all -recursive`
2. `assetfinder --subs-only`
3. `crt.sh` query
4. `amass enum -passive`
5. `chaos-client -d <domain>` (PTR-data, if entitled)

Dedupe, sort, save to `engagement/recon-notes.md`.

## Phase 2 — liveness + tech

```bash
httpx -l subs.txt -ports 80,443,8080,8443,8000,8888 \
      -tech-detect -title -status-code -ip -tls-probe -favicon -silent
```

Annotate with favicon hash (mmh3) — Shodan-correlate to known
appliances.

## Phase 3 — endpoint mining

```bash
gau --threads 10 example.com > endpoints.txt
waybackurls example.com >> endpoints.txt
katana -u https://example.com -d 3 -jc -fs fqdn >> endpoints.txt
sort -u endpoints.txt | grep -E '\\.js(\?|$)|/api/|/admin|/internal|/debug' > interesting.txt
```

## Phase 4 — secret hunting

For every JS bundle:

```bash
python scripts/secret_scan.py path=<bundle-url>
```

Loads `references/secret-patterns.md` and applies entropy filters.

For every public GitHub org/user related to the target:

```bash
gh search code --owner <org> "amazonaws.com"
gh search code --owner <org> "BEGIN RSA PRIVATE KEY"
gh search code --owner <org> "<custom-domain>"
```

See `references/dork-corpus.md` for the full corpus.

## Phase 5 — identity fabric

For every email found:

- Run through `references/identity-fabric.md` — does this email
  have accounts on Slack, GitHub, GitLab, Trello, Notion,
  Salesforce, etc?
- Cross-reference with breach data via HIBP (`references/breach-and-credentials.md`).

This builds the "spray surface" for any future credential testing —
but **never** use real victim creds without explicit engagement
authorization.

## Phase 6 — cloud asset enumeration

See `references/cloud-recon.md`. Common buckets:

```
<target>-prod
<target>-staging
<target>-backup
<target>-assets
backup.<target>.com → CNAME to S3
```

Tools: `cloud_enum`, `s3scanner`, `gobuster dns -w bucket-names.txt`.

## Discipline

- Passive sources only by default. Active probing must respect
  scope.md.
- Never publish dorks or recon output to a public channel without
  redaction.
- Identity-fabric data is **not** a license to social-engineer.
  Document the surface; act on it only within engagement scope.

## See also

- `recon-stack` — the tooling-only sibling skill
- `surface-mapping` — turn recon into a scope-pinned asset list
- `hunt-*` skills — where recon flows into validation
