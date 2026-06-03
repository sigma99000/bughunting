---
name: hunt
description: Auto-load relevant hunt-* skills for the target and emit phase-by-phase attack checklists.
---

# /hunt

**Args:** `target=<host> [class=<vuln-class>] [endpoint=<url>]`

## What this command does

1. If `class=` is supplied, load `hunt-<class>` directly. Otherwise,
   choose based on:
   - `intel` output (stack-specific CVEs)
   - The endpoint corpus in `recon-notes.md` (e.g., `/graphql` →
     `hunt-graphql`; `/oauth/authorize` → `hunt-oauth`; file-upload
     forms → `hunt-file-upload`)
2. For each loaded `hunt-*` skill, emit the phase plan from its
   `SKILL.md` with the target URL substituted in.
3. Track payload attempts in `recon-notes.md` under
   `## hunt-<class>-<date>` so dupes don't re-run.

## Available classes

`xss sqli ssrf oauth saml idor auth rce xxe ssti csrf redirect jwt graphql race cache-poison smuggling deserialization path-traversal file-upload prototype-pollution cors csp-bypass lfi nosql ldap cmdi mass-assignment`

## Discipline

- Every payload must pass `scope-discipline` before being suggested.
- For destructive classes (`rce`, `cmdi`, `deserialization`), require
  the operator to confirm "I have authorization to attempt RCE on
  this host" before emitting weaponized payloads.
- Output format: one section per phase, payloads in code blocks
  tagged with the language, expected indicators after each.

## Output contract

```
Loaded: hunt-<class>
Target: <host>

Phase 1 — <name>:
  Test: <payload>
  Expect: <indicator>
  Disclosed ref: H1 #<id> or CVE-YYYY-NNNNN

Phase 2 — ...
```

When a phase produces a hit, ask the operator: `Send to /chain or
/validate?`
