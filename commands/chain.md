---
name: chain
description: Compose multi-vuln chains to escalate single low-impact findings into reportable impact.
---

# /chain

**Args:** `finding=<id> [start-from=<finding-id>]`

## What this command does

1. Reads the finding(s) referenced.
2. Cross-loads relevant `hunt-*` skills.
3. Searches `recon-notes.md` for adjacent primitives (open redirects,
   takeovers, exposed admin paths, leaked secrets).
4. Proposes 1–3 chain templates that escalate the finding to an
   accepted impact (per `scope.md`).
5. Writes the chosen chain to `chains.md` under a new section.

## Common chain templates

| Components                                              | Reaches |
|---------------------------------------------------------|---------|
| Open redirect + OAuth redirect_uri allow-list + Postmessage leak | Account takeover (P1) |
| Subdomain takeover + cookie-domain `.example.com` + CSRF | Cookie injection → ATO |
| SSRF + cloud metadata + IAM role chained to S3          | Cloud takeover (Crit) |
| Stored self-XSS (own profile) + IDOR (set victim's profile) | Stored XSS in victim context |
| File upload (any) + path traversal + supported handler  | RCE |
| SAML XSW + assertion replay + role attribute            | Privilege escalation |
| HTTP smuggling + cached auth response + CDN poisoning   | Cross-user data exposure |

## Output contract

```
Chain candidate: <name>
Components:
  1. <finding-id-or-primitive> → <effect>
  2. ...
Reaches: <accepted-impact label>
Confidence: low | medium | high
Validation steps: <list>
```

## Discipline

- A chain is only valid if every component has a real, reproducible
  HTTP request — no "theoretically you could".
- If validation reveals a missing piece, surface it explicitly:
  `BLOCKER: need open-redirect on *.example.com — currently only
  found on example-blog.com (different apex).`
