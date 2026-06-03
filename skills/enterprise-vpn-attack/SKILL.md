---
name: enterprise-vpn-attack
description: External pre-auth attacks against VPN/SSL-VPN appliances — Cisco ASA/Firepower, Fortinet, Citrix, Palo Alto, Pulse, SonicWall, F5.
keywords: [vpn, ssl vpn, fortinet, fortigate, citrix, netscaler, gateway, cisco, asa, anyconnect, palo alto, globalprotect, pulse, ivanti, sonicwall, f5, big-ip, ssl-vpn]
---

# enterprise-vpn-attack

## When this skill loads

Triggers: "vpn", "ssl-vpn", "fortinet", "fortigate", "fortios",
"citrix", "netscaler", "anyconnect", "globalprotect", "pulse",
"ivanti", "sonicwall", "big-ip", "f5".

## Phase 1 — fingerprint the appliance

Distinct landing pages and headers:

| Appliance | Signal |
|---|---|
| Cisco ASA / AnyConnect | `/+CSCOE+/logon.html`, `Server: ASA-SSLVPN`, favicon hash `1278322865` |
| Cisco Firepower | `/admin/login.html`, `X-Frame-Options: SAMEORIGIN` + cert CN includes `Firepower` |
| Fortinet FortiGate / FortiOS SSL-VPN | `/remote/login`, `/sslvpn`, response includes `name=fgt_lang` |
| Citrix NetScaler / Gateway / ADC | `/vpn/index.html`, `/logon/LogonPoint`, `Server: NetScaler` |
| Palo Alto GlobalProtect | `/global-protect/login.esp`, `/sslmgr`, `Set-Cookie: PHPSESSID` + custom favicon |
| Pulse / Ivanti Connect Secure | `/dana-na/auth/url_default/welcome.cgi`, `Server: Pulse Secure` |
| SonicWall SMA / NetExtender | `/cgi-bin/welcome`, `/__api__/v1/`, response `SonicWall` in HTML |
| F5 BIG-IP APM | `/my.policy`, `Server: BigIP`, `Set-Cookie: BIGipServer` |

Use `httpx -title -tech-detect -favicon -hash mmh3` for batch.

## Phase 2 — version disclosure

| Appliance | Path |
|---|---|
| Fortinet | `/error_page/AdminWelcomeMessage.html` (older), build hash in JS |
| Citrix | `/vpn/js/rdx/core/lang/en.js`, version in comment |
| Palo Alto | `/global-protect/portal/css/login.css?v=<ver>` |
| Pulse | `/dana-na/auth/welcome.cgi?p=user`, build in HTML |
| BIG-IP | `/tmui/login.jsp` (build in HTML), iControl REST `/mgmt/tm/sys/version` |
| Cisco ASA | banner in OPTIONS response or `Server` |

`refresh-cve-index.py --vendor <vendor>` keeps the table below
synced; the static snapshot is below.

## Phase 3 — curated pre-auth CVE matrix

(48 entries; refresh with `scripts/refresh-cve-index.py`)

