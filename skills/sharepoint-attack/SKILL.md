---
name: sharepoint-attack
description: SharePoint on-prem + Online attack — pre-auth RCE CVEs, ViewState abuse, SAML / OAuth integration quirks.
keywords: [sharepoint, spo, sharepoint online, owstimer, viewstate, soap, ssrs]
---

# sharepoint-attack

## Triggers

"sharepoint", "spo", "_layouts", "owstimer", "viewstate".

## Phase 1 — fingerprint

Paths: `/_layouts/15/`, `/_api/web/`, `/_vti_bin/`, `/_catalogs/`.

Version disclosure:
```
GET /_vti_pvt/service.cnf
GET /_layouts/15/AdminCenterRedirect.aspx
HEAD / — MicrosoftSharePointTeamServices header
```

## Phase 2 — pre-auth CVE matrix (curated)

| CVE | Year | Title |
|---|---|---|
| CVE-2019-0604 | 2019 | XML deser → RCE (China Chopper era) |
| CVE-2020-1147 | 2020 | XML deser variant |
| CVE-2020-16952 | 2020 | EditingPageParser RCE |
| CVE-2021-31181 | 2021 | InfoPath RCE |
| CVE-2022-29108 / 29109 | 2022 | Server-side RCE |
| CVE-2023-29357 | 2023 | Auth bypass via spoofed JWT — chains with 24955 for RCE |
| CVE-2023-24955 | 2023 | RCE via injected serialized code, paired with 29357 |
| CVE-2024-38094 / 38024 | 2024 | RCE in Server, multiple variants |
| CVE-2025-53770 / 53771 | 2025 | ToolShell — pre-auth RCE chain (deserialization + machineKey) |

## Phase 3 — ViewState abuse

If the application's `MachineKey` is leakable (via path traversal,
backup file disclosure), ViewState can be forged → RCE via
`ysoserial.net`:

```bash
ysoserial.net -p ViewState -g TypeConfuseDelegate \
  --validationkey=<key> --validationalg=SHA1 \
  -c 'cmd /c whoami > C:\Windows\Temp\poc.txt'
```

CVE-2025-53770 chained exactly this: leak the cryptographic
material, then forge ViewState.

## Phase 4 — common misconfigs

- Anonymous read on document libraries (`/sites/<site>/Forms/AllItems.aspx`)
- `client.svc` / `_api/web` over-permissive
- InfoPath forms with embedded VBA (`.xsn`)
- Search service exposing internal content

## Phase 5 — SharePoint Online quirks

- Tenant ID via `https://<tenant>.sharepoint.com/_api/site/getmetadata`
- Inheritance from Entra (see `m365-entra-attack`)
- Power Automate flows on lists — public-flow URLs

## See also

- `hunt-deserialization` — ViewState gadget
- `m365-entra-attack` — SPO auth front
- `exchange-attack` — companion on-prem service
