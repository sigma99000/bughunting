---
name: intel
description: Fingerprint the stack → emit a CVE & misconfig matrix tailored to the discovered versions.
---

# /intel

**Args:** `target=<host>`

## What this command does

1. Reads `recon-notes.md` to identify the tech stack.
2. Loads `enterprise-vpn-attack`, `m365-entra-attack`, `okta-attack`,
   `sharepoint-attack`, `vcenter-attack`, `exchange-attack` selectively
   based on detected fingerprints.
3. For each detected component, emits:
   - **Version range** (best guess from `Server`, `X-Powered-By`,
     hash of static assets, error fingerprints)
   - **Known CVEs** that match the range, with public PoC links
   - **Misconfig classes** that don't have a CVE but are commonly
     exploitable for that component
4. Cross-references with the engagement's `scope.md` accepted-impact
   list — CVEs whose only impact is "DoS" are deprioritized for bug
   bounty engagements that exclude DoS.

## Example output

```
Target: app.example.com
Stack signals:
  Server: nginx/1.18.0 (Ubuntu)
  X-Powered-By: Spring Boot 2.6.7
  Auth: Okta (login.example.okta.com observed)
  Frontend: React 17

CVE matrix:
| Component       | CVE           | Severity | PoC          | Suggested skill   |
|-----------------|---------------|----------|--------------|-------------------|
| Spring Cloud    | CVE-2022-22963| 9.8      | github.com/x | hunt-ssti, hunt-rce|
| nginx merge_slashes off (config) | -- | High | PortSwigger  | hunt-smuggling     |
| Okta IdP-init   | CVE-2022-24788| 5.4      | Okta KB      | okta-attack        |

Misconfig classes to test:
- Spring Boot Actuator /actuator/env, /heapdump exposure
- React DevTools enabled in prod (look for __REACT_DEVTOOLS_GLOBAL_HOOK__)
- Okta tenant enumeration via well-known config

Suggested next:
/hunt target=app.example.com class=ssti
/hunt target=app.example.com class=oauth
```

## Discipline

- Never claim a CVE without a version match. If unsure, mark
  "candidate — needs version confirmation".
- Don't suggest active exploitation here; this command's job is
  prioritization, not execution.
