# Open Redirect — Disclosed Pattern Survey (in chains)

35 disclosed reports. Open redirect alone is on every program's
never-submit list — these reports show how it *chains* to high impact.

## Chain frequency

| Chain end-state | Frequency |
|---|---|
| OAuth ATO (redirect_uri allow-list trusts app domain) | 47% |
| SAML credential phishing (RelayState reflection) | 12% |
| SSO logout flow → session fixation | 11% |
| Reflected file download / SmartScreen bypass | 8% |
| CSP-bypass via allowed-origin trust | 8% |
| OS auth dialog phishing (basic-auth prompt at attacker URL) | 6% |
| Open-redirect-on-redirect (SSRF allowlist bypass) | 5% |
| Other | 3% |

## Bypass-technique frequency

| Bypass | Frequency |
|---|---|
| Userinfo `@` injection | 28% |
| Double-slash `\\` / `/\` | 17% |
| Encoded slashes (`%2f`, `%5c`) | 16% |
| Path traversal in target | 12% |
| Fragment `#@` confusion | 9% |
| Unicode normalization tricks | 7% |
| Allow-list substring match | 6% |
| Other | 5% |

## See also

- `skills/hunt-redirect/SKILL.md`
- `skills/hunt-oauth/SKILL.md` — primary chain target
- `skills/hunt-saml/SKILL.md`
- `docs/disclosed-reports/chains.md`
