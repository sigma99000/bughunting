# Security Policy

## Reporting issues in Claude Bug Hunter itself

If you find a security issue in CBH (e.g., a script that performs
unintended actions, a payload that targets the wrong asset class, a
verification lab that opens a real port), email
**security@<your-org>.example** with:

- Affected file path
- Reproduction steps
- Proposed fix (if any)

We acknowledge within 72 hours and fix high-severity issues within 14 days.

## Out-of-scope for this policy

- Vulnerabilities in third-party tools listed in `recon-stack`
  (report upstream)
- Findings produced *using* CBH against external targets — those go to
  the target's bug-bounty program, not us
- AI-safety / prompt-injection concerns about Claude itself — report to
  Anthropic

## Responsible use

CBH is for **authorized** offensive security work. By using it you assert:

1. You have written authorization (bug bounty enrollment, pentest SOW,
   internal red-team charter) for every target you probe.
2. You will follow each program's scope, rate-limit, and disclosure
   policy.
3. You will not use CBH to maintain persistent access, exfiltrate user
   data, or affect availability beyond what's needed for proof of
   impact.

CBH actively refuses to emit payloads for hosts not present in
`scope.md`. The `scope-discipline` skill enforces this. Removing or
bypassing it is a misuse of the tool.

## Lab safety

Verification labs in `docs/verification/` are **intentionally
vulnerable**. Never expose them to the public internet. Run them only
on `127.0.0.1` or inside an isolated VM. The `docker-compose.yml` files
bind to `127.0.0.1` by default — do not change this.

## Threat model

CBH assumes:

- The operator is trusted (it's a tool for the operator, not a
  defensive control).
- Engagement folders may contain sensitive program data — never commit
  them to public Git.
- `secret_scan.py` and `token-scan` outputs may contain live API keys —
  treat the output directory as secret-bearing.

We ship a `.gitignore` that excludes `engagements/` from version control.
