---
name: payload-discipline
description: Payload safety — read-only first, no destruction, deconfliction, blast-radius awareness.
keywords: [payload, safety, opsec, read only, blast radius, deconfliction, destructive]
---

# payload-discipline

## When this skill loads

Loaded implicitly by `/hunt`, `/chain`, `/autopilot`. Also referenced
by every hunt-* skill that suggests an active payload.

## The 5 rules

### 1. Read before write
Always demonstrate impact with a **read** primitive (file read,
data query, version dump) before any write. Reads are reversible;
writes leave artifacts.

### 2. One PoC, never two
A single successful PoC is enough to prove impact. Don't "verify"
by repeating the payload — every additional request inflates the
target's blast radius.

### 3. Minimal blast radius
- File writes → unique path: `/tmp/pentest-<engagement>-<date>.txt`
- DB writes → `WHERE id = -1` (no actual record) when possible
- RCE → `id` or `whoami` only; never spawn shells in bug-bounty
- Multi-step chains → run end-to-end only after dry-run with print-
  only mode

### 4. Deconfliction
Tag every payload with operator handle + engagement ID:

```bash
curl -A "CBH/<handle>/<engagement-id> bug-bounty PoC" ...
```

Many programs deconflict against this tag — your traffic stays
distinguishable from real attacks during triage.

### 5. Never use real PII
- Test accounts only, both attacker and "victim" side.
- If a finding requires a real second account (no test-account
  feature), STOP and ask the program for guidance — most programs
  will provide a test pair.

## Refuse-list

CBH refuses to emit the following without explicit operator
confirmation per session:

| Payload class | Why |
|---|---|
| `rm -rf`, `del /F /S` | Destructive |
| `iptables -F`, `netsh advfirewall set` | Operational disruption |
| `shutdown`, `reboot`, `init 0` | DoS |
| `mysqldump --all` to attacker host | Bulk data exfil |
| Sliver / Mythic stagers | Persistence-class |
| Crypto miners | (...obvious) |
| Real outbound C2 binaries | Reusable backdoor |

The operator may explicitly enable a refuse-list item per
engagement by adding to `scope.md`:

```
## Explicitly permitted actions
- Bulk data exfil of `users` table to engagement evidence dir
  (red-team scope; authorized by SOW § 3.4)
```

## "Theoretical impact" rejection

If an operator asks "what would the payload to exfiltrate the
database look like?", CBH explains the *approach* (in prose) but
does not emit a copy-paste-ready exfil payload unless `scope.md`
explicitly permits.

## See also

- `scope-discipline`
- `redteam-mindset` (rule 9: avoid destructive actions)
- `triage-validation` — Q6 demands evidence, not theory
