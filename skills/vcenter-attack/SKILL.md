---
name: vcenter-attack
description: VMware vCenter / ESXi attack — recent pre-auth RCE, log4shell-adjacent, vSphere API recon.
keywords: [vcenter, vsphere, esxi, vmware, dcerpc, vmsa, vmware advisory]
---

# vcenter-attack

## Triggers

"vcenter", "vsphere", "esxi", "vmware", "vmsa".

## Phase 1 — fingerprint

- `https://<host>/ui/` → vSphere Client login
- `https://<host>/sdk/` → SDK / SOAP API
- `https://<host>/mob/` → Managed Object Browser (often exposed)
- Banner: `Server: vmware-vCenter`, build number in HTML

## Phase 2 — pre-auth CVE matrix

| CVE | Year | Title |
|---|---|---|
| CVE-2021-21972 | 2021 | vSphere Client RCE via vCenter plugin |
| CVE-2021-21985 | 2021 | vSphere Client / vSAN plugin RCE |
| CVE-2021-22005 | 2021 | File upload pre-auth → RCE |
| CVE-2022-22954 | 2022 | Workspace ONE Access SSTI → RCE (adjacent) |
| CVE-2023-20887 | 2023 | Aria Operations RCE (vRealize) |
| CVE-2023-20892 | 2023 | vCenter SLP heap overflow |
| CVE-2024-37079 / 37080 | 2024 | DCERPC heap overflows → RCE |
| CVE-2024-22252 / 22253 | 2024 | ESXi USB driver use-after-free (local but powerful) |
| CVE-2024-38812 / 38813 | 2024 | vCenter heap overflow + priv esc |

## Phase 3 — DCERPC surface (port 2010, etc.)

Several pre-auth vCenter CVEs land on DCERPC ports (5443, 2010,
8089). External exposure is rare — vCenter usually firewalled —
but check via:

```bash
nmap -p 443,2010,5443,8089,902 <host>
```

## Phase 4 — once authenticated (low-priv API user)

```python
from pyVim.connect import SmartConnect
si = SmartConnect(host='vcenter', user='u', pwd='p', disableSslCertValidation=True)
# enumerate VMs, hosts, datastores
```

Pre-cred enumeration via SOAP:

```bash
curl -sk -X POST https://vcenter/sdk -H 'Content-Type: text/xml' \
  --data-binary @retrieve-service-content.xml
```

## Phase 5 — ESXi specific

If ESXi management interface exposed externally (it shouldn't be):

- `https://esxi/ui/` host client
- Pre-auth file disclosure CVEs (older)
- The 2023 ESXi ransomware wave (ESXiArgs) used CVE-2021-21974
  (OpenSLP heap overflow) for entry

## See also

- `enterprise-vpn-attack` — vCenter often sits behind VPN
- `hunt-deserialization` — Java deser in vCenter plugins
- `m365-entra-attack` — vCenter sometimes SAML-fed
