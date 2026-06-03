---
name: exchange-attack
description: On-prem Exchange — ProxyLogon, ProxyShell, ProxyNotShell, autodiscover, basic-auth survival.
keywords: [exchange, owa, autodiscover, proxylogon, proxyshell, proxynotshell, ews, mapi, push notification]
---

# exchange-attack

## Triggers

"exchange", "owa", "autodiscover", "proxylogon", "proxyshell", "ews".

## Phase 1 — fingerprint

```
/owa/                            (OWA login)
/owa/auth/logon.aspx
/ecp/                            (Exchange Control Panel)
/Autodiscover/Autodiscover.xml
/mapi/                           (MAPI over HTTP — Outlook desktop)
/EWS/Exchange.asmx               (Exchange Web Services)
/PowerShell/                     (Remote PowerShell — high-risk)
/X-OWA-Version header           (sometimes leaks version)
```

OWA/ECP version in HTML `OwaPage` JS file's path
(`/owa/auth/15.2.1118/...`).

## Phase 2 — pre-auth CVE matrix

| CVE | Year | Chain name |
|---|---|---|
| CVE-2021-26855 | 2021 | ProxyLogon — SSRF via `X-AnonResource-Backend` cookie |
| CVE-2021-26857 | 2021 | Insecure deser in Unified Messaging — RCE post-26855 |
| CVE-2021-27065 | 2021 | Arbitrary file write post-26855 |
| CVE-2021-34473 | 2021 | ProxyShell — path confusion (`/autodiscover/autodiscover.json@x/...`) |
| CVE-2021-34523 | 2021 | ProxyShell — `Email` parameter privilege escalation |
| CVE-2021-31207 | 2021 | ProxyShell — arbitrary file write |
| CVE-2022-41040 | 2022 | ProxyNotShell — SSRF (cousin of 26855) |
| CVE-2022-41082 | 2022 | ProxyNotShell — RCE post-41040 |
| CVE-2023-21709 | 2023 | Privilege escalation via password spray amplifier |
| CVE-2023-23397 | 2023 | Outlook calendar invite leaks NTLM hash (client-side) |
| CVE-2024-21413 (MonikerLink) | 2024 | Outlook NTLM via link |
| CVE-2024-49040 / 49019 | 2024 | Multiple post-auth RCEs |

## Phase 3 — basic-auth survival

By default Microsoft disabled basic auth on Exchange Online in
2022-2023 but on-prem Exchange and some hybrid M365 tenants still
allow it on specific protocols (Autodiscover, EWS, ActiveSync, OAB).

Spray test (carefully):

```bash
# only after explicit RoE
curl -s -u user@example.com:Password1 \
  https://owa.example.com/EWS/Exchange.asmx
```

Basic-auth bypasses MFA on Exchange — which is why MS killed it.

## Phase 4 — autodiscover misuse

`Autodiscover.xml` is queried by Outlook with full creds in Basic
auth. Open redirects in autodiscover responses, untrusted certs
accepted by Outlook, etc.

Famous: 2021 "autodiscover.com" leak — Outlook fell back to
`autodiscover.<TLD>` if local autodiscover unreachable; researcher
registered domains and harvested creds.

## Phase 5 — chain templates

| Chain | Components |
|---|---|
| ProxyLogon classic | 26855 SSRF → mailbox impersonation → 27065 file write → web shell |
| ProxyShell classic | 34473 path confusion → 34523 backend privesc → 31207 file write → web shell |
| ProxyNotShell | 41040 SSRF → 41082 PowerShell remoting |

## See also

- `m365-entra-attack` — cloud Exchange + hybrid
- `hunt-deserialization` — UM RCE step
- `hunt-path-traversal` — file write step
