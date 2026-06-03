# SAML — Disclosed Pattern Survey

18 disclosed reports + foundational research.

## Pattern frequency

| Pattern | Frequency |
|---|---|
| XSW (XML signature wrapping) — XSW-1 to XSW-8 | 39% |
| NameID comment-truncation | 22% (the 2018 Duo + GitHub class) |
| Assertion replay (no `InResponseTo` binding) | 17% |
| Audience confusion (substring match) | 11% |
| Algorithm downgrade (`sha1`, RSA→HMAC) | 6% |
| XXE in SAML XML | 5% |

## Foundational refs

- Duo 2018 advisory: NameID comment-truncation across 4+ libraries
- GitHub 2018 disclosure: XSW + comment injection → ATO via SAML
- CVE-2017-11427 (ruby-saml): XSW XSW-1
- CVE-2024-45409 (Ruby OmniAuth-SAML): signature bypass via XSW
- CVE-2014-1456 (OpenSAML): XXE in metadata
- CVE-2022-29874 (Apache Pulsar): XXE in SAML

## See also

- `skills/hunt-saml/SKILL.md`
- `skills/hunt-xxe/SKILL.md`
- `skills/m365-entra-attack/SKILL.md`, `skills/okta-attack/SKILL.md`
