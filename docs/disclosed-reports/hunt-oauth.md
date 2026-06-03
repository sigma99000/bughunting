# OAuth — Disclosed Pattern Survey

Patterns from 41 disclosed reports.

## `redirect_uri` bypass — top 10 techniques

| Rank | Technique | Disclosed in |
|---|---|---|
| 1 | Userinfo `@` injection (`https://app.example.com@attacker.com`) | H1 #244696, #131202 |
| 2 | Fragment confusion (`...#@attacker.com/`) | H1 #665651 |
| 3 | Path traversal (`/cb/../../redirect/to/attacker`) | Multiple 2020–2022 |
| 4 | Backslash injection (`https://attacker.com\@app.example.com`) | Several SSO product CVEs |
| 5 | Subdomain takeover on `*.example.com` allow-list | H1 #1037436 |
| 6 | Open redirect on app's domain as redirect_uri | H1 #1062228 |
| 7 | Suffix match (`.example.com` matched `example.com.attacker.com`) | H1 #244##e (Slack) |
| 8 | Encoded slash (`/cb%2F@attacker.com`) | Multiple |
| 9 | Trailing-question-mark trick (`/cb?attacker.com`) | Auth0 / Okta variants |
| 10 | Userinfo with port (`https://example.com:80@attacker.com`) | Less common but observed |

## `state` parameter — disclosed CSRF patterns

| Pattern | Example |
|---|---|
| state omitted entirely | H1 #131202 (Uber) |
| state not session-bound | Auth0 misconfigs |
| state reused across requests | Multiple ride-share apps |
| state predictable (timestamp / userId) | Rare but observed |

## Authorization-code interception channels

| Channel | Disclosed reports |
|---|---|
| Referer header (open redirect → external page) | H1 #665651 |
| postMessage to attacker iframe | H1 #156288-adjacent |
| Open redirect on `redirect_uri` host | H1 #1062228 |
| Browser history + bfcache | Less reported but theorized |
| iframe + window.opener | Some social-login disclosures |

## Implicit / response_type abuse

| Pattern | Disclosed |
|---|---|
| `response_type=token` accepted on confidential client | Multiple SaaS pre-2020 |
| Hybrid `code id_token` accepted with id_token unverified | Auth0 (2018) |
| `none` response type with side-channel state leak | Less common |

## PKCE / id_token issues

| Issue | Source |
|---|---|
| PKCE optional on confidential client → bypass via downgrade | Various |
| `code_challenge_method=plain` accepted | Several SSO products |
| id_token `alg=none` accepted | jsonwebtoken-family CVEs |
| id_token signature not verified (only decoded) | Multiple early-2020 |
| `aud` claim accepted as superset | Microsoft "nOAuth" pattern (2023) |
| `email_verified` claim trusted blindly | Microsoft "nOAuth" pattern (2023) |

## Provider-specific quirks (disclosed)

| Provider | Quirk |
|---|---|
| Google | `hd=` domain-restriction not validated server-side |
| Apple | "Hide my email" relay confused with primary email |
| Facebook | `email` returned without `email_verified` |
| Microsoft | `tid=common` accepted from any tenant |
| Okta | `prompt=none` IdP-initiated CSRF |
| Auth0 | `connection` param swap to weaker IdP |

## Chain templates (disclosed)

- Open redirect + redirect_uri bypass → ATO (multiple, 2018–2023)
- Subdomain takeover + cookie-domain `.example.com` + login CSRF
  → ATO via cookie injection
- OAuth state CSRF + linking flow → account-linking takeover
- Old-version redirect URI accepted from Wayback + still valid →
  ATO via legacy endpoint

## See also

- `skills/hunt-oauth/SKILL.md`
- `skills/hunt-redirect/SKILL.md`
- `skills/m365-entra-attack/SKILL.md`
- `skills/okta-attack/SKILL.md`
