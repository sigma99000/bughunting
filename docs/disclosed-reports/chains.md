# Multi-Vuln Chain — Disclosed Pattern Survey

102 chains catalogued. Single-class bugs rarely meet "Critical" — the
chains in this file demonstrate the typical bridges from "Medium
finding" to "P1 impact".

## Top chain archetypes (frequency in corpus)

### 1. Open redirect → OAuth ATO  (18 chains)

```
Open redirect on app.example.com (e.g., /logout?return=)
    ↓
redirect_uri allow-list trusts *.example.com
    ↓
attacker page steals authorization code via referer/postMessage
    ↓
attacker exchanges code → victim session
```

### 2. Subdomain takeover → cookie/CORS trust  (12 chains)

```
Dangling CNAME on legacy-promo.example.com (orphan Heroku)
    ↓
Cookie scope `.example.com` shared
    ↓
Attacker sets victim cookie → session fixation / token theft
```

### 3. SSRF → cloud metadata → cloud takeover  (15 chains)

```
SSRF in image-fetch
    ↓
IMDSv1 or GCP/Azure metadata
    ↓
IAM creds for over-scoped role
    ↓
S3 / SecretsManager / KMS dump
```

### 4. Self-XSS → IDOR → stored XSS in victim context  (11 chains)

```
Stored XSS on attacker's own profile (visible only to attacker — KILL alone)
    ↓
IDOR allows setting victim's profile bio to attacker's value
    ↓
Victim's profile renders attacker payload → ATO via cookie theft
```

### 5. File upload (any) → handler enabling → RCE  (10 chains)

```
Upload .htaccess enabling .png as PHP handler
    ↓
Upload shell.png with PHP body
    ↓
Request shell.png → RCE
```

Variant: SVG upload + dangerous viewer → XSS → admin ATO.

### 6. SSTI → OAuth secret leak → ATO at scale  (8 chains)

```
SSTI in email template (Jinja2)
    ↓
Reads OAuth client_secret from config
    ↓
Forges id_tokens for any user
    ↓
ATO at platform scale
```

### 7. SAML XSW + assertion replay  (6 chains)

```
Capture valid SAML response
    ↓
XSW-3 modify NameID to "admin"
    ↓
SP accepts wrapped assertion → admin login
```

### 8. JWT confusion → privilege escalation  (8 chains)

```
JWT uses RS256, jwt.verify called with pub key as symmetric secret
    ↓
Attacker re-signs token with HS256 + pub key
    ↓
Modifies role claim to "admin"
    ↓
Service accepts forged token
```

### 9. Smuggling → cache poisoning → cross-user XSS  (5 chains)

```
TE.CL smuggling primitive
    ↓
Poison /important.js with attacker content (X-Forwarded-Host reflected)
    ↓
CDN caches poison
    ↓
All victim users get attacker JS → mass ATO
```

### 10. Race condition → double-spend / 2FA bypass  (9 chains)

```
Single-packet attack (HTTP/2)
    ↓
2FA OTP verify endpoint
    ↓
Parallel submission with invalid + valid codes
    ↓
Race window allows session promotion before counter increment
```

## Chains by impact tier

| Impact | Chains |
|---|---|
| RCE | 28 |
| ATO without UI | 19 |
| ATO with 1-click | 31 |
| Privilege escalation | 14 |
| Mass data exfil | 10 |

## Patterns that show up across multiple classes

- **Trust transitivity**: app trusts `*.example.com`, attacker
  controls one corner of that
- **Time-of-check vs time-of-use**: re-resolution gaps, cache
  invalidation gaps
- **Allow-list normalization**: `endswith()` without anchoring,
  case-sensitivity mismatches
- **Single source of truth violations**: same data validated
  client-side AND server-side, but with different rules

## See also

- `skills/hunt-oauth/SKILL.md`, `skills/hunt-ssrf/SKILL.md`,
  `skills/hunt-jwt/SKILL.md`, `skills/hunt-saml/SKILL.md`,
  `skills/hunt-smuggling/SKILL.md`, `skills/hunt-race/SKILL.md`
- `commands/chain.md`
