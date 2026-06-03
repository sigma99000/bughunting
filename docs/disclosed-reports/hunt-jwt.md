# JWT — Disclosed Pattern Survey

22 disclosed reports + library-CVE corpus.

## Attack-class frequency

| Class | Frequency |
|---|---|
| `alg=none` accepted | 23% (pre-2018-heavy) |
| RS/HS confusion (HS256 forged with public key) | 18% |
| `kid` path-traversal / SQLi | 14% |
| `jku` allow-list bypass | 12% |
| Weak HS256 secret (dictionary cracked) | 11% |
| Embedded `jwk` header | 8% |
| Token reuse after logout | 7% |
| `aud` cross-service confusion | 7% |

## Reference CVEs / reports

| CVE / H1 | Pattern |
|---|---|
| CVE-2015-9235 | jsonwebtoken `alg=none` (defining bug) |
| CVE-2018-0114 | python-jose RS/HS confusion |
| CVE-2022-21449 (PsychicSignatures) | Java 15+ ECDSA-P256 — (0,0) signature accepted |
| CVE-2024-54150 | cjose null-pointer dereference / signature skip |
| H1 #738109 | Authelia `kid` path traversal to `/dev/null` |
| H1 #826358 | Auth0 JKU allowlist bypass via `@` userinfo |

## See also

- `skills/hunt-jwt/SKILL.md`
- `skills/hunt-oauth/SKILL.md`