| CVE | Year | Vendor | CVSS | Auth | Type | Notes |
|---|---|---|---|---|---|---|
| CVE-2018-13379 | 2018 | Fortinet FortiOS | 9.8 | None | Path traversal → cred file read | Still in use |
| CVE-2019-11510 | 2019 | Pulse Connect Secure | 10.0 | None | Arbitrary file read → creds | Famously weaponized |
| CVE-2019-11539 | 2019 | Pulse Connect Secure | 7.2 | Auth | Cmd injection in admin | post-auth |
| CVE-2019-1579 | 2019 | Palo Alto GlobalProtect | 8.1 | None | Format-string → RCE | |
| CVE-2019-19781 | 2019 | Citrix NetScaler / Gateway | 9.8 | None | Path traversal → RCE | "Shitrix" |
| CVE-2020-2021 | 2020 | Palo Alto PAN-OS | 10.0 | None | Auth bypass when SAML config | |
| CVE-2020-3580 | 2020 | Cisco ASA / FTD | 6.1 | None | XSS pre-auth in WebVPN | |
| CVE-2020-5902 | 2020 | F5 BIG-IP TMUI | 9.8 | None | Path traversal → RCE | |
| CVE-2021-22893 | 2021 | Pulse Connect Secure | 10.0 | None | Buffer-overflow → RCE | |
| CVE-2021-22941 | 2021 | Citrix ShareFile / Gateway | 9.8 | None | Path traversal | |
| CVE-2021-26855 | 2021 | (Exchange — see m365 skill) | | | | |
| CVE-2021-40539 | 2021 | ManageEngine ADSelfService | 9.8 | None | Auth bypass + RCE | (ADSSP often perimeter) |
| CVE-2022-1388 | 2022 | F5 BIG-IP iControl REST | 9.8 | None | Auth bypass | |
| CVE-2022-22954 | 2022 | VMware Workspace ONE Access | 9.8 | None | SSTI → RCE | |
| CVE-2022-22972 | 2022 | VMware vRA / Identity Mgr | 9.8 | None | Auth bypass | |
| CVE-2022-26134 | 2022 | Atlassian Confluence | 9.8 | None | OGNL RCE | (perimeter Confluence) |
| CVE-2022-27510 | 2022 | Citrix Gateway | 9.8 | None | Auth bypass on SAML | |
| CVE-2022-29464 | 2022 | WSO2 Identity Server | 9.8 | None | Arbitrary file upload | |
| CVE-2022-30190 | 2022 | Microsoft Support Diag (Follina) | 7.8 | None | RCE via ms-msdt | |
| CVE-2022-40684 | 2022 | Fortinet FortiOS/FGT/FAZ | 9.8 | None | Auth bypass admin via crafted HTTP req | |
| CVE-2022-41328 | 2022 | Fortinet FortiOS | 6.5 | Admin | Path traversal — used by Volt Typhoon | |
| CVE-2023-2868 | 2023 | Barracuda ESG | 9.8 | None | Cmd injection in attachment | |
| CVE-2023-20269 | 2023 | Cisco ASA / FTD | 9.1 | None | Unauthorized VPN access | Akira ransomware |
| CVE-2023-27997 | 2023 | Fortinet FortiOS SSL-VPN | 9.8 | None | Heap overflow → RCE | "XORtigate" |
| CVE-2023-3519 | 2023 | Citrix NetScaler | 9.8 | None | Stack overflow → RCE | "Citrix Bleed 1" |
| CVE-2023-4966 | 2023 | Citrix NetScaler Gateway | 9.4 | None | Buffer over-read → session theft | "Citrix Bleed" |
| CVE-2023-46805 | 2023 | Ivanti Connect Secure | 8.2 | None | Auth bypass in admin web | chained w/ 21887 |
| CVE-2024-21887 | 2024 | Ivanti Connect Secure | 9.1 | Auth (chained from 46805) | Cmd injection | full pre-auth RCE chain |
| CVE-2024-21893 | 2024 | Ivanti Connect Secure | 8.2 | None | SSRF in SAML | |
| CVE-2024-22024 | 2024 | Ivanti Connect Secure | 8.3 | None | XXE in SAML | |
| CVE-2024-3400 | 2024 | Palo Alto PAN-OS GlobalProtect | 10.0 | None | Cmd injection in GP feature | exploited pre-disclosure |
| CVE-2024-23108 / 23109 | 2024 | Fortinet FortiSIEM | 9.8 | None | Cmd injection | |
| CVE-2024-21762 | 2024 | Fortinet FortiOS SSL-VPN | 9.6 | None | Out-of-bounds write → RCE | |
| CVE-2024-47574 | 2024 | Fortinet FortiClient EMS | 9.8 | None | SQLi → RCE | |
| CVE-2024-24919 | 2024 | Check Point Quantum Gateway | 8.6 | None | Arbitrary file read on Remote Access | |
| CVE-2024-7593 | 2024 | Ivanti Virtual Traffic Manager | 9.8 | None | Auth bypass admin panel | |
| CVE-2024-8190 | 2024 | Ivanti Cloud Services Appliance | 7.2 | Auth | OS cmd injection — chained from 0708 | |
| CVE-2024-8963 | 2024 | Ivanti CSA | 9.4 | None | Path traversal admin | |
| CVE-2024-29973 | 2024 | Zyxel NAS | 9.8 | None | Pre-auth RCE | |
| CVE-2025-0282 | 2025 | Ivanti Connect Secure | 9.0 | None | Stack overflow pre-auth | |
| CVE-2025-0283 | 2025 | Ivanti Connect Secure | 7.0 | Auth | priv esc | |
| CVE-2025-22457 | 2025 | Ivanti Connect Secure | 9.0 | None | Stack overflow → RCE | active in the wild |
| CVE-2025-23006 | 2025 | SonicWall SMA1000 | 9.8 | None | Deserialization → RCE | |
| CVE-2025-0108 | 2025 | Palo Alto PAN-OS | 7.8 | None | Auth bypass mgmt UI | |
| CVE-2025-31324 | 2025 | SAP NetWeaver Visual Composer | 10.0 | None | Unrestricted file upload → RCE | |
| CVE-2024-55591 | 2024 | Fortinet FortiOS/FortiProxy | 9.6 | None | Auth bypass via Node.js websocket | |
| CVE-2025-7775 | 2025 | Citrix NetScaler | 9.2 | None | Memory disclosure → session theft | "Citrix Bleed 2" |
| CVE-2024-13159 | 2024 | Ivanti EPM | 9.8 | None | Path traversal credential leak | |

## Phase 4 — chain templates

| Chain | Components |
|---|---|
| Fortinet ATO chain | CVE-2018-13379 file read → cleartext creds → VPN login → AD recon |
| Citrix Bleed chain | CVE-2023-4966 over-read → session cookie → ICA file → internal RDP |
| Ivanti CS double | CVE-2023-46805 auth-bypass → CVE-2024-21887 cmd-inject → root |
| Palo Alto GP | CVE-2024-3400 → cmd inject → cron persistence |
| F5 iControl | CVE-2022-1388 → `/mgmt/tm/util/bash` → root |

## Phase 5 — discipline

- Pre-auth RCE on a VPN appliance is **never** a "try and see" — always
  confirm version pin before any payload.
- Many of these CVEs have been used by ransomware crews; abuse here
  generates immediate IR. For bug-bounty work, only safe-mode probes
  (version disclosure + non-destructive PoC) until you have explicit
  go-ahead.
- For red-team, the chain templates above are the playbook; for
  bug-bounty, focus on demonstrating impact via a benign read
  (e.g., reading the appliance's banner or config index file).

## See also

- `m365-entra-attack` — VPN-fronting Okta/Entra
- `scripts/refresh-cve-index.py` — refresh this table
- `triage-validation` — Q1 evidence for VPN findings is the version
  fingerprint + the pre-auth response delta
