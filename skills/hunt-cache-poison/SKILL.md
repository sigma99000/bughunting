---
name: hunt-cache-poison
description: Web cache poisoning — unkeyed input, key normalization, fat GET, internal cache, CDN-specific quirks.
keywords: [cache poisoning, cdn, varnish, akamai, cloudflare, fastly, unkeyed header, cache key, fat get]
---

# hunt-cache-poison

## Triggers

"cache poisoning", "cdn", "varnish", "akamai", "cloudflare cache",
"fastly", "cache key", "unkeyed".

## Phase 1 — identify cache + key

Sample headers:

```
X-Cache: HIT from cf-edge-iad-12345
Age: 432
CF-Cache-Status: HIT
Via: 1.1 varnish-v4
X-Served-By: cache-bos4670-BOS
```

Cache key is usually: `Host + URL`. **Unkeyed** inputs are anything
else that affects the response:

- `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Scheme`
- `X-Forwarded-For` (when reflected in error pages)
- Specific cookie names (`X-Lang` reflected but not in key)
- Custom headers like `X-Original-URL`, `X-Rewrite-URL`

## Phase 2 — probe for reflection

Send:

```
GET / HTTP/1.1
Host: app.example.com
X-Forwarded-Host: attacker.com
```

Look in response body for `attacker.com` (in `<base>` tag, OG image,
canonical link, JS strings). If found → unkeyed input reflected →
poison candidate.

## Phase 3 — cache it

After confirming reflection:

1. Probe the cache key (the URL the victim would visit, e.g., `/`)
2. Determine the cache TTL (`Age` header growth, `Cache-Control: max-age`)
3. Send the poisoned request to a clean cache region (different
   edge POP)
4. From a clean browser, fetch the URL → see attacker payload

Tool: `param-miner` Burp extension auto-discovers unkeyed headers.

## Phase 4 — fat-GET cache poisoning

Some CDNs only cache by URL but the origin honors a body on GET
(unusual, but observed). Send a request with a body that triggers
different origin behavior:

```
GET /api/config HTTP/1.1
Host: app.example.com
Content-Length: 39

{"override":"https://attacker.com"}
```

If origin merges body params and CDN caches the result → poison.

## Phase 5 — cache key injection

When cache key includes URL but URL parsing differs:

- Path-parameter delimiter `;`:
  `/api/items;poison=x` vs `/api/items?poison=x` — CDN keys without `;`,
  origin reads it
- Encoded slashes: `/api%2fitems` keyed as one path; origin decodes
- Trailing slash sometimes keyed, sometimes not

## Phase 6 — internal cache (Varnish-style)

When app has an internal cache before origin (e.g., Varnish in front
of Django), poisoning the internal cache poisons all downstream users
even if CDN is clean.

## Phase 7 — CDN quirks

| CDN | Quirk |
|---|---|
| Cloudflare | Caches by URL+host; `Vary` header honored; `X-Forwarded-Host` is not in default key |
| Fastly | VCL-driven; check `Vary` and custom CDN rules |
| Akamai | "Cache key modifications" can include headers; depends on customer config |
| AWS CloudFront | Cache policies — only headers listed in policy enter key |
| Varnish | VCL — completely customizable |

## Chain templates

| Component | Reaches |
|---|---|
| Cache poisoning + reflected XSS via unkeyed header | Stored XSS at scale (CDN-wide) |
| Cache poisoning + open redirect | Mass phishing infrastructure |
| Cache poisoning + smuggling (`hunt-smuggling`) | Cross-user response stealing |
| Cache deception (`/profile/me/x.css` proxied to `/profile/me`) | Read victim PII |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #409370 (Twitter) | X-Forwarded-Host reflected in OG → poison home page |
| H1 #893372 | Akamai cache deception via `.jpg` path append |
| H1 #1063571 | Cache poisoning via smuggling |
| PortSwigger research | Web Cache Vulnerability Scanner |

## Never-submit fallbacks

- Local-browser cache "poisoning" — not server-side; KILL
- Cache poisoning of a page nobody visits → DOWNGRADE
- Detecting unkeyed input alone without a cached payload → CHAIN REQUIRED

## See also

- `hunt-smuggling`
- `hunt-xss`
- `hunt-redirect`
